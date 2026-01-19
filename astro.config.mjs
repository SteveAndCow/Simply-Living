import { defineConfig } from 'astro/config';
import svelte from '@astrojs/svelte';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
  integrations: [
    svelte(),
    tailwind({
      applyBaseStyles: false, // We'll use custom global styles
    })
  ],
  output: 'static',
  site: 'https://simplylivingstudios.com', // Update with actual domain
});
