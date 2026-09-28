import { build, preview } from 'vite'
import react from '@vitejs/plugin-react'

const timeout = 300000
const outDir = 'dist'
const proxy = Object.fromEntries(
  ['/auth', '/doctors', '/patients', '/reports', '/analysis', '/health'].map((path) => [
    path,
    {
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
      proxyTimeout: timeout,
      timeout,
    },
  ]),
)

proxy['/chat'] = {
  target: 'http://localhost:8000',
  changeOrigin: true,
  secure: false,
  ws: true,
  proxyTimeout: timeout,
  timeout,
}

const sharedConfig = {
  configFile: false,
  root: process.cwd(),
  plugins: [react()],
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
}

await build({
  ...sharedConfig,
  build: {
    outDir,
    emptyOutDir: true,
  },
})

if (!process.argv.includes('--build-only')) {
  const server = await preview({
    ...sharedConfig,
    build: { outDir },
    preview: {
      host: '127.0.0.1',
      port: 5173,
      strictPort: true,
      proxy,
    },
  })

  server.printUrls()
}
