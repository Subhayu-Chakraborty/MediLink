import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  server: {
    port: 5173,
    host: true, // bind to 0.0.0.0 for Docker compatibility

    // Proxy API requests to the FastAPI backend during development.
    // This avoids CORS issues locally — the browser sees requests
    // going to the same origin (localhost:5173).
    proxy: {
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        proxyTimeout: 300000,
        timeout: 300000,
      },
      '/doctors': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        proxyTimeout: 300000,
        timeout: 300000,
      },
      '/patients': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        proxyTimeout: 300000,
        timeout: 300000,
      },
      '/reports': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        proxyTimeout: 300000,
        timeout: 300000,
      },
      '/analysis': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        proxyTimeout: 300000,
        timeout: 300000,
      },
      '/chat': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        ws: true,
        proxyTimeout: 300000,
        timeout: 300000,
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        proxyTimeout: 300000,
        timeout: 300000,
      },
    },
  },

  // Resolve aliases for cleaner imports.
  resolve: {
    alias: {
      '@': '/src',
      '@components': '/src/components',
      '@pages': '/src/pages',
      '@services': '/src/services',
      '@hooks': '/src/hooks',
      '@context': '/src/context',
      '@types': '/src/types',
      '@utils': '/src/utils',
      '@layouts': '/src/layouts',
    },
  },
})
