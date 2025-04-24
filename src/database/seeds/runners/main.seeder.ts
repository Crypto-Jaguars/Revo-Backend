import { Injectable, Logger } from '@nestjs/common';
import { UserSeeder } from './user.seeder';
import { ProductSeeder } from './product.seeder';
import { OrderSeeder } from './order.seeder';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class MainSeeder {
  private readonly logger = new Logger(MainSeeder.name);

  constructor(
    private readonly userSeeder: UserSeeder,
    private readonly productSeeder: ProductSeeder,
    private readonly orderSeeder: OrderSeeder,
    private readonly configService: ConfigService,
  ) {}

  async run(options?: { clean?: boolean }): Promise<void> {
    try {
      this.logger.log('Starting seeding...');
      
      const currentEnv = this.configService.get<string>('seed.environment', 'development');
      const envConfig = this.configService.get(`seed.environments.${currentEnv}`, {});
      const shouldRun = envConfig.runSeeders !== false;
      const shouldClean = options?.clean ?? envConfig.truncate ?? false;
      
      if (!shouldRun) {
        this.logger.log(`Seeding is disabled for environment: ${currentEnv}`);
        return;
      }

      // Clean data if specified
      if (shouldClean) {
        this.logger.log('Cleaning existing data...');
        // Clean in reverse order to avoid foreign key constraints
        await this.orderSeeder.clean();
        await this.productSeeder.clean();
        await this.userSeeder.clean();
      }

      // Run seeders in order based on dependencies
      await this.userSeeder.run();
      await this.productSeeder.run();
      await this.orderSeeder.run();

      this.logger.log('Seeding completed successfully!');
    } catch (error) {
      this.logger.error('Seeding failed', error?.stack);
      throw error;
    }
  }
} 