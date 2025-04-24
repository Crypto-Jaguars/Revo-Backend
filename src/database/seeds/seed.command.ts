import { NestFactory } from '@nestjs/core';
import { Logger } from '@nestjs/common';
import { SeedModule } from './seed.module';
import { MainSeeder } from './runners/main.seeder';
import { ConfigService } from '@nestjs/config';
import * as dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();

async function bootstrap() {
  const logger = new Logger('SeedCommand');
  
  try {
    logger.log('Starting seed process...');
    
    // Create a standalone application context
    const appContext = await NestFactory.createApplicationContext(SeedModule);
    
    // Get the main seeder and config service
    const seeder = appContext.get(MainSeeder);
    const configService = appContext.get(ConfigService);
    
    // Parse command-line arguments
    const args = process.argv.slice(2);
    const clean = args.includes('--clean');
    const env = args.find(arg => arg.startsWith('--env='))?.split('=')[1];
    
    // Set environment if provided
    if (env) {
      process.env.NODE_ENV = env;
      logger.log(`Setting environment to: ${env}`);
    }
    
    // Log the environment
    const currentEnv = configService.get<string>('seed.environment', 'development');
    logger.log(`Running seeds for environment: ${currentEnv}`);
    
    // Run the seeder
    await seeder.run({ clean });
    
    // Close the application context
    await appContext.close();
    logger.log('Seed process completed successfully!');
    process.exit(0);
  } catch (error) {
    logger.error('Seed process failed', error?.stack);
    process.exit(1);
  }
}

bootstrap(); 