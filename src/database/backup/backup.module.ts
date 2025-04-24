/* eslint-disable prettier/prettier */
import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { ScheduleModule } from '@nestjs/schedule';
import { BackupService } from './services/backup.service';
import backupConfig from '../config/backup.config';
import { LoggingModule } from '../../modules/logging/logging.module';

@Module({
  imports: [
    ConfigModule.forFeature(backupConfig),
    ScheduleModule.forRoot(),
    LoggingModule,
  ],
  providers: [BackupService],
  exports: [BackupService],
})
export class BackupModule {}
