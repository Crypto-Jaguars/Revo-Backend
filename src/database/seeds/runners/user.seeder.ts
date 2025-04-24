import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from '../../../modules/auth/entities/user.entity';
import { UserFactory } from '../factories/user.factory';
import { BaseSeeder } from './base.seeder';
import { ConfigService } from '@nestjs/config';
import { staticUsers } from '../data/users.data';

@Injectable()
export class UserSeeder extends BaseSeeder {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
    private readonly userFactory: UserFactory,
    private readonly configService: ConfigService,
  ) {
    super();
  }

  async run(): Promise<void> {
    try {
      this.logProgress('Seeding users...');

      // Create predefined users
      for (const userData of staticUsers) {
        await this.userFactory.create(userData);
      }

      // Create random users based on config
      const defaultCount = this.configService.get<number>('seed.defaultCount.users', 10);
      await this.userFactory.createMany(defaultCount);

      this.logProgress(`Successfully seeded ${defaultCount + staticUsers.length} users`);
    } catch (error) {
      this.logError('Failed to seed users', error);
      throw error;
    }
  }

  async clean(): Promise<void> {
    try {
      this.logProgress('Cleaning users...');
      await this.userRepository.clear();
      this.logProgress('Successfully cleaned users');
    } catch (error) {
      this.logError('Failed to clean users', error);
      throw error;
    }
  }
} 