import type { APIRoute } from 'astro';

// Redirect sitemap.xml to sitemap-index.xml
export const GET: APIRoute = ({ site, redirect }) => {
  if (!site) {
    return new Response('Site configuration missing', { status: 500 });
  }
  
  return redirect('/sitemap-index.xml', 301);
}; 