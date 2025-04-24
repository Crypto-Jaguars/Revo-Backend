import { Injectable, BadRequestException, Inject, NotFoundException, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Order, OrderStatus } from '../entities/order.entity';
import { OrderService } from './order.service';
import { StatusEntry } from '../entities/status.entity';

@Injectable()
export class StatusService {
  private readonly logger = new Logger(StatusService.name);

  constructor(
    @InjectRepository(Order)
    private ordersRepository: Repository<Order>,
    private readonly orderService: OrderService,
  ) {}

  async updateOrderStatus(orderId: string, newStatus: OrderStatus): Promise<void> {
    const order = await this.orderService.findOne(orderId);
    if (!order) {
      const msg = `Order with ID ${orderId} not found`;
      this.logger.error(msg);
      throw new NotFoundException(msg);
    }
    const previousStatus = order.status;

    if (!this.isValidTransition(previousStatus, newStatus)) {
      const msg = `Invalid status transition: ${previousStatus} -> ${newStatus}`;
      this.logger.error(msg);
      throw new BadRequestException(msg);
    }

    this.logger.log(`Updating order ${orderId} status: ${previousStatus} -> ${newStatus}`);

    order.status = newStatus;
    if (!order.statusHistory) {
      order.statusHistory = [];
    }
    order.statusHistory.push({ status: newStatus, timestamp: new Date() });

    await this.ordersRepository.save(order);
    this.logger.log(`Order ${orderId} status updated successfully to ${newStatus}`);
  }
    async getOrderStatusHistory(orderId: string): Promise<StatusEntry[]> {
      const order = await this.orderService.findOne(orderId);
        if (!order) {
          const msg =  `Order ${orderId} Not Found`;
          this.logger.error(msg);
          throw new NotFoundException(msg)
        }

        return order.statusHistory || [];

    }

  private isValidTransition(
    currentStatus: OrderStatus,
    newStatus: OrderStatus,
  ): boolean {
    const allowedTransitions = {
      [OrderStatus.PENDING]: [OrderStatus.COMPLETED, OrderStatus.CANCELED],
      [OrderStatus.COMPLETED]: [],
      [OrderStatus.CANCELED]: [],
    };
    return allowedTransitions[currentStatus]?.includes(newStatus) ?? false;
  }
}