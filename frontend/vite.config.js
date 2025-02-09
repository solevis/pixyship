import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue(),
    vuetify({ autoImport: true }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build: {
    assetsDir: 'static',
    sourcemap: false,
  },
  server: {
    host: '0.0.0.0',
    port: 8080,
    // Ajout de ces configurations
    hmr: true,
    base: '/',  // Important pour le routing
    middlewareMode: false
  },
  // Base URL pour la production
  base: '/',
  // Gestion des assets publics
  publicDir: 'public',
})
