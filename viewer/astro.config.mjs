// @ts-check
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: process.env.SITE_URL || 'https://example.org',
  base: process.env.BASE_PATH || '/',
  trailingSlash: 'ignore',
  adapter: node({ mode: 'standalone' }),
  // Hide the bottom-center Astro dev toolbar — it was intercepting clicks meant
  // for centered UI underneath it. (It never appeared in production anyway.)
  devToolbar: { enabled: false },
  vite: { plugins: [tailwindcss()] },
});
