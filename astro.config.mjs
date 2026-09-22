import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://executiveordersarchive.org',
  integrations: [tailwind(), sitemap()],
  output: 'static',
  server: {
    host: true, // Listen on all network interfaces (0.0.0.0)
    port: 4321
  }
});
