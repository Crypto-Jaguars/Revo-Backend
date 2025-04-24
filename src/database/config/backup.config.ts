/* eslint-disable prettier/prettier */
import { registerAs } from '@nestjs/config';
import * as path from 'path';

export interface BackupConfig {
  backupDir: string;
  retentionDays: number;
  schedule: string;
  compressionLevel: number;
  enableNotifications: boolean;
  notificationEmail?: string;
  maxConcurrentBackups: number;
  validateBackups: boolean;
  backupPrefix: string;
}

const defaultConfig: BackupConfig = {
  backupDir: path.join(process.cwd(), 'backups'),
  retentionDays: 30,
  schedule: '0 2 * * *', // Every day at 2 AM
  compressionLevel: 9,
  enableNotifications: false,
  maxConcurrentBackups: 1,
  validateBackups: true,
  backupPrefix: 'revo-db-backup',
};

export default registerAs('backup', (): BackupConfig => {
  return {
    ...defaultConfig,
    backupDir: process.env.BACKUP_DIR || defaultConfig.backupDir,
    retentionDays:
      parseInt(process.env.BACKUP_RETENTION_DAYS, 10) ||
      defaultConfig.retentionDays,
    schedule: process.env.BACKUP_SCHEDULE || defaultConfig.schedule,
    compressionLevel:
      parseInt(process.env.BACKUP_COMPRESSION_LEVEL, 10) ||
      defaultConfig.compressionLevel,
    enableNotifications: process.env.BACKUP_ENABLE_NOTIFICATIONS === 'true',
    notificationEmail: process.env.BACKUP_NOTIFICATION_EMAIL,
    maxConcurrentBackups:
      parseInt(process.env.BACKUP_MAX_CONCURRENT, 10) ||
      defaultConfig.maxConcurrentBackups,
    validateBackups: process.env.BACKUP_VALIDATE !== 'false',
    backupPrefix: process.env.BACKUP_PREFIX || defaultConfig.backupPrefix,
  };
});
