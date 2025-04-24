// src/docs/tests/validators/doc-linter.ts
import { Spectral } from '@stoplight/spectral-core';
import { fetch } from '@stoplight/spectral-runtime';
import * as path from 'path';
import * as fs from 'fs';
import axios from 'axios';
const { bundleAndLoadRuleset } = require('@stoplight/spectral-ruleset-bundler/with-loader');

export async function lintDocs(port: number = 3000, openApiSpec?: any) {
  try {
    if (!openApiSpec) {
      console.log(`Fetching OpenAPI spec from http://localhost:${port}/api/docs-json`);
      const response = await axios.get(`http://localhost:${port}/api/docs-json`);
      console.log('OpenAPI spec fetched successfully');
      openApiSpec = response.data;
    } else {
      console.log('Using provided OpenAPI spec');
    }

    const spectral = new Spectral();
    
    const rulesetPath = path.join(__dirname, '../../ruleset.yaml');
    console.log(`Loading ruleset from: ${rulesetPath}`);
    
    if (!fs.existsSync(rulesetPath)) {
      throw new Error(`Ruleset file not found at: ${rulesetPath}`);
    }

    let ruleset;
    try {
      ruleset = await bundleAndLoadRuleset(rulesetPath, { fs, fetch });
    } catch (rulesetError) {
      console.error('Error loading ruleset:', rulesetError);
      if (rulesetError instanceof AggregateError) {
        console.error('AggregateError details:', rulesetError.errors);
      }
      throw rulesetError;
    }

    if (ruleset.rules['oas3-unused-component']) {
      ruleset.rules['oas3-unused-component'].enabled = false;
      console.log('Rule oas3-unused-component disabled successfully');
    } else {
      console.warn('Rule oas3-unused-component not found in ruleset');
    }

    console.log('Ruleset loaded successfully:', ruleset.rules['oas3-unused-component']);

    spectral.setRuleset(ruleset);

    console.log('Running Spectral linting...');
    const result = await spectral.run(openApiSpec);

    if (result.length > 0) {
      throw new Error(`Documentation linting failed: ${JSON.stringify(result, null, 2)}`);
    }

    console.log('Documentation linting passed');
  } catch (error) {
    console.error('Detailed error in lintDocs:', error.message);
    if (error.response) {
      console.error('Axios error response:', error.response.data);
    }
    if (error.stack) {
      console.error('Error stack:', error.stack);
    }
    throw new Error(`Error in lintDocs: ${error.message}`);
  }
}