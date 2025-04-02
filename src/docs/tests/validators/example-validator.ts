import Ajv from 'ajv';
import { ProductSchema, OrderSchema, OrderItemSchema, UserSchema } from '../../schemas/schemas';
import { generateJsonSchema } from '../../utils/generate-json-schema';

const ajv = new Ajv({ allErrors: true });

export async function validateExamples(openApiSpec?: any) {
  try {
    if (!openApiSpec) {
      throw new Error('OpenAPI spec must be provided');
    }

    const generatedSchemas = openApiSpec.components?.schemas || {};

    const schemaClasses = {
      ProductSchema,
      OrderSchema,
      OrderItemSchema,
      UserSchema,
    };
    //IF npm install ts-json-schema-generator ajv
    for (const [schemaName] of Object.entries(schemaClasses)) {
      const schema = generateJsonSchema(schemaName, 'src/docs/schemas/schemas.ts');
      const validate = ajv.compile(schema); 

      const generatedSchema = generatedSchemas[schemaName];
      if (!generatedSchema) {
        throw new Error(`Schema ${schemaName} not found in OpenAPI specification`);
      }

      const properties = generatedSchema.properties || {};
      for (const [propName, prop] of Object.entries(properties)) {
        const example = (prop as any).example;
        if (example !== undefined) {
          const valid = validate({ [propName]: example }); // Validar el ejemplo
          if (!valid) {
            console.log(`Validation errors for ${schemaName}.${propName}:`, validate.errors);
            throw new Error(`Example for ${propName} in ${schemaName} is invalid`);
          }
        }
      }
    }

    console.log('Example validation passed');
  } catch (error) {
    throw new Error(`Example validation error: ${error.message}`);
  }
}