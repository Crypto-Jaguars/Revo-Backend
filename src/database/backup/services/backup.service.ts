/* eslint-disable prettier/prettier */
import { Injectable, OnModuleInit } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { SchedulerRegistry } from '@nestjs/schedule';
import { CronJob } from 'cron';
import * as fs from 'fs';
import * as path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';
import { BackupConfig } from '../../config/backup.config';
import { LoggerService } from '../../../modules/logging/services/logger.service';

const execAsync = promisify(exec);

@Injectable()
export class BackupService implements OnModuleInit {
  private readonly backupConfig: BackupConfig;
  private isBackupRunning = false;
  // Change the type of backupQueue to match the executeBackup function's return type
  private backupQueue: (() => Promise<string>)[] = [];

  constructor(
    private readonly configService: ConfigService,
    private readonly schedulerRegistry: SchedulerRegistry,
    private readonly logger: LoggerService,
  ) {
    this.logger.setContext('BackupService');
    this.backupConfig = this.configService.get<BackupConfig>('backup');
    this.ensureBackupDirExists();
  }

  onModuleInit() {
    this.setupBackupSchedule();
  }

  private ensureBackupDirExists() {
    if (!fs.existsSync(this.backupConfig.backupDir)) {
      this.logger.info(
        `Creating backup directory: ${this.backupConfig.backupDir}`,
      );
      fs.mkdirSync(this.backupConfig.backupDir, { recursive: true });
    }
  }

  private setupBackupSchedule() {
    const job = new CronJob(this.backupConfig.schedule, () => {
      this.logger.info('Scheduled backup starting');
      this.createBackup()
        .then(() => this.logger.info('Scheduled backup completed successfully'))
        .catch((error) =>
          this.logger.error(
            'Scheduled backup failed',
            'BackupService',
            error.stack,
          ),
        );
    });

    this.schedulerRegistry.addCronJob('database-backup', job);
    job.start();
    this.logger.info(`Backup schedule set: ${this.backupConfig.schedule}`);
  }

  async createBackup(
    options: { manual?: boolean; label?: string } = {},
  ): Promise<string> {
    const queuedBackup = new Promise<string>((resolve, reject) => {
      const executeBackup = async () => {
        if (this.isBackupRunning) {
          this.logger.warn('A backup is already running, queuing this request');
          this.backupQueue.push(executeBackup);
          return;
        }

        this.isBackupRunning = true;
        try {
          const backupPath = await this.executeBackup(options);
          resolve(backupPath);
          return backupPath;
        } catch (error) {
          this.logger.error('Backup failed', 'BackupService', error.stack);
          reject(error);
          throw error;
        } finally {
          this.isBackupRunning = false;
          if (this.backupQueue.length > 0) {
            const nextBackup = this.backupQueue.shift();
            nextBackup();
          }
        }
      };

      executeBackup();
    });

    return queuedBackup;
  }

  private async executeBackup(
    options: { manual?: boolean; label?: string } = {},
  ): Promise<string> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const label = options.label ? `-${options.label}` : '';
    const backupType = options.manual ? 'manual' : 'scheduled';
    const filename = `${this.backupConfig.backupPrefix}-${backupType}${label}-${timestamp}.sql.gz`;
    const backupPath = path.join(this.backupConfig.backupDir, filename);

    this.logger.info(`Starting database backup to ${backupPath}`);

    const dbConfig = this.configService.get('database');
    const command = `pg_dump -h ${dbConfig.host} -p ${dbConfig.port} -U ${dbConfig.username} -d ${dbConfig.database} | gzip -${this.backupConfig.compressionLevel} > "${backupPath}"`;

