import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Order } from '../../../modules/orders/entities/order.entity';
import { OrderFactory } from '../factories/order.factory';
import { OrderItemFactory } from '../factories/order-item.factory';
import { BaseSeeder } from './base.seeder';
import { ConfigService } from '@nestjs/config';
import { User } from '../../../modules/auth/entities/user.entity';

@Injectable()
export class OrderSeeder extends BaseSeeder {
  constructor(
    @InjectRepository(Order)
    private readonly orderRepository: Repository<Order>,
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
    private readonly orderFactory: OrderFactory,
    private readonly orderItemFactory: OrderItemFactory,
    private readonly configService: ConfigService,
  ) {
    super();
  }

  async run(): Promise<void> {
    try {
      this.logProgress('Seeding orders...');

      // Get real user IDs from the database
      const users = await this.userRepository.find();
      if (users.length === 0) {
        throw new Error('No users found in the database. Please run the UserSeeder first.');
      }

      // Create random orders based on config
      const defaultCount = this.configService.get<number>('seed.defaultCount.orders', 20);
      const orders = [];

      for (let i = 0; i < defaultCount; i++) {
        // Select a random user for this order
        const randomUser = users[Math.floor(Math.random() * users.length)];
        
        // Create order with the actual user ID
        const order = await this.orderFactory.create({ userId: randomUser.id });
        orders.push(order);
      }

      // Add order items to each order
      for (const order of orders) {
        // Add between 1 and 5 items to each order
        const itemCount = this.getRandomInt(1, 5);
        await this.orderItemFactory.createForOrder(order, itemCount);
      }

      this.logProgress(`Successfully seeded ${defaultCount} orders`);
    } catch (error) {
      this.logError('Failed to seed orders', error);
      throw error;
    }
  }

  async clean(): Promise<void> {
    try {
      this.logProgress('Cleaning orders...');
      await this.orderRepository.clear();
      this.logProgress('Successfully cleaned orders');
    } catch (error) {
      this.logError('Failed to clean orders', error);
      throw error;
    }
  }

  private getRandomInt(min: number, max: number): number {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }
} 