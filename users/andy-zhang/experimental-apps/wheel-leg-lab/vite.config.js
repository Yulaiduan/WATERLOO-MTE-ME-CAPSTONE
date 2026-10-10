import { defineConfig } from 'vite';
import { fileURLToPath } from 'node:url';
export default defineConfig({
  root: fileURLToPath(new URL('./linkage/', import.meta.url)),
  base: '/linkage/',
  build: { outDir: '../web/linkage', emptyOutDir: true },
});
