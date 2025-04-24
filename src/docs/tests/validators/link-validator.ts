import { execSync } from 'child_process';
import { existsSync } from 'fs';
//IF npm install linkinator --save-dev
export async function checkLinks() {
  console.log('Running link validation...');
  const specPath = 'src/docs/openapi-spec.json';

  if (!existsSync(specPath)) {
    throw new Error(`OpenAPI spec file not found at ${specPath}. Ensure validateSchema runs first.`);
  }

  try {
    execSync('npx linkinator src/docs/openapi-spec.json --skip "http://localhost|https://example.com"', { stdio: 'inherit' });
    console.log('Link validation passed');
  } catch (error) {
    throw new Error('Link validation failed: ' + error.message);
  }
}