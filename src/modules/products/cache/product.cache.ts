import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Inject, Injectable } from '@nestjs/common';
import { Cache } from 'cache-manager';
import { Product } from '../entities/product.entity';
import { cachedKeys } from '../constants/cache.constant';

@Injectable()
export class ProductCache {
  constructor(@Inject(CACHE_MANAGER) private cacheManager: Cache) {}

  async cacheSingleProduct(key: string, value: Product, ttl: number) {
    await this.cacheManager.set(key, value, ttl);
  }

  async cacheAllProducts(value: Product[], ttl: number) {
    await this.cacheManager.set(cachedKeys.ALL_PRODUCTS, value, ttl);
  }

  async getSingleProductFromCache(key: string): Promise<Product> {
    return await this.cacheManager.get(key);
  }

  async getAllProductsFromCache(): Promise<Product[]> {
    return await this.cacheManager.get(cachedKeys.ALL_PRODUCTS);
  }

  async invalidateSingleProduct(key: string): Promise<boolean> {
    return await this.cacheManager.del(key);
  }

  async InvalidateAll(): Promise<boolean> {
    return await this.cacheManager.del(cachedKeys.ALL_PRODUCTS);
  }
}
