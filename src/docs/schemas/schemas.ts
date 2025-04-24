import { ApiProperty } from '@nestjs/swagger';

export class UserSchema {
  @ApiProperty({
    type: 'integer',
    description: 'Unique identifier for the user',
  })
  id: number;

  @ApiProperty({
    type: 'string',
    description: 'Unique username of the user',
  })
  username: string;

  @ApiProperty({
    type: 'string',
    description: 'Hashed password of the user',
  })
  password: string;
}

export class ProductSchema {
  @ApiProperty({
    type: 'string',
    format: 'uuid',
    description: 'Unique identifier for the product',
  })
  id: string;

  @ApiProperty({
    type: 'string',
    description: 'Name of the product',
  })
  name: string;

  @ApiProperty({
    type: 'string',
    description: 'Description of the product',
    nullable: true,
    required: false, 
  })
  description?: string | null; 

  @ApiProperty({
    type: 'number',
    description: 'Price of the product',
  })
  price: number;

  @ApiProperty({
    type: 'string',
    description: 'Unit of measurement (e.g., kg, liter)',
  })
  unit: string;

  @ApiProperty({
    type: 'array',
    items: { type: 'string' },
    description: 'List of image URLs',
    required: false, 
  })
  images?: string[]; 

  @ApiProperty({
    type: 'number',
    description: 'Available stock quantity',
  })
  stockQuantity: number;

  @ApiProperty({
    type: 'string',
    format: 'date-time',
    description: 'Date of harvest',
  })
  harvestDate: string;

  @ApiProperty({
    type: 'string',
    format: 'date-time',
    description: 'Creation timestamp',
    required: false, 
  })
  createdAt?: string; 

  @ApiProperty({
    type: 'string',
    format: 'date-time',
    description: 'Last update timestamp',
    required: false, 
  })
  updatedAt?: string; 
}

export class OrderSchema {
  @ApiProperty({
    type: 'string',
    format: 'uuid',
    description: 'Unique identifier for the order',
  })
  id: string;

  @ApiProperty({
    type: 'string',
    format: 'uuid',
    description: 'ID of the user who placed the order',
  })
  userId: string;

  @ApiProperty({
    type: 'number',
    description: 'Total amount of the order',
  })
  totalAmount: number;

  @ApiProperty({
    type: 'string',
    enum: ['pending', 'completed', 'canceled'],
    description: 'Order status',
  })
  status: string;

  @ApiProperty({
    type: 'string',
    format: 'date-time',
    description: 'Creation timestamp',
    required: false, 
  })
  createdAt?: string; 

  @ApiProperty({
    type: 'string',
    format: 'date-time',
    description: 'Last update timestamp',
    required: false, 
  })
  updatedAt?: string; 
}

export class OrderItemSchema {
  @ApiProperty({
    type: 'string',
    format: 'uuid',
    description: 'Unique identifier for the order item',
  })
  id: string;

  @ApiProperty({
    type: 'string',
    format: 'uuid',
    description: 'ID of the associated order',
  })
  orderId: string;

  @ApiProperty({
    type: 'string',
    format: 'uuid',
    description: 'ID of the associated product',
  })
  productId: string;

  @ApiProperty({
    type: 'number',
    description: 'Quantity of the product in the order',
  })
  quantity: number;

  @ApiProperty({
    type: 'number',
    description: 'Price of the product in the order',
  })
  price: number;
}