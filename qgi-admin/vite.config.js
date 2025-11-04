import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    // Use terser for better minification
    minify: 'terser',
    terserOptions: {
      compress: {
        // Remove console.log in production
        drop_console: true,
        drop_debugger: true,
      },
    },
    // Manual chunking for better caching
    rollupOptions: {
      output: {
        manualChunks: {
          // React vendor chunk
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          // Chart libraries
          'chart-vendor': ['recharts'],
          // Animation libraries
          'animation-vendor': ['framer-motion'],
          // UI components (if they're large enough)
          // 'ui-vendor': ['@radix-ui/react-*'], // Uncomment if using many radix components
        },
      },
    },
    // Increase chunk size warning limit (optional)
    chunkSizeWarningLimit: 1000,
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5174,
    host: true
  }
})

