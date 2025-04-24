import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { User } from '../../modules/auth/entities/user.entity';
import { Product } from '../../modules/products/entities/product.entity';
import { Order } from '../../modules/orders/entities/order.entity';
import { OrderItem } from '../../modules/orders/entities/order-item.entity';
import { UserFactory } from './factories/user.factory';
import { ProductFactory } from './factories/product.factory';
import { OrderFactory } from './factories/order.factory';
import { OrderItemFactory } from './factories/order-item.factory';
import { UserSeeder } from './runners/user.seeder';
import { ProductSeeder } from './runners/product.seeder';
import { OrderSeeder } from './runners/order.seeder';
import { MainSeeder } from './runners/main.seeder';
import seedConfig from '../config/seed.config';
import databaseConfig from '../../config/database.config';
import { HashingService } from '../../modules/auth/services/hashing.service';
import { join } from 'path';

@Module({
  imports: [
    ConfigModule.forRoot({
      load: [seedConfig, databaseConfig],
      isGlobal: true,
    }),
    TypeOrmModule.forRoot({
      type: 'better-sqlite3',
      database: 'test-database.sqlite',
      entities: [User, Product, Order, OrderItem],
      synchronize: process.env.NODE_ENV === 'development',
      logging: process.env.NODE_ENV !== 'production',
    }),
    TypeOrmModule.forFeature([User, Product, Order, OrderItem]),
  ],
  providers: [
    // Services
    HashingService,
    
    // Factories
    UserFactory,
    ProductFactory,
    OrderFactory,
    OrderItemFactory,
    
    // Seeders
    UserSeeder,
    ProductSeeder,
    OrderSeeder,
    MainSeeder,
  ],
  exports: [MainSeeder],
})
export class SeedModule {} 