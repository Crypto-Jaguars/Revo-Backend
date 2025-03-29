import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Product } from '../../modules/products/entities/product.entity';
import { ProductController } from './controllers/product.controller';
import { ProductService } from './services/product.service';
import { MediaController } from './controllers/media.controller';
import { MediaService } from './services/media.service';
import { ProductImage } from './entities/media.entity';
import { Category } from './entities/category.entity';
import { CategoryService } from './services/category.service';
import { CategoryController } from './controllers/category.controller';

@Module({
  imports: [TypeOrmModule.forFeature([Product, ProductImage, Category])],
  providers: [ProductService, MediaService, CategoryService],
  controllers: [ProductController, MediaController, CategoryController],
  exports: [ProductService, MediaService, CategoryService],
})
export class ProductsModule {}