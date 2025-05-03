
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
    host: '0.0.0.0',          
    port: 8080,               // Set port to 8080 to match the root config
    strictPort: true,         
    cors: true,               
    allowedHosts: true,       
    hmr: {
      protocol: 'ws',
      host: 'localhost',      
      clientPort: 443         
    }
  },
  preview: {
    host: '0.0.0.0',
    port: 8080,               // Match the server port
    strictPort: true,
    allowedHosts: true,       
    cors: true
  }
}))
