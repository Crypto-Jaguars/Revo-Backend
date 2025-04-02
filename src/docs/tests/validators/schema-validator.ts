import { writeFileSync } from 'fs';
import SwaggerParser from '@apidevtools/swagger-parser';
import { ProductSchema, OrderSchema, OrderItemSchema, UserSchema } from '../../schemas/schemas';
import deepEqual from 'deep-equal';

export async function validateSchema(openApiSpec?: any) {
  try {
    if (!openApiSpec) {
      throw new Error('OpenAPI spec must be provided');
    }

    writeFileSync('src/docs/openapi-spec.json', JSON.stringify(openApiSpec, null, 2));

    await SwaggerParser.validate(openApiSpec);
    const generatedSchemas = openApiSpec.components?.schemas || {};

    const expectedSchemas = {
      ProductSchema: {
        class: ProductSchema,
        properties: {
          id: { type: 'string', format: 'uuid', description: 'Unique identifier for the product' },
          name: { type: 'string', description: 'Name of the product' },
          description: { type: 'string', description: 'Description of the product', nullable: true },
          price: { type: 'number', description: 'Price of the product' },
          unit: { type: 'string', description: 'Unit of measurement (e.g., kg, liter)' },
          images: { type: 'array', items: { type: 'string' }, description: 'List of image URLs' },
          stockQuantity: { type: 'number', description: 'Available stock quantity' },
          harvestDate: { type: 'string', format: 'date-time', description: 'Date of harvest' },
          createdAt: { type: 'string', format: 'date-time', description: 'Creation timestamp' },
          updatedAt: { type: 'string', format: 'date-time', description: 'Last update timestamp' },
        },
        required: ['id', 'name', 'price', 'unit', 'stockQuantity', 'harvestDate'],
      },
      OrderSchema: {
        class: OrderSchema,
        properties: {
          id: { type: 'string', format: 'uuid', description: 'Unique identifier for the order' },
          userId: { type: 'string', format: 'uuid', description: 'ID of the user who placed the order' },
          totalAmount: { type: 'number', description: 'Total amount of the order' },
          status: { type: 'string', enum: ['pending', 'completed', 'canceled'], description: 'Order status' },
          createdAt: { type: 'string', format: 'date-time', description: 'Creation timestamp' },
          updatedAt: { type: 'string', format: 'date-time', description: 'Last update timestamp' },
        },
        required: ['id', 'userId', 'totalAmount', 'status'],
      },
      OrderItemSchema: {
        class: OrderItemSchema,
        properties: {
          id: { type: 'string', format: 'uuid', description: 'Unique identifier for the order item' },
          orderId: { type: 'string', format: 'uuid', description: 'ID of the associated order' },
          productId: { type: 'string', format: 'uuid', description: 'ID of the associated product' },
          quantity: { type: 'number', description: 'Quantity of the product in the order' },
          price: { type: 'number', description: 'Price of the product in the order' },
        },
        required: ['id', 'orderId', 'productId', 'quantity', 'price'],
      },
      UserSchema: {
        class: UserSchema,
        properties: {
          id: { type: 'integer', description: 'Unique identifier for the user' }, // Esto ya es correcto
          username: { type: 'string', description: 'Unique username of the user' },
          password: { type: 'string', description: 'Hashed password of the user' },
        },
        required: ['id', 'username', 'password'],
      },
    };

    for (const [schemaName, { properties: expectedProps, required: expectedRequired }] of Object.entries(expectedSchemas)) {
      const generatedSchema = generatedSchemas[schemaName];
      if (!generatedSchema) {
        throw new Error(`Schema ${schemaName} not found in OpenAPI specification`);
      }

      const generatedProps = generatedSchema.properties || {};
      for (const [propName, expectedProp] of Object.entries(expectedProps)) {
        if (!generatedProps[propName]) {
          throw new Error(`Property ${propName} not found in schema ${schemaName}`);
        }
        if (!deepEqual(expectedProp, generatedProps[propName], { strict: false })) {
          console.log(`Expected property ${propName}:`, expectedProp);
          console.log(`Generated property ${propName}:`, generatedProps[propName]);
          throw new Error(`Property ${propName} in schema ${schemaName} does not match expected definition`);
        }
      }

      const generatedRequired = (generatedSchema.required || []).sort();
      const sortedExpectedRequired = expectedRequired.sort();
      if (!deepEqual(sortedExpectedRequired, generatedRequired)) {
        throw new Error(`Schema ${schemaName} required fields do not match. Expected: ${sortedExpectedRequired}, Got: ${generatedRequired}`);
      }
    }

    console.log('Schema validation passed');
  } catch (error) {
    throw new Error(`Schema validation error: ${error.message}`);
  }
}