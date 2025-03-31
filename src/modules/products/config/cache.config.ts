import { CacheModuleAsyncOptions } from '@nestjs/cache-manager';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { redisStore } from 'cache-manager-redis-store';

export const RedisOptions: CacheModuleAsyncOptions = {
  isGlobal: true,
  imports: [ConfigModule],
  useFactory: async (configService: ConfigService) => {
    const store = await redisStore({
      socket: {
-        host: configService.get<string>('REDIS_HOST'),
-        port: parseInt(configService.get<string>('REDIS_PORT')),
+        host: configService.get<string>('REDIS_HOST') || 'localhost',
+        port: parseInt(configService.get<string>('REDIS_PORT') || '6379'),
      },
    });
    console.log('the store is this', store);

    return {
      store: () => store,
    };
  },
  inject: [ConfigService],
};
