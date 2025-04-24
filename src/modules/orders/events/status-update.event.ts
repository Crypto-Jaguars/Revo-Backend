import { OrderStatus, Order } from '../entities/order.entity';

export class OrderStatusUpdatedEvent {
  constructor(
    public readonly orderId: string,
    public readonly previousStatus: OrderStatus | null,
    public readonly newStatus: OrderStatus,
  ) {}
}