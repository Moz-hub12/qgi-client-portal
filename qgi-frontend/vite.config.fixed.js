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
        // Manual chunking for better code splitting
        manualChunks(id) {
          // Vendor chunks
          if (id.includes('node_modules/react') || 
              id.includes('node_modules/react-dom') || 
              id.includes('node_modules/react-router-dom')) {
            return 'react-vendor'
          }
          
          // UI vendor chunk
          if (id.includes('node_modules/@radix-ui')) {
            return 'ui-vendor'
          }
          
          // Chart vendor chunk
          if (id.includes('node_modules/recharts')) {
            return 'chart-vendor'
          }
          
          // Note: lucide-react icons are now tree-shakable, so they'll be in the main bundle
          // This is actually better for performance with the optimized imports
        },
      },
    },
    copyPublicDir: true,
    // Optimize chunk size
    chunkSizeWarningLimit: 600,
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

