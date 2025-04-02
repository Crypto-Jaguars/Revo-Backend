import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import session from 'express-session';
import * as dotenv from 'dotenv';
import { ValidationPipe } from '@nestjs/common';
import { HttpExceptionFilter } from './filters/http-exception.filter';
import { LoggerService } from './modules/logging/services/logger.service';
import { RedisStore } from 'connect-redis';
import { setupSwagger } from './docs/config/swagger.config';

dotenv.config();

async function bootstrap() {
  const startTime = Date.now();
  console.log('Starting application initialization...');

  const app = await NestFactory.create(AppModule);
  console.log(`NestFactory.create took ${Date.now() - startTime}ms`);

  const redisClient = app.get('REDIS_CLIENT');
  console.log(`Redis client retrieved after ${Date.now() - startTime}ms`);

  const redisStore = new RedisStore({
    client: redisClient,
    prefix: 'revo-session:',
  });

  const sessionSecret = process.env.SESSION_SECRET;
  if (!sessionSecret) {
    throw new Error('SESSION_SECRET is not defined in your environment variables');
  }

  app.use(
    session({
      store: redisStore,
      secret: sessionSecret,
      resave: false,
      saveUninitialized: false,
    }),
  );

  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
    }),
  );

  const logger = app.get(LoggerService);
  logger.setContext('Bootstrap');
  app.useLogger(logger);
  app.useGlobalFilters(new HttpExceptionFilter());

  setupSwagger(app);
  console.log(`Swagger setup completed after ${Date.now() - startTime}ms`);

  const port = process.env.PORT ?? 3000;
  await app.listen(port, '0.0.0.0');
  console.log(`Server listening on port ${port} after ${Date.now() - startTime}ms`);

  logger.info(`Application is running on: http://localhost:${port}`);
  logger.info(`API Documentation is available at: http://localhost:${port}/api/docs`);

  process.on('SIGINT', async () => {
    logger.info('Shutting down application...');
    await app.close();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    logger.info('Shutting down application...');
    await app.close();
    process.exit(0);
  });
}

bootstrap().catch((error) => {
  console.error('Failed to start the application:', error);
  process.exit(1);
});