import type { APIRoute } from 'astro';

// Redirect sitemap.xml to sitemap-0.xml
export const GET: APIRoute = ({ site, redirect }) => {
  if (!site) {
    return new Response('Site configuration missing', { status: 500 });
  }
  
  return redirect('/sitemap-0.xml', 301);
}; 