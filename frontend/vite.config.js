import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	build: {
		outDir: 'build',
		emptyOutDir: true
	},
	server: {
		host: '0.0.0.0',
		port: 3000
	},
	preview: {
		host: '0.0.0.0',
		port: 3000
	}
});
