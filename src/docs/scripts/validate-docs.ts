import { NestFactory } from '@nestjs/core';
import { AppModule } from '../../app.module';
import { lintDocs } from '../tests/validators/doc-linter';
import { validateSchema } from '../tests/validators/schema-validator';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { API_VERSIONS, DEFAULT_VERSION } from '../../docs/config/api-version.config';
import { version } from '../../../package.json';
import { ProductSchema, OrderSchema, OrderItemSchema, UserSchema } from '../../docs/schemas/schemas';
import { validateExamples } from '../tests/validators/example-validator';
import { checkLinks } from '../tests/validators/link-validator';

async function generateOpenApiDocument(app: any) {
  console.log('Generating OpenAPI document...');
  const config = new DocumentBuilder()
    .setTitle('Farmers Marketplace API')
    .setDescription('API documentation for the Farmers Marketplace platform')
    .setVersion(version)
    .addApiKey({ type: 'apiKey', name: 'Authorization', in: 'header' }, 'access-token')
    .addTag('general', 'Operaciones generales de la API')
    .addTag('auth', 'Operaciones relacionadas con autenticación')
    .addTag('products', 'Operaciones relacionadas con productos')
    .addTag('categories', 'Operaciones relacionadas con categorías')
    .addTag('media', 'Operaciones relacionadas con archivos multimedia')
    .addTag('orders', 'Operaciones relacionadas con pedidos')
    .addTag('webhook', 'Operaciones relacionadas con webhooks')
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

  return document;
}

async function validateDocs() {
  const app = await NestFactory.create(AppModule);
  try {
    const openApiDocument = await generateOpenApiDocument(app);
    console.log('OpenAPI document generated successfully');

    console.log('Running lintDocs...');
    await lintDocs(3000, openApiDocument);
    console.log('lintDocs completed successfully');

    console.log('Running validateSchema...');
    await validateSchema(openApiDocument);
    console.log('validateSchema completed successfully');

    console.log('Running validateExamples...');
    await validateExamples(openApiDocument);
    console.log('validateExamples completed successfully');

    console.log('Running checkLinks...');
    await checkLinks(); 
    console.log('checkLinks completed successfully');

    console.log('Documentation validation completed successfully');
  } catch (error) {
    console.error('Documentation validation failed:', error.message);
    throw error;
  } finally {
    console.log('Closing application...');
    await app.close();
    console.log('Application closed successfully');
  }
}



validateDocs()
  .then(() => {
    process.exit(0);
  })
  .catch((error) => {
    console.error('Documentation validation failed:', error.message);
    process.exit(1);
  });