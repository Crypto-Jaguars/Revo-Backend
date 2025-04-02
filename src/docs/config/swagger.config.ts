// src/docs/config/swagger.config.ts
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { INestApplication } from '@nestjs/common';
import { API_VERSIONS, DEFAULT_VERSION } from './api-version.config';
import { version } from '../../../package.json';
import { ProductSchema, OrderSchema, OrderItemSchema, UserSchema } from '../schemas/schemas';

export const setupSwagger = (app: INestApplication) => {
  console.log('Setting up Swagger...');

  const config = new DocumentBuilder()
    .setTitle('Farmers Marketplace API')
    .setDescription('API documentation for the Farmers Marketplace platform')
    .setVersion(version)
    .addApiKey({ type: 'apiKey', name: 'Authorization', in: 'header' }, 'access-token')
    .addTag('auth', 'Authentication endpoints')
    .addTag('users', 'User management endpoints')
    .addTag('products', 'Operations related to products')
    .addTag('categories', 'Operations related to categories')
    .addTag('media', 'Operations related to media files')
    .addTag('orders', 'Operations related to orders')
    .addTag('webhook', 'Operations related to webhooks')
    .addServer(`/api/${DEFAULT_VERSION}`)
    .addServer('/api/v1')
    .addServer('/api/v2');

  API_VERSIONS.forEach((apiVersion) => {
    if (apiVersion.status === 'active') {
      config.addServer(`/api/${apiVersion.version}`);
    }
  });

  const documentConfig = config.build();
  const document = SwaggerModule.createDocument(app, documentConfig, {
    extraModels: [ProductSchema, OrderSchema, OrderItemSchema, UserSchema],
  });

  console.log('Swagger document created successfully');

  SwaggerModule.setup('api/docs', app, document, {
    swaggerOptions: {
      persistAuthorization: true,
      docExpansion: 'none',
      filter: true,
      showRequestDuration: true,
      syntaxHighlight: {
        theme: 'monokai',
      },
    },
    customSiteTitle: 'Farmers Marketplace API Documentation',
    customfavIcon: '/favicon.ico',
  });


  app.getHttpAdapter().get('/api/docs-json', (req, res) => {
    res.json(document);
  });

  console.log('Swagger setup completed at /api/docs and /api/docs-json');
};