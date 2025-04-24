# Database Seeding System

This directory contains the database seeding system for development and testing environments.

## Structure

```
src/database/
├── seeds/
│   ├── factories/        # Entity factory classes
│   ├── data/             # Static seed data
│   ├── runners/          # Seeder runner classes
│   └── seed.module.ts    # Seeder module
├── config/
│   └── seed.config.ts    # Seeding configuration
```

## Factories

Factories are responsible for creating entities with realistic data. Each entity has its own factory class that extends `BaseFactory`.

Available factories:
- `UserFactory`: Creates user entities with generated usernames and hashed passwords
- `ProductFactory`: Creates product entities with generated names, prices, and other attributes
- `OrderFactory`: Creates order entities with random data
- `OrderItemFactory`: Creates order item entities linked to orders and products

## Data

The `data` directory contains predefined data sets that are used for seeding. These are useful for creating consistent test data.

Available data sets:
- `users.data.ts`: Contains predefined users (admin, farmers, customers)
- `products.data.ts`: Contains predefined products with realistic attributes

## Runners

Seeders are responsible for running the factories and creating the entities. Each entity has its own seeder class that extends `BaseSeeder`.

Available seeders:
- `UserSeeder`: Seeds users
- `ProductSeeder`: Seeds products
- `OrderSeeder`: Seeds orders and order items
- `MainSeeder`: Orchestrates all seeders with proper dependencies

## Usage

### Available Commands

```bash
# Run the seeder with default options
npm run seed

# Run the seeder and truncate tables first
npm run seed:clean

# Run the seeder for development environment
npm run seed:dev

# Run the seeder for test environment (includes cleaning)
npm run seed:test
```

### Command Line Options

- `--clean`: Truncate tables before seeding
- `--env=<environment>`: Set the environment (development, test, production)

### Environment Variables

- `NODE_ENV`: Environment (development, test, production)
- `SEED_TRUNCATE`: Whether to truncate tables before seeding (true/false)

## Adding a New Seeder

1. Create a factory in `factories/` for your entity
2. Add predefined data in `data/` if needed
3. Create a seeder in `runners/` that uses your factory
4. Add your seeder to `MainSeeder` in the proper dependency order
5. Register your factory and seeder in `seed.module.ts`

## Best Practices

1. Always use factory methods to create entities
2. Maintain proper dependency order in seeders
3. Use realistic data for better testing
4. Be careful with truncating tables in production
5. Make sure foreign key constraints are respected when truncating tables 