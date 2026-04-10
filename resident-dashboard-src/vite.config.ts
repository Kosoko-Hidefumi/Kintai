import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../resident_dashboard',
    // Windows で別プロセスが assets を掴むと emptyOutDir が EPERM になることがある
    emptyOutDir: false,
  },
})
