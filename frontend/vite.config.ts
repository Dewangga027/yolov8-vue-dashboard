import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  server: {
    proxy: {
      '/static': 'http://localhost:5000'
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@pages': path.resolve(__dirname, 'src/pages'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@assets': path.resolve(__dirname, 'src/assets'),
      '@router': path.resolve(__dirname, 'src/router'),
      '@icon': path.resolve(__dirname, 'src/icon'),
      '@composables': path.resolve(__dirname, 'src/composables'),
    },
  },
  plugins: [vue(), tailwindcss()],
})
