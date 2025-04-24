/* eslint-disable prettier/prettier */
import { Injectable } from '@nestjs/common';
import { InjectRedis } from '@nestjs-modules/ioredis';
import Redis from 'ioredis';

@Injectable()
export class CacheService {
  redisService: any;
  set: any;
  get: any;
  constructor(@InjectRedis() private readonly redis: Redis) {}

  async setCache(key: string, value: any, ttl: number = 3600) {
    await this.redis.set(key, JSON.stringify(value), 'EX', ttl);
  }

  async getCache(key: string) {
    try {
      const data = await this.redis.get(key);
      if (!data) return null;
      return JSON.parse(data);
    } catch (error) {
      console.error(`Error retrieving cache for key ${key}:`, error);
      return null;
    }
  }
}
