import type { APIRoute } from 'astro';

const languages = ['fr', 'ar', 'en'];
const staticPages = ['about', 'contact-us', 'privacy-policy'];
const cities = ['ain-aouda', 'casablanca', 'marrakech', 'rabat', 'sale', 'temara'];

export const GET: APIRoute = async ({ site }) => {
  if (!site) {
    return new Response('Site configuration missing', { status: 500 });
  }

  const currentDate = new Date().toISOString().split('T')[0];
  
  const urls = [
    // French homepage
    {
      loc: `${site}/fr/`,
      lastmod: currentDate,
      priority: '1.00'
    },
    
    // Other homepages
    ...['ar', 'en'].map(lang => ({
      loc: `${site}/${lang}/`,
      lastmod: currentDate,
      priority: '0.80'
    })),

    // Pages for each language
    ...languages.flatMap(lang => [
      ...staticPages.map(page => ({
        loc: `${site}/${lang}/${page}/`,
        lastmod: currentDate,
        priority: lang === 'fr' ? '0.80' : '0.64'
      })),
      ...cities.map(city => ({
        loc: `${site}/${lang}/pharmacies/${city}/`,
        lastmod: currentDate,
        priority: lang === 'fr' ? '0.80' : '0.64'
      }))
    ])
  ];

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
${urls.map(url => `<url>
  <loc>${url.loc}</loc>
  <lastmod>${url.lastmod}</lastmod>
  <priority>${url.priority}</priority>
</url>`).join('\n')}
</urlset>`;

  return new Response(xml.trim(), {
    headers: {
      'Content-Type': 'application/xml',
      'Cache-Control': 'no-cache',
      'X-Content-Type-Options': 'nosniff'
    },
  });
}; 