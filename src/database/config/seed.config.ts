import { registerAs } from '@nestjs/config';

export default registerAs('seed', () => ({
  // Environment to determine which seeds to run
  environment: process.env.NODE_ENV || 'development',
  
  // Default number of items to seed if not specified
  defaultCount: {
    users: 10,
    products: 50,
    orders: 20,
  },
  
  // Truncate tables before seeding (be careful in production)
  truncate: process.env.SEED_TRUNCATE === 'true',
  
  // Specific seeding options for different environments
  environments: {
    development: {
      runSeeders: true,
      truncate: true,
    },
    test: {
      runSeeders: true,
      truncate: true,
    },
    production: {
      runSeeders: false,
      truncate: false,
    },
  },
})); 