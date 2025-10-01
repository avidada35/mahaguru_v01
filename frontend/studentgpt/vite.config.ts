import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
  server: {
    port: 5174, // Different from main app
  },
  base: '/studentgpt/', // Important: this makes it work as a subpath
});
