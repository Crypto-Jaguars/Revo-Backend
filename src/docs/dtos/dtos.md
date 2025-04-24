# DTO Documentation

This document provides an overview of the Data Transfer Objects (DTOs) used in the application. DTOs are used to define the structure of data sent to and from the API. They ensure data consistency, validation, and type safety.

## 1. CreateProductDTO

### Purpose:
Defines the structure of data required to create a new product.

### Usage:
- Used in the `POST /products` endpoint to validate and process incoming data for creating a product.
- Ensures that all required fields are provided and valid.

### Fields:

| Field            | Type    | Description                                                      | Constraints                       |
|------------------|---------|------------------------------------------------------------------|-----------------------------------|
| `name`           | String  | Name of the product.                                             | Required, Must be a string        |
| `description`    | String  | Description of the product.                                      | Optional, Must be a string        |
| `price`          | Number  | Price of the product.                                            | Required, Must be a number        |
| `unit`           | String  | Unit of measurement (e.g., kg, liter).                          | Required, Must be a string        |
| `images`         | Array   | List of image URLs for the product.                              | Optional, Must be an array of strings |
| `stockQuantity`  | Number  | Quantity of the product in stock.                                | Required, Must be a number        |
| `harvestDate`    | Date    | Date the product was harvested.                                  | Required, Must be a valid date    |

### Example Code:
```typescript
import {
  IsString,
  IsNumber,
  IsOptional,
  IsArray,
  IsDate,
  IsNotEmpty,
} from 'class-validator';

export class CreateProductDTO {
  @IsNotEmpty()
  @IsString()
  name: string;

  @IsOptional()
  @IsString()
  description?: string;

  @IsNotEmpty()
  @IsNumber()
  price: number;

  @IsNotEmpty()
  @IsString()
  unit: string;

  @IsOptional()
  @IsArray()
  images?: string[];

  @IsNotEmpty()
  @IsNumber()
  stockQuantity: number;

  @IsNotEmpty()
  @IsDate()
  harvestDate: Date;
}
```

## 2. UpdateProductDTO

### Purpose:
Defines the structure of data required to update an existing product.

### Usage:
- Used in the `PATCH /products/:id` endpoint to validate and process incoming data for updating a product.
- Allows partial updates, meaning only the fields that need to be updated are required.

### Fields:

| Field            | Type    | Description                                                      | Constraints                       |
|------------------|---------|------------------------------------------------------------------|-----------------------------------|
| `name`           | String  | Name of the product.                                             | Optional, Must be a string        |
| `description`    | String  | Description of the product.                                      | Optional, Must be a string        |
| `price`          | Number  | Price of the product.                                            | Optional, Must be a number        |
| `unit`           | String  | Unit of measurement (e.g., kg, liter).                          | Optional, Must be a string        |
| `images`         | Array   | List of image URLs for the product.                              | Optional, Must be an array of strings |
| `stockQuantity`  | Number  | Quantity of the product in stock.                                | Optional, Must be a number        |
| `harvestDate`    | Date    | Date the product was harvested.                                  | Optional, Must be a valid date    |

### Example Code:
```typescript
import {
  IsString,
  IsNumber,
  IsOptional,
  IsArray,
  IsDate,
} from 'class-validator';

export class UpdateProductDTO {
  @IsString()
  @IsOptional()
  name?: string;

  @IsString()
  @IsOptional()
  description?: string;

  @IsNumber()
  @IsOptional()
  price?: number;

  @IsString()
  @IsOptional()
  unit?: string;

  @IsArray()
  @IsOptional()
  images?: string[];

  @IsNumber()
  @IsOptional()
  stockQuantity?: number;

  @IsDate()
  @IsOptional()
  harvestDate?: Date;
}

```
