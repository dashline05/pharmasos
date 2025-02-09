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
      filter: (page) => {
        return !page.includes('/api/') && 
               !page.includes('/dev/') && 
               !page.includes('/draft/') &&
               !page.includes('/blog/');
      },
      lastmod: new Date().toISOString().split('T')[0],
      serialize: (item) => {
        const url = new URL(item.url);
        const path = url.pathname;
        
        // French homepage
        if (path === '/fr/') {
          return { ...item, priority: 1.00 };
        }
        
        // Other homepages
        if (path === '/ar/' || path === '/en/') {
          return { ...item, priority: 0.80 };
        }

        // French pages
        if (path.startsWith('/fr/')) {
          return { ...item, priority: 0.80 };
        }

        // Other pages
        return { ...item, priority: 0.64 };
      },
      customPages: [
        // Cities for each language
        ...['fr', 'ar', 'en'].flatMap(lang => 
          ['ain-aouda', 'casablanca', 'marrakech', 'rabat', 'sale', 'temara']
            .map(city => `https://pharmasos.com/${lang}/pharmacies/${city}`)
        )
      ]
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