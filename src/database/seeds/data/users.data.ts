import { User } from '../../../modules/auth/entities/user.entity';

// Define static users for development/testing
export const staticUsers: Partial<User>[] = [
  {
    username: 'admin',
    // Password will be hashed by the UserFactory
  },
  {
    username: 'farmer1',
    // Password will be hashed by the UserFactory
  },
  {
    username: 'farmer2',
    // Password will be hashed by the UserFactory
  },
  {
    username: 'customer1',
    // Password will be hashed by the UserFactory
  },
  {
    username: 'customer2',
    // Password will be hashed by the UserFactory
  },
]; 