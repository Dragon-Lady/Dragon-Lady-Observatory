// @ts-check
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: process.env.SITE_URL || 'https://example.org',
  base: process.env.BASE_PATH || '/',
  trailingSlash: 'ignore',
  adapter: node({ mode: 'standalone' }),
  vite: { plugins: [tailwindcss()] },
});
