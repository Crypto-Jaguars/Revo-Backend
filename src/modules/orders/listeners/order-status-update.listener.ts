import { Injectable, Logger } from '@nestjs/common';
import { OnEvent } from '@nestjs/event-emitter';
import { OrderStatusUpdatedEvent } from '../events/status-update.event';
import { StatusService } from '../services/status.service';
import { OrderStatus } from '../entities/order.entity';

@Injectable()
export class OrderStatusUpdateListener {
    private readonly logger = new Logger(OrderStatusUpdateListener.name);
    constructor(private readonly statusService: StatusService) {}

  @OnEvent('order.status.updated')
  async handleOrderStatusUpdate(event: OrderStatusUpdatedEvent) {
    this.logger.log(
      `Received event: Order ${event.orderId} status changed from ${event.previousStatus} to ${event.newStatus}`,
    );

      this.sendNotification(event.orderId, event.newStatus);

      try {
          await this.statusService.updateOrderStatus(event.orderId, event.newStatus);
      } catch (error) {
          this.logger.error("Error updating order status:", error);
      }
  }
    // Simulate sending a notification
  private sendNotification(orderId: string, newStatus: OrderStatus) {
    this.logger.log(`Sending notification: Order ${orderId} status updated to ${newStatus}`);
  }
}