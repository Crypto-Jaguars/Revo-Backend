# **Schemas Documentation**

This document provides an overview of the schemas used in the application. The schemas define the structure of the data models, including their fields, types, and validation rules. These schemas are used for validation, documentation, and serialization of data in the application.

---

## **Schemas and Their Uses**

### **1. Product Schema**

- **Purpose**: Represents a product in the system.
- **Uses**:
  - Validation of product data.
  - Documentation in Swagger/OpenAPI.
  - Serialization of product data in API responses.

**Fields**:
| Field          | Type     | Description                              | Constraints                |
|-----------------|----------|------------------------------------------|----------------------------|
| `id`           | String   | Unique identifier for the product.       | Required, UUID format      |
| `name`         | String   | Name of the product.                     | Required                   |
| `description`  | String   | Description of the product.              | Optional                   |
| `price`        | Number   | Price of the product.                    | Required                   |
| `unit`         | String   | Unit of measurement (e.g., kg, liter).   | Required                   |
| `images`       | Array    | List of image URLs for the product.      | Optional                   |
| `stockQuantity`| Number   | Quantity of the product in stock.        | Required                   |
| `harvestDate`  | Date     | Date the product was harvested.          | Required                   |
| `createdAt`    | Date     | Timestamp when the product was created.  | Auto-generated             |
| `updatedAt`    | Date     | Timestamp when the product was last updated. | Auto-generated         |

**Example Schema**:
```typescript
export const ProductSchema = {
  type: 'object',
  properties: {
    id: { type: 'string', format: 'uuid', description: 'Unique identifier for the product' },
    name: { type: 'string', description: 'Name of the product' },
    description: { type: 'string', nullable: true, description: 'Description of the product' },
    price: { type: 'number', format: 'decimal', description: 'Price of the product' },
    unit: { type: 'string', description: 'Unit of measurement (e.g., kg, liter)' },
    images: { type: 'array', items: { type: 'string' }, description: 'List of image URLs' },
    stockQuantity: { type: 'number', description: 'Available stock quantity' },
    harvestDate: { type: 'string', format: 'date-time', description: 'Date of harvest' },
    createdAt: { type: 'string', format: 'date-time', description: 'Creation timestamp' },
    updatedAt: { type: 'string', format: 'date-time', description: 'Last update timestamp' },
  },
  required: ['id', 'name', 'price', 'unit', 'stockQuantity', 'harvestDate'],
};
```
# Order Schema Documentation

## Purpose
The **Order Schema** represents an order placed by a user. It is used in various contexts, including:

- **Validation** of order data to ensure integrity before saving or processing.
- **Documentation** in Swagger/OpenAPI to provide clear API documentation.
- **Serialization** of order data in API responses to ensure proper formatting.

## Example Schema

```typescript
export const OrderSchema = {
  type: 'object',
  properties: {
    id: { 
      type: 'string', 
      format: 'uuid', 
      description: 'Unique identifier for the order' 
    },
    userId: { 
      type: 'string', 
      format: 'uuid', 
      description: 'ID of the user who placed the order' 
    },
    totalAmount: { 
      type: 'number', 
      format: 'decimal', 
      description: 'Total amount of the order' 
    },
    status: { 
      type: 'string', 
      enum: ['pending', 'completed', 'canceled'], 
      description: 'Order status' 
    },
    createdAt: { 
      type: 'string', 
      format: 'date-time', 
      description: 'Creation timestamp' 
    },
    updatedAt: { 
      type: 'string', 
      format: 'date-time', 
      description: 'Last update timestamp' 
    },
  },
  required: ['id', 'userId', 'totalAmount', 'status'],
};
```

# OrderItem Schema Documentation

## Purpose
The **OrderItem Schema** represents an item in an order. It is used in various contexts, including:

- **Validation** of order item data to ensure integrity before saving or processing.
- **Documentation** in Swagger/OpenAPI to provide clear API documentation.
- **Serialization** of order item data in API responses to ensure proper formatting.

## Example Schema

```typescript
export const OrderItemSchema = {
  type: 'object',
  properties: {
    id: { 
      type: 'string', 
      format: 'uuid', 
      description: 'Unique identifier for the order item' 
    },
    orderId: { 
      type: 'string', 
      format: 'uuid', 
      description: 'ID of the associated order' 
    },
    productId: { 
      type: 'string', 
      format: 'uuid', 
      description: 'ID of the associated product' 
    },
    quantity: { 
      type: 'number', 
      description: 'Quantity of the product in the order' 
    },
    price: { 
      type: 'number', 
      format: 'decimal', 
      description: 'Price of the product in the order' 
    },
  },
  required: ['id', 'orderId', 'productId', 'quantity', 'price'],
};
```


# **User Schema Documentation**

## Purpose
The **User Schema** represents a user in the system. It is used in various contexts, including:

- **Validation** of user data to ensure integrity before saving or processing.
- **Documentation** in Swagger/OpenAPI to provide clear API documentation.
- **Serialization** of user data in API responses to ensure proper formatting.

## Example Schema

```typescript
export const UserSchema = {
  type: 'object',
  properties: {
    id: { type: 'integer', description: 'Unique identifier for the user' },
    username: { type: 'string', description: 'Unique username of the user' },
    password: { type: 'string', description: 'Hashed password of the user' },
  },
  required: ['id', 'username', 'password'],
};
```