import type { APIRoute } from 'astro';

export const GET: APIRoute = () => {
  const xsl = `<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" 
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9">
  <xsl:output method="html" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <html>
      <head>
        <title>Sitemap - PharmaS.O.S</title>
        <style>
          body { font-family: -apple-system, system-ui, sans-serif; color: #333; max-width: 1200px; margin: 0 auto; padding: 1rem; }
          h1 { color: #22c55e; }
          table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
          th, td { padding: 0.5rem; text-align: left; border-bottom: 1px solid #ddd; }
          th { background: #f9fafb; }
          a { color: #22c55e; text-decoration: none; }
          a:hover { text-decoration: underline; }
        </style>
      </head>
      <body>
        <h1>PharmaS.O.S Sitemap</h1>
        <table>
          <tr>
            <th>URL</th>
            <th>Last Modified</th>
          </tr>
          <xsl:for-each select="sitemap:sitemapindex/sitemap:sitemap">
            <tr>
              <td><a href="{sitemap:loc}"><xsl:value-of select="sitemap:loc"/></a></td>
              <td><xsl:value-of select="sitemap:lastmod"/></td>
            </tr>
          </xsl:for-each>
        </table>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>`;

  return new Response(xsl, {
    headers: {
      'Content-Type': 'text/xsl',
      'Cache-Control': 'public, max-age=3600'
    },
  });
}; 