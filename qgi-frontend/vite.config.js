import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  root: '.',
  publicDir: 'public',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: './index.html',
      output: {
        // Manual chunking - EXCLUDING recharts to avoid initialization issues
        manualChunks(id) {
          // Only chunk React vendor (most stable)
          if (id.includes('node_modules/react') || 
              id.includes('node_modules/react-dom') || 
              id.includes('node_modules/react-router-dom')) {
            return 'react-vendor'
          }
          
          // UI vendor chunk
          if (id.includes('node_modules/@radix-ui')) {
            return 'ui-vendor'
          }
          
          // NOTE: Recharts is NOT chunked separately to avoid circular dependency issues
          // It will be included in the main bundle where initialization order is guaranteed
        },
      },
    },
    copyPublicDir: true,
    // Optimize chunk size
    chunkSizeWarningLimit: 1000,
    // Use esbuild for minification (faster and no extra dependencies)
    minify: 'esbuild',
  },
  esbuild: {
    // Drop console and debugger in production
    drop: ['console', 'debugger'],
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    host: true
  },
  // Optimize dependencies
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom'],
  },
})

