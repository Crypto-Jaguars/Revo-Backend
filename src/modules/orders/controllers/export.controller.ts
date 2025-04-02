import {
  Controller,
  Get,
  Logger,
  InternalServerErrorException,
  UseGuards,
} from '@nestjs/common';
import { InjectQueue } from '@nestjs/bullmq';
import { Queue } from 'bullmq';
import { OrderService } from '../services/order.service';
import { JwtAuthGuard } from './../../../modules/auth/guards/jwt-auth.guard';
@Controller('orders/export')
export class ExportController {
  private readonly logger = new Logger(ExportController.name);

  constructor(
    @InjectQueue('exportQueue') private readonly exportQueue: Queue,
    private readonly orderService: OrderService,
  ) {}

  @UseGuards(JwtAuthGuard)
  @Get()
  async exportOrders() {
    try {
      const orders = await this.orderService.findAll();
      await this.exportQueue.add(
        'export-job',
        { orders, filename: `sales-report-${Date.now()}` },
        {
          priority: 1,
          attempts: 3,
        },
      );
      this.logger.log(`Export job queued with ${orders.length} orders`);
      return { message: 'Export is being processed in the background.' };
    } catch (error) {
      this.logger.error(
        `Failed to queue export job: ${error.message}`,
        error.stack,
      );
      throw new InternalServerErrorException(
        'Failed to process export request',
      );
    }
  }
}
