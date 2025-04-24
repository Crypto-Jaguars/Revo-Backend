import { Product } from '../../../modules/products/entities/product.entity';

// Define specific products that should always be seeded
export const staticProducts: Partial<Product>[] = [
  {
    name: 'Organic Apples',
    description: 'Fresh organic apples grown without pesticides.',
    price: 2.99,
    unit: 'kg',
    stockQuantity: 100,
    images: ['https://example.com/images/apples.jpg'],
    harvestDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // 7 days ago
  },
  {
    name: 'Fresh Tomatoes',
    description: 'Vine-ripened tomatoes harvested at peak ripeness.',
    price: 3.49,
    unit: 'kg',
    stockQuantity: 75,
    images: ['https://example.com/images/tomatoes.jpg'],
    harvestDate: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000), // 3 days ago
  },
  {
    name: 'Local Honey',
    description: 'Pure, raw honey from local beekeepers.',
    price: 8.99,
    unit: 'jar',
    stockQuantity: 50,
    images: ['https://example.com/images/honey.jpg'],
    harvestDate: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000), // 14 days ago
  },
  {
    name: 'Organic Carrots',
    description: 'Fresh organic carrots with tops.',
    price: 2.49,
    unit: 'bunch',
    stockQuantity: 120,
    images: ['https://example.com/images/carrots.jpg'],
    harvestDate: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000), // 5 days ago
  },
  {
    name: 'Grass-Fed Beef',
    description: 'Local grass-fed beef, humanely raised.',
    price: 15.99,
    unit: 'kg',
    stockQuantity: 30,
    images: ['https://example.com/images/beef.jpg'],
    harvestDate: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000), // 2 days ago
  },
]; 