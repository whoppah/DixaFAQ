// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: '/', 
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',  // Django dev server
    },
  },
})
