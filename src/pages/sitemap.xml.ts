import type { APIRoute } from 'astro';

// Redirect sitemap.xml to sitemap-0.xml
export const GET: APIRoute = async ({ site }) => {
  if (!site) {
    return new Response('Site configuration missing', { status: 500 });
  }
  
  // Return the same content as sitemap-0.xml instead of redirecting
  const response = await fetch(`${site}/sitemap-0.xml`);
  const xml = await response.text();
  
  return new Response(xml, {
    headers: {
      'Content-Type': 'application/xml',
      'Cache-Control': 'public, max-age=3600'
    },
  });
}; 