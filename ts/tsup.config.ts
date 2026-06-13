import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  dts: true,
  splitting: false,
  sourcemap: true,
  clean: true,
  // Bundle JSON data files inline so the package is self-contained
  // (required for browser and React Native consumers).
  loader: { '.json': 'json' },
  noExternal: [/\.json$/],
});
