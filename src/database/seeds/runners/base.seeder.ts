import { Logger } from '@nestjs/common';

export abstract class BaseSeeder {
  protected readonly logger = new Logger(this.constructor.name);

  /**
   * Run the seeder
   */
  abstract run(): Promise<void>;

  /**
   * Clear the data before seeding
   */
  abstract clean(): Promise<void>;

  /**
   * Log the seeding progress
   */
  protected logProgress(message: string): void {
    this.logger.log(message);
  }

  /**
   * Log the seeding error
   */
  protected logError(message: string, error?: Error): void {
    this.logger.error(message, error?.stack);
  }
} 