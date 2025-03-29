import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Product } from '../../modules/products/entities/product.entity';
import { ProductController } from './controllers/product.controller';
import { ProductService } from './services/product.service';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { ProductCache } from './cache/product.cache';

@Module({
  imports: [TypeOrmModule.forFeature([Product]), ConfigModule],
  providers: [ProductService, ConfigService, ProductCache],
  controllers: [ProductController],
  exports: [ProductService],
})
export class ProductsModule {}
