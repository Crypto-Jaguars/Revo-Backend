import { Repository } from 'typeorm';
import { faker } from '@faker-js/faker';

export abstract class BaseFactory<T> {
  protected faker = faker;
  
  constructor(protected repository: Repository<T>) {}
  
  /**
   * Create a single entity with the provided data
   */
  abstract make(overrideParams?: Partial<T>): T | Promise<T>;
  
  /**
   * Create and save a single entity to the database
   */
  async create(overrideParams?: Partial<T>): Promise<T> {
    const entity = await this.make(overrideParams);
    return this.repository.save(entity as any);
  }
  
  /**
   * Create multiple entities with the provided data
   */
  async makeMany(count: number, overrideParams?: Partial<T>): Promise<T[]> {
    const entities: T[] = [];
    for (let i = 0; i < count; i++) {
      entities.push(await this.make(overrideParams));
    }
    return entities;
  }
  
  /**
   * Create and save multiple entities to the database
   */
  async createMany(count: number, overrideParams?: Partial<T>): Promise<T[]> {
    const entities = await this.makeMany(count, overrideParams);
    return this.repository.save(entities as any[]);
  }
  
  /**
   * Truncate the repository's table
   */
  async truncate(): Promise<void> {
    await this.repository.clear();
  }
} 