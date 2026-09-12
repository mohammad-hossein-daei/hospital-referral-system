import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      },
    },
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
      '/admin': {                                // ← اضافه کنید
        target: 'http://backend:8000',
        changeOrigin: true,
      },
      '/static': {                               // برای فایل‌های استاتیک جنگو
        target: 'http://backend:8000',
        changeOrigin: true,
      },
    },
  },
});

