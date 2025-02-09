import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

const languages = ['fr', 'en', 'ar'];
const pages = ['', 'about', 'contact-us', 'privacy-policy', 'pharmacies'];

export const GET: APIRoute = async ({ site }) => {
  if (!site) {
    return new Response('Site configuration missing', { status: 500 });
  }

  const sitemapEntries = pages.flatMap(page => 
    languages.map(lang => ({
      url: `${site}${lang}/${page}`,
      lastmod: new Date().toISOString(),
      changefreq: page === 'pharmacies' ? 'daily' : 'monthly',
      priority: page === 'pharmacies' ? '1.0' : page === '' ? '0.9' : '0.5'
    }))
  );

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
            xmlns:xhtml="http://www.w3.org/1999/xhtml">
      ${sitemapEntries.map(entry => `
        <url>
          <loc>${entry.url}</loc>
          <lastmod>${entry.lastmod}</lastmod>
          <changefreq>${entry.changefreq}</changefreq>
          <priority>${entry.priority}</priority>
          ${languages.map(lang => `
            <xhtml:link 
              rel="alternate" 
              hreflang="${lang}" 
              href="${site}${lang}/${entry.url.split('/').pop()}"
            />`).join('')}
        </url>
      `).join('')}
    </urlset>`;

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/xml',
      'Cache-Control': 'public, max-age=3600'
    },
  });
}; 