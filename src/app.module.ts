import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import databaseConfig from './config/database.config';
import { LoggingModule } from './modules/logging/logging.module';
import { APP_INTERCEPTOR } from '@nestjs/core';
import { LoggingInterceptor } from './modules/logging/interceptors/logging.interceptor';
import { ProductsModule } from './modules/products/products.module';
import { OrdersModule } from './modules/orders/orders.module';
import { CacheModule } from '@nestjs/cache-manager';
import { RedisOptions } from './modules/products/config/cache.config';
import { AuthModule } from './modules/auth/auth.module';
import { MetricsModule } from './modules/metrics/metrics.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      load: [databaseConfig],
    }),
    TypeOrmModule.forRootAsync({
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => ({
        ...configService.get('database'),
      }),
    }),
    LoggingModule,
    CacheModule.registerAsync(RedisOptions),
    ProductsModule,
    AuthModule,
    MetricsModule,
  ],
  providers: [
    {
      provide: APP_INTERCEPTOR,
      useClass: LoggingInterceptor,
    },
    ProductsModule,
    OrdersModule,
    AuthModule,
  ],
})
export class AppModule {}
