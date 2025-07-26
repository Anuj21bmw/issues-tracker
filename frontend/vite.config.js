import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
    plugins: [sveltekit()],
    css: {
        postcss: './postcss.config.js',
    },
    server: {
        port: 5173,
        host: '0.0.0.0',
        hmr: {
            overlay: true
        },
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
                secure: false
            },
            '/ws': {
                target: 'ws://localhost:8000',
                ws: true,
                changeOrigin: true
            }
        }
    },
    preview: {
        port: 4173,
        host: '0.0.0.0'
    },
    build: {
        target: 'esnext',
        outDir: 'build'
    },
    define: {
        global: 'globalThis'
    }
});
