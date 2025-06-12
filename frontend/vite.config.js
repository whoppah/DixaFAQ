// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  base: '/', 
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'), 
    },
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000',  // Django dev server
    },
  },
})
