import { Controller, Post, Headers, Body, Res } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBody } from '@nestjs/swagger'; // Agregamos los decoradores de Swagger
import { notifyDto } from '../dtos/notification.dto';
import { NotificationService } from '../services/notification.services';
import { Queue } from 'bullmq';
import { InjectQueue } from '@nestjs/bullmq';
import { Throttle } from '@nestjs/throttler';

@ApiTags('webhook') 
@Controller('webhook')
export class WebhookController {
  constructor(
    @InjectQueue('notification') private notificationQueue: Queue,
    private readonly notificationService: NotificationService,
  ) {}

  @Throttle({ default: { limit: 5, ttl: 60 } })
  @Post('status-update')
  @ApiOperation({ description: 'Handles status update events from external services.' })
  @ApiBody({ type: notifyDto, description: 'Notification payload for status updates.' })
  @ApiResponse({ status: 200, description: 'Webhook processed successfully.' })
  @ApiResponse({ status: 500, description: 'Internal server error.' })
  async handleStatusUpdate(
    @Body() notifyDto: notifyDto,
    @Res() res,
    @Headers() headers,
  ) {
    try {
      await this.notificationQueue.add('status-update', notifyDto, {
        attempts: 3,
        backoff: 5000, // 5s
      });

      return res.status(200).send({ received: true });
    } catch (error) {
      console.error('Failed to process webhook:', error);

      return res.status(500).send({
        error: 'Failed to process webhook',
        message: process.env.NODE_ENV === 'production' ? undefined : error.message,
      });
    }
  }
}