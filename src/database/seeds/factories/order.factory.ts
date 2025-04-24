import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Order, OrderStatus } from '../../../modules/orders/entities/order.entity';
import { BaseFactory } from './base.factory';

@Injectable()
export class OrderFactory extends BaseFactory<Order> {
  constructor(
    @InjectRepository(Order)
    protected readonly repository: Repository<Order>,
  ) {
    super(repository);
  }

  async make(overrideParams?: Partial<Order>): Promise<Order> {
    // Generate a random Stellar transaction hash (for demonstration purposes)
    const stellarTransactionHash = this.faker.string.alphanumeric(64).toLowerCase();
    
    // Generate a random Stellar public key (for demonstration purposes)
    const stellarPublicKey = `G${this.faker.string.alphanumeric(55)}`;
    
    // Set payment deadline to some time in the next 24 hours
    const paymentDeadline = this.faker.date.soon({ days: 1 });
    
    // Random metadata
    const metadata = {
      customerNote: this.faker.lorem.sentence(),
      deliveryPreference: this.faker.helpers.arrayElement(['morning', 'afternoon', 'evening']),
    };
    
    // Random status with higher probability for completed orders
    const status = this.faker.helpers.weightedArrayElement([
      { weight: 3, value: OrderStatus.COMPLETED },
      { weight: 2, value: OrderStatus.PENDING },
      { weight: 1, value: OrderStatus.CANCELED },
    ]);
    
    // Random total amount between $10 and $500
    const totalAmount = parseFloat(this.faker.commerce.price({ min: 10, max: 500 }));

    const order = this.repository.create({
      // Don't set userId here - it will be provided in overrideParams
      totalAmount,
      status,
      stellarTransactionHash,
      stellarPublicKey,
      paymentDeadline,
      metadata,
      items: [], // Will be filled by OrderItemFactory
      ...overrideParams,
    });

    return order;
  }
} 