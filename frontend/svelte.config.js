// import adapter from '@sveltejs/adapter-static';

// const config = {
// 	kit: {
// 		adapter: adapter({
// 			pages: 'build',
// 			assets: 'build',
// 			fallback: 'index.html',
// 			precompress: false
// 		})
// 	}
// };

// export default config;



import adapter from '@sveltejs/adapter-auto';
import { vitePreprocess } from '@sveltejs/kit/vite';

/** @type {import('@sveltejs/kit').Config} */
const config = {
    // Consult https://kit.svelte.dev/docs/integrations#preprocessors
    preprocess: vitePreprocess(),

    kit: {
        // adapter-auto only supports some environments, see https://kit.svelte.dev/docs/adapter-auto for a list.
        adapter: adapter(),
        
        // Path configuration
        paths: {
            base: '',
            assets: ''
        },
        
        // Prerender configuration
        prerender: {
            handleHttpError: 'warn'
        },
        
        // Service worker
        serviceWorker: {
            register: false
        },
        
        // CSP configuration for security
        csp: {
            mode: 'auto'
        }
    }
};

export default config;