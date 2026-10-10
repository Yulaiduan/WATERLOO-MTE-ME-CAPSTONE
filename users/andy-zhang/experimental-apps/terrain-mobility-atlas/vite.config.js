import { defineConfig } from 'vite';
import { fileURLToPath } from 'node:url';

export default defineConfig({
  server: { host: '127.0.0.1', port: 5173, strictPort: true },
  // MapLibre includes its rendering engine and worker. It is loaded lazily,
  // independently of the small initial application bundle.
  build: {
    chunkSizeWarningLimit: 1600,
    rollupOptions: {
      input: {
        atlas: fileURLToPath(new URL('./index.html', import.meta.url)),
        workbench: fileURLToPath(new URL('./workbench/index.html', import.meta.url)),
        linkage: fileURLToPath(new URL('./linkage/index.html', import.meta.url)),
      },
    },
  },
});
