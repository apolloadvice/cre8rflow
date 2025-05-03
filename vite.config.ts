
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
      '@': path.resolve(__dirname, './frontend/src'),
    },
  },
  build: {
    outDir: 'dist',
  },
  root: './',
  server: {
    host: '0.0.0.0',          // bind on all interfaces
    port: 8080,               // keep the same port the Dockerfile expects
    strictPort: true,         // fail if 8080 is busy
    cors: true,               // let Lovable's proxy iframe the app
    allowedHosts: true,       // accept any host
    hmr: {
      protocol: 'ws',
      host: 'localhost',      // bypass websocket host check
      clientPort: 443         // works for both HTTP and HTTPS previews
    }
  },
  preview: {
    host: '0.0.0.0',
    port: 8080,
    strictPort: true,
    allowedHosts: true,       // preview server (needed since Vite 5.4.12+)
    cors: true
  }
}))
