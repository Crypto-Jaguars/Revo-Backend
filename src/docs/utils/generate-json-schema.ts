import { createGenerator } from 'ts-json-schema-generator';
import * as path from 'path';

export function generateJsonSchema(className: string, filePath: string) {
  const config = {
    path: path.resolve(filePath),
    tsconfig: path.resolve('tsconfig.json'),
    type: className,
  };

  const generator = createGenerator(config);
  return generator.createSchema(className);
}