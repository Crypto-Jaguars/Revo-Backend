/* eslint-disable prettier/prettier */
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { RedisModule } from '@nestjs-modules/ioredis';
import { OrderRepository } from './repositories/order.repository';
import { OrderService } from './services/order.service';
import { OrderController } from './controllers/order.controller';
import { OrderItem } from './entities/order-item.entity';
import { ProductsModule } from '../products/products.module';
import { BullModule } from '@nestjs/bullmq';
import { NotificationService } from './services/notification.services';
import { WebhookController } from './controllers/webhook.controller';
import { NotificationLogListener } from './events/notification-log.listener';
import { Payment } from './entities/payment.entity';
import { StatusService } from './services/status.service';
import { EventEmitterModule } from '@nestjs/event-emitter';
import { OrderStatusUpdateListener } from './listeners/order-status-update.listener';
import { Order } from './entities/order.entity';

@Module({
  imports: [
    TypeOrmModule.forFeature([Order, OrderItem, Payment]),
    ProductsModule,
        // If using local RedisModule, remove this completely
        // If @nestjs-modules/ioredis is required:
        RedisModule.forRoot({
          type: 'single',
          options: {
            host: process.env.REDIS_HOST || 'localhost',
            port: parseInt(process.env.REDIS_PORT || '6379', 10),
          },
        }),
    BullModule.registerQueue({
      name: 'notification',
    }),
    EventEmitterModule.forRoot(),
  ],
  providers: [
    OrderService,
    NotificationService,
    NotificationLogListener,
    StatusService,
    OrderStatusUpdateListener,
    OrderRepository,
  ],
  controllers: [OrderController, WebhookController],
})
export class OrdersModule {}