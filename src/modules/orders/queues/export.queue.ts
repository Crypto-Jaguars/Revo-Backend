/* eslint-disable prettier/prettier */
import { Process, Processor } from '@nestjs/bull';
import { Job } from 'bull';
import { ExportService } from './../services/export.service';

@Processor('exportQueue')
export class ExportQueue {
  constructor(private readonly exportService: ExportService) {}

  @Process()
  @Process('export')
  async handleExport(job: Job) {
    try {
      await this.exportService.streamExportToCSV(job.data.orders, job.data.filename);
      return { success: true, filename: job.data.filename };
    } catch (error) {
      console.error(`Export job failed: ${error.message}`);
      throw error;
    }
  }
}
