// types/stoplight-spectral-ruleset-bundler.d.ts
declare module '@stoplight/spectral-ruleset-bundler/with-loader' {
    export function bundleAndLoadRuleset(
      rulesetPath: string,
      options: { fs: typeof import('fs'); fetch: typeof import('@stoplight/spectral-runtime').fetch }
    ): Promise<any>;
  }