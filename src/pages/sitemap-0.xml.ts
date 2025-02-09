import type { APIRoute } from 'astro';

const languages = ['fr', 'ar', 'en'];
const staticPages = ['about', 'contact-us', 'privacy-policy'];
const cities = ['ain-aouda', 'casablanca', 'marrakech', 'rabat', 'sale', 'temara'];

export const GET: APIRoute = async ({ site }) => {
  if (!site) {
    return new Response('Site configuration missing', { status: 500 });
  }

  const currentDate = new Date().toISOString().replace(/\.\d+Z$/, '+00:00');
  
  // Generate URL entries
  const urls = [
    // French homepage (main language)
    {
      loc: `${site}/fr/`,
      lastmod: currentDate,
      priority: '1.00'
    },
    
    // Other language homepages
    ...['ar', 'en'].map(lang => ({
      loc: `${site}/${lang}/`,
      lastmod: currentDate,
      priority: '0.80'
    })),

    // Static pages and pharmacies for each language
    ...languages.flatMap(lang => [
      // Static pages with trailing slash
      ...staticPages.map(page => ({
        loc: `${site}/${lang}/${page}/`,
        lastmod: currentDate,
        priority: lang === 'fr' ? '0.80' : '0.64'
      })),
      
      // Static pages without trailing slash
      ...staticPages.map(page => ({
        loc: `${site}/${lang}/${page}`,
        lastmod: currentDate,
        priority: lang === 'fr' ? '0.80' : '0.64'
      })),
      
      // City pages without trailing slash
      ...cities.map(city => ({
        loc: `${site}/${lang}/pharmacies/${city}`,
        lastmod: currentDate,
        priority: lang === 'fr' ? '0.80' : '0.64'
      })),
      
      // City pages with trailing slash
      ...cities.map(city => ({
        loc: `${site}/${lang}/pharmacies/${city}/`,
        lastmod: currentDate,
        priority: '0.64'
      }))
    ])
  ];

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
<!--  created with Free Online Sitemap Generator www.xml-sitemaps.com  -->
${urls.map(url => `<url>
<loc>${url.loc}</loc>
<lastmod>${url.lastmod}</lastmod>
<priority>${url.priority}</priority>
</url>`).join('\n')}
</urlset>`;

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/xml',
      'Cache-Control': 'public, max-age=3600'
    },
  });
}; 