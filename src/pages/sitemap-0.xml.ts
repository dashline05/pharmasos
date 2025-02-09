import type { APIRoute } from 'astro';
import pharmacyData from "@/data/pharmacyData.json";

const languages = ['fr', 'ar', 'en'];
const staticPages = ['about', 'contact-us', 'privacy-policy'];
const cities = ['ain-aouda', 'casablanca', 'marrakech', 'rabat', 'sale', 'temara'];

export const GET: APIRoute = async ({ site }) => {
  if (!site) {
    return new Response('Site configuration missing', { status: 500 });
  }

  const currentDate = new Date().toISOString().slice(0, 19) + '+01:00';
  
  // Generate URL entries
  const urls = [
    // Home page
    {
      loc: `${site}/`,
      lastmod: currentDate,
      priority: '1.0'
    },
    
    // Language root pages
    ...languages.map(lang => ({
      loc: `${site}${lang}/`,
      lastmod: currentDate,
      priority: '0.8'
    })),

    // Static pages for each language
    ...languages.flatMap(lang => 
      staticPages.map(page => [
        {
          loc: `${site}${lang}/${page}/`,
          lastmod: currentDate,
          priority: '0.6'
        },
        {
          loc: `${site}${lang}/${page}`,
          lastmod: currentDate,
          priority: '0.8'
        }
      ]).flat()
    ),

    // City pages for each language
    ...languages.flatMap(lang =>
      cities.map(city => [
        {
          loc: `${site}${lang}/pharmacies/${city}`,
          lastmod: currentDate,
          priority: '0.6'
        },
        {
          loc: `${site}${lang}/pharmacies/${city}/`,
          lastmod: currentDate,
          priority: '0.4'
        }
      ]).flat()
    )
  ];

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
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