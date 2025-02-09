import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import cloudflare from '@astrojs/cloudflare';
import partytown from '@astrojs/partytown';

// https://astro.build/config
export default defineConfig({
  output: 'server',
  outDir: './dist',
  adapter: cloudflare({
    mode: 'directory',
    runtime: {
      mode: 'local',
      type: 'pages'
    },
    imageService: 'passthrough'
  }),
  integrations: [
    mdx(),
    sitemap({
      filter: (page) => !page.includes('/api/'),
      i18n: {
        defaultLocale: 'fr',
        locales: {
          fr: 'fr-FR',
          en: 'en-US',
          ar: 'ar-MA'
        }
      },
      changefreq: 'daily',
      priority: 0.7,
      lastmod: new Date(),
      serialize: (item) => {
        // Customize priority for different pages
        if (item.url.includes('/pharmacies/')) {
          return {
            ...item,
            changefreq: 'daily',
            priority: 1.0
          };
        }
        if (item.url.includes('/about') || item.url.includes('/contact-us')) {
          return {
            ...item,
            changefreq: 'monthly',
            priority: 0.5
          };
        }
        return item;
      }
    }),
    partytown({
      config: {
        forward: ["dataLayer.push", "gtag"],
        debug: true
      },
    }),
  ],
  i18n: {
    defaultLocale: 'fr',
    locales: ['fr', 'ar', 'en'],
    routing: {
      prefixDefaultLocale: true,
    },
  },
  vite: {
    ssr: {
      noExternal: ['astro:i18n']
    }
  },
  site: 'https://pharmasos.com',
  server: {
    host: true,
    port: 4321
  }
});