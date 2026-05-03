import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    watch: {
      usePolling: true,   // required for HMR inside Docker on Linux
      interval: 500,
    },
    proxy: {
      '/api': {
        target: 'http://jpos-cms-backend:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
