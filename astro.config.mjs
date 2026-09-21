import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
  site: 'https://executiveordersarchive.org',
  integrations: [tailwind()],
  output: 'static',
  server: {
    host: true, // Listen on all network interfaces (0.0.0.0)
    port: 4321
  }
});
