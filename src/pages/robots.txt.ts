import type { APIRoute } from 'astro';

const getRobotsTxt = (sitemapURL: URL) => `
User-agent: *
Allow: /

# Sitemaps
Sitemap: ${sitemapURL.href}sitemap.xml
Sitemap: ${sitemapURL.href}sitemap-index.xml

# Crawl-delay
Crawl-delay: 10

# Common crawlers
User-agent: Googlebot
Allow: /

User-agent: Googlebot-Image
Allow: /

User-agent: Bingbot
Allow: /

User-agent: Slurp
Allow: /

# Prevent crawling of admin or private areas
Disallow: /api/
Disallow: /admin/
Disallow: /dev/
Disallow: /draft/
`;

export const GET: APIRoute = ({ site }) => {
  if (!site) {
    return new Response('Error: site is not defined', { status: 500 });
  }
  const sitemapURL = new URL('', site);
  return new Response(getRobotsTxt(sitemapURL), {
    headers: {
      'Content-Type': 'text/plain',
    },
  });
}; 