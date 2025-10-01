import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';
import path from 'path';

export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  resolve: {
    alias: [
      { find: '@', replacement: path.resolve(__dirname, 'src') },
      { find: '@studentgpt', replacement: path.resolve(__dirname, 'studentgpt/src') }
    ]
  },
  base: '/',
  server: {
    port: 3000,
    host: 'localhost',
    strictPort: true,
    open: false,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api/v1'),
      }
    }
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks: {
          react: ['react', 'react-dom', 'react-router-dom'],
        },
      },
    },
  },
  // This is needed for client-side routing to work
  appType: 'spa',
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom'],
  },
  // Add fallback for SPA routing
  preview: {
    port: 3000,
    host: 'localhost',
  },
  // Add this to handle client-side routing
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development'),
  },
});
