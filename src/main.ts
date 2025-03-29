import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import session from 'express-session';
import * as dotenv from 'dotenv';
import { ValidationPipe } from '@nestjs/common';
import { HttpExceptionFilter } from './filters/http-exception.filter';
import { LoggerService } from './modules/logging/services/logger.service';
import { createClient } from 'redis';
import { RedisStore } from 'connect-redis';

dotenv.config();

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Create the Redis client in legacy mode for compatibility
  const redisClient = createClient({
    legacyMode: true,
    url:
      process.env.REDIS_URL ||
      `redis://${process.env.REDIS_HOST || 'localhost'}:${process.env.REDIS_PORT || 6379}`,
    password: process.env.REDIS_PASSWORD,
  });
  redisClient.on('error', (err) => console.error('Redis Client Error', err));
  await redisClient.connect().catch(console.error);

  // Initialize the RedisStore using the ESM import syntax
  const redisStore = new RedisStore({ client: redisClient });

  // Configure session middleware with the Redis-backed store
  const sessionSecret = process.env.SESSION_SECRET;
  if (!sessionSecret) {
    throw new Error(
      'SESSION_SECRET is not defined in your environment variables',
    );
  }
  app.use(
    session({
      store: redisStore,
      secret: sessionSecret,
      resave: false,
      saveUninitialized: false,
    }),
  );

  // Set up global validation pipe and exception filter
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      exceptionFactory: (error) => {
        console.log('validation error is this', error);
      },
    }),
  );

  const logger = app.get(LoggerService);
  logger.setContext('Bootstrap');
  app.useLogger(logger);
  app.useGlobalFilters(new HttpExceptionFilter());

  await app.listen(process.env.PORT ?? 3000);

  logger.info(
    `Application is running on: http://localhost:${process.env.PORT}`,
  );
}

bootstrap();
