import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import cloudflare from '@astrojs/cloudflare';

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
      filter: (page) => {
        // Exclude API routes and development pages
        return !page.includes('/api/') && 
               !page.includes('/dev/') && 
               !page.includes('/draft/');
      },
      serialize: (item) => {
        // Pharmacy pages get highest priority and daily updates
        if (item.url.includes('/pharmacies/')) {
          return {
            ...item,
            changefreq: 'daily',
            priority: 1.0,
            lastmod: new Date()
          };
        }
        
        // Static pages get lower priority and monthly updates
        if (item.url.includes('/about') || 
            item.url.includes('/contact-us') || 
            item.url.includes('/privacy-policy')) {
          return {
            ...item,
            changefreq: 'monthly',
            priority: 0.5,
            lastmod: new Date()
          };
        }

        // Homepage for each language
        if (item.url.endsWith('pharmasos.com/') || 
            item.url.endsWith('/fr/') || 
            item.url.endsWith('/en/') || 
            item.url.endsWith('/ar/')) {
          return {
            ...item,
            changefreq: 'daily',
            priority: 0.9,
            lastmod: new Date()
          };
        }

        return item;
      }
    })
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