import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from '../../../modules/auth/entities/user.entity';
import { BaseFactory } from './base.factory';
import { HashingService } from '../../../modules/auth/services/hashing.service';

@Injectable()
export class UserFactory extends BaseFactory<User> {
  constructor(
    @InjectRepository(User)
    protected readonly repository: Repository<User>,
    private readonly hashingService: HashingService,
  ) {
    super(repository);
  }

  async make(overrideParams?: Partial<User>): Promise<User> {
    const username = this.faker.internet.userName();
    // Default password is 'password' for all seeded users
    const password = await this.hashingService.hashPassword('password');

    const user = this.repository.create({
      username,
      password,
      ...overrideParams,
    });

    return user;
  }

  async createAdmin(): Promise<User> {
    return this.create({
      username: 'admin',
    });
  }
} 