import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    // Use esbuild for faster builds and better tree-shaking
    minify: 'esbuild',
    target: 'es2015',
    cssCodeSplit: true,
    sourcemap: false,
    // Manual chunking for better caching
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            // React and React-related libraries
            if (id.includes('react') || id.includes('react-dom') || id.includes('react-router')) {
              return 'react-vendor';
            }
            // Lucide icons
            if (id.includes('lucide-react')) {
              return 'icons';
            }
            // Radix UI components
            if (id.includes('@radix-ui')) {
              return 'ui-vendor';
            }
            // Recharts - keep in main bundle to avoid circular dependencies
            // Other vendor libraries
            return 'vendor';
          }
        }
      },
    },
    // Increase chunk size warning limit
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

