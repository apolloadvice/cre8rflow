
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from 'path'
import { componentTagger } from "lovable-tagger"

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [
    react(),
    mode === 'development' && componentTagger(),
  ].filter(Boolean),
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
  host: true,              // Allow external access from any IP
  port: 8080,              // Optional, or keep 5173 if default
  strictPort: true,
  origin: undefined,       // Let Vite infer origin (do NOT hardcode Loveable domain)
  hmr: {
    host: 'localhost',     // Helps bypass websocket-origin checks
    protocol: 'ws',
    }
  }
}))
