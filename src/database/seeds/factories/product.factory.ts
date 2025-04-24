import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Product } from '../../../modules/products/entities/product.entity';
import { BaseFactory } from './base.factory';

@Injectable()
export class ProductFactory extends BaseFactory<Product> {
  private readonly units = ['kg', 'g', 'lb', 'oz', 'each', 'bunch', 'box'];

  constructor(
    @InjectRepository(Product)
    protected readonly repository: Repository<Product>,
  ) {
    super(repository);
  }

  async make(overrideParams?: Partial<Product>): Promise<Product> {
    const name = this.faker.commerce.productName();
    const description = this.faker.commerce.productDescription();
    const price = parseFloat(this.faker.commerce.price({ min: 1, max: 100 }));
    const unit = this.faker.helpers.arrayElement(this.units);
    const stockQuantity = this.faker.number.int({ min: 0, max: 1000 });
    const imagesCount = this.faker.number.int({ min: 1, max: 5 });
    const images = Array(imagesCount)
      .fill(null)
      .map(() => this.faker.image.url());
    
    // Generate a random harvest date within the last 30 days
    const harvestDate = this.faker.date.recent({ days: 30 });

    const product = this.repository.create({
      name,
      description,
      price,
      unit,
      stockQuantity,
      harvestDate,
      images,
      ...overrideParams,
    });

    return product;
  }
} 