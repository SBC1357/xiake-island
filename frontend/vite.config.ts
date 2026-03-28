import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` (production, development, etc.)
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [react()],
    server: {
      proxy: {
        '/v1': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
        },
      },
    },
    define: {
      // Default to same-origin so the built frontend works for localhost and Tailscale access.
      'import.meta.env.VITE_API_BASE_URL': JSON.stringify(env.VITE_API_BASE_URL ?? ''),
    },
  }
})
