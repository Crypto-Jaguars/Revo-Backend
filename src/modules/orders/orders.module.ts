/* eslint-disable prettier/prettier */
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { OrderRepository } from './repositories/order.repository';
import { OrderService } from './services/order.service';
import { OrderController } from './controllers/order.controller';
import { OrderItem } from './entities/order-item.entity';
import { ProductsModule } from '../products/products.module';
import { BullModule } from '@nestjs/bullmq';
import { NotificationService } from './services/notification.services';
import { WebhookController} from './controllers/webhook.controller';
import { NotificationLogListener } from './events/notification-log.listener';
import { Payment } from './entities/payment.entity';
import { StatusService } from './services/status.service';
import { EventEmitterModule } from '@nestjs/event-emitter';
import { OrderStatusUpdateListener } from './listeners/order-status-update.listener';

@Module({
  imports: [TypeOrmModule.forFeature([OrderRepository, OrderItem, Payment]), ProductsModule,  BullModule.registerQueue(
    {
      name:'notification'
    }
  )],
  providers: [OrderService, NotificationService, NotificationLogListener],
  controllers: [OrderController, WebhookController],
})


export class OrdersModule {}