    try {
      // Set PGPASSWORD environment variable for the command
      const env = { ...process.env, PGPASSWORD: dbConfig.password };
      await execAsync(command, { env });

      if (this.backupConfig.validateBackups) {
        await this.validateBackup(backupPath);
      }

      this.logger.info(`Backup completed successfully: ${backupPath}`);
      await this.performBackupRetention();
      return backupPath;
    } catch (error) {
      this.logger.error(
        `Backup failed: ${error.message}`,
        'BackupService',
        error.stack,
      );
      // Clean up failed backup file if it exists
      if (fs.existsSync(backupPath)) {
        fs.unlinkSync(backupPath);
      }
      throw error;
    }
  }

  private async validateBackup(backupPath: string): Promise<boolean> {
    this.logger.info(`Validating backup: ${backupPath}`);

    // Check if file exists and has content
    if (!fs.existsSync(backupPath)) {
      throw new Error(`Backup file does not exist: ${backupPath}`);
    }

    const stats = fs.statSync(backupPath);
    if (stats.size === 0) {
      throw new Error(`Backup file is empty: ${backupPath}`);
    }

    // Test the integrity of the gzip file
    const command = `gzip -t "${backupPath}"`;
    try {
      await execAsync(command);
      this.logger.info(`Backup validation successful: ${backupPath}`);
      return true;
    } catch (error) {
      this.logger.error(
        `Backup validation failed: ${error.message}`,
        'BackupService',
        error.stack,
      );
      throw new Error(`Backup validation failed: ${error.message}`);
    }
  }

  async restoreBackup(backupPath: string): Promise<void> {
    if (!fs.existsSync(backupPath)) {
      throw new Error(`Backup file does not exist: ${backupPath}`);
    }

    this.logger.info(`Starting database restoration from ${backupPath}`);

    const dbConfig = this.configService.get('database');
    const command = `gunzip -c "${backupPath}" | psql -h ${dbConfig.host} -p ${dbConfig.port} -U ${dbConfig.username} -d ${dbConfig.database}`;

    try {
      // Set PGPASSWORD environment variable for the command
      const env = { ...process.env, PGPASSWORD: dbConfig.password };
      await execAsync(command, { env });
      this.logger.info(
        `Database restoration completed successfully from ${backupPath}`,
      );
    } catch (error) {
      this.logger.error(
        `Database restoration failed: ${error.message}`,
        'BackupService',
        error.stack,
      );
      throw error;
    }
  }

  async listBackups(): Promise<
    { filename: string; path: string; size: number; date: Date }[]
  > {
    this.ensureBackupDirExists();

    const files = fs.readdirSync(this.backupConfig.backupDir);
    const backupFiles = files
      .filter(
        (file) =>
          file.startsWith(this.backupConfig.backupPrefix) &&
          file.endsWith('.sql.gz'),
      )
      .map((filename) => {
        const filePath = path.join(this.backupConfig.backupDir, filename);
        const stats = fs.statSync(filePath);
        return {
          filename,
          path: filePath,
          size: stats.size,
          date: stats.mtime,
        };
      })
      .sort((a, b) => b.date.getTime() - a.date.getTime()); // Sort by date, newest first

    return backupFiles;
  }

  private async performBackupRetention(): Promise<void> {
    const backups = await this.listBackups();
    const now = new Date();

    for (const backup of backups) {
      const ageInDays =
        (now.getTime() - backup.date.getTime()) / (1000 * 60 * 60 * 24);

      if (ageInDays > this.backupConfig.retentionDays) {
        this.logger.info(
          `Removing old backup: ${backup.path} (${ageInDays.toFixed(1)} days old)`,
        );
        fs.unlinkSync(backup.path);
      }
    }
  }

  async getBackupStatus(): Promise<{
    totalBackups: number;
    oldestBackup: Date | null;
    newestBackup: Date | null;
    totalSize: number;
    backupDirSize: number;
    backupDirPath: string;
  }> {
    const backups = await this.listBackups();

    return {
      totalBackups: backups.length,
      oldestBackup:
        backups.length > 0 ? backups[backups.length - 1].date : null,
      newestBackup: backups.length > 0 ? backups[0].date : null,
      totalSize: backups.reduce((sum, backup) => sum + backup.size, 0),
      backupDirSize: this.getDirSize(this.backupConfig.backupDir),
      backupDirPath: this.backupConfig.backupDir,
    };
  }

  private getDirSize(dirPath: string): number {
    let size = 0;
    const files = fs.readdirSync(dirPath);

    for (const file of files) {
      const filePath = path.join(dirPath, file);
      const stats = fs.statSync(filePath);

      if (stats.isDirectory()) {
        size += this.getDirSize(filePath);
      } else {
        size += stats.size;
      }
    }

    return size;
  }
}
