import { Processor, Process } from '@nestjs/bull';
import { NotificationService } from '../services/notification.services';
import { notifyDto } from '../dtos/notification.dto';
import { Job } from 'bull'

@Processor('notification')
export class NotificationProcessor{
  constructor(private notificationService: NotificationService) {
    
  }

  @Process('status-update')
  async notificationProcessor(job: Job<notifyDto>): Promise<any> {
    const data = job.data as notifyDto;
    const { email, phone, orderId, status } = data;

    try {
      await this.notificationService.sendStatusUpdateNotification({ email, phone, orderId, status });
      return { success: true };
    } catch (error) {
      console.error('[NotificationProcessor] Job failed:', error.message);
      throw error;
    }
  }
}
