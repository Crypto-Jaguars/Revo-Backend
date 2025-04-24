import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { OrderItem } from '../../../modules/orders/entities/order-item.entity';
import { BaseFactory } from './base.factory';
import { Order } from '../../../modules/orders/entities/order.entity';
import { Product } from '../../../modules/products/entities/product.entity';

@Injectable()
export class OrderItemFactory extends BaseFactory<OrderItem> {
  constructor(
    @InjectRepository(OrderItem)
    protected readonly repository: Repository<OrderItem>,
    @InjectRepository(Product)
    private readonly productRepository: Repository<Product>,
  ) {
    super(repository);
  }

  async make(overrideParams?: Partial<OrderItem>): Promise<OrderItem> {
    // If no specific product is provided, get a random one from the database
    let product: Product;
    if (overrideParams?.productId) {
      product = await this.productRepository.findOne({ 
        where: { id: overrideParams.productId } 
      });
    } else {
      // Get a random product from the database
      const products = await this.productRepository.find({ take: 10 });
      product = this.faker.helpers.arrayElement(products);
    }

    if (!product) {
      throw new Error('No products found for order item creation');
    }

    // Random quantity between 1 and 10
    const quantity = this.faker.number.int({ min: 1, max: 10 });
    const pricePerUnit = parseFloat(product.price.toString());
    const totalPrice = quantity * pricePerUnit;

    const orderItem = this.repository.create({
      productId: product.id,
      quantity,
      pricePerUnit,
      totalPrice,
      productSnapshot: product,
      ...overrideParams,
    });

    return orderItem;
  }

  async createForOrder(order: Order, count = 1): Promise<OrderItem[]> {
    const items: OrderItem[] = [];
    for (let i = 0; i < count; i++) {
      const item = await this.make({ order });
      items.push(item);
    }
    return this.repository.save(items);
  }
} 