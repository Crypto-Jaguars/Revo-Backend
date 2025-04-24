import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Product } from '../../../modules/products/entities/product.entity';
import { ProductFactory } from '../factories/product.factory';
import { BaseSeeder } from './base.seeder';
import { ConfigService } from '@nestjs/config';
import { staticProducts } from '../data/products.data';

@Injectable()
export class ProductSeeder extends BaseSeeder {
  constructor(
    @InjectRepository(Product)
    private readonly productRepository: Repository<Product>,
    private readonly productFactory: ProductFactory,
    private readonly configService: ConfigService,
  ) {
    super();
  }

  async run(): Promise<void> {
    try {
      this.logProgress('Seeding products...');

      // Create predefined products
      for (const productData of staticProducts) {
        await this.productFactory.create(productData);
      }

      // Create random products based on config
      const defaultCount = this.configService.get<number>('seed.defaultCount.products', 50);
      await this.productFactory.createMany(defaultCount);

      this.logProgress(`Successfully seeded ${defaultCount + staticProducts.length} products`);
    } catch (error) {
      this.logError('Failed to seed products', error);
      throw error;
    }
  }

  async clean(): Promise<void> {
    try {
      this.logProgress('Cleaning products...');
      await this.productRepository.clear();
      this.logProgress('Successfully cleaned products');
    } catch (error) {
      this.logError('Failed to clean products', error);
      throw error;
    }
  }
} 