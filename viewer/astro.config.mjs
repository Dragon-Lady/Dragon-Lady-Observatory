// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: process.env.SITE_URL || 'https://example.org',
  base: process.env.BASE_PATH || '/',
  trailingSlash: 'ignore',
  vite: { plugins: [tailwindcss()] },
});
