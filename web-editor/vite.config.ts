import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // 后端（MD 读写 / 导出）代理到 Express :8080
      '/api': 'http://127.0.0.1:8080',
      '/exports': 'http://127.0.0.1:8080',
    },
  },
})
