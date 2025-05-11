/**
 * Cleans a file path to create a URL-friendly slug
 */
export function cleanSlug(id: string): string {
  return id.split('/').pop()
    ?.replace(/\.mdx$/, '')
    ?.toLowerCase()
    ?.normalize('NFD')
    ?.replace(/[\u0300-\u036f]/g, '') // Remove diacritics
    ?.replace(/[^a-z0-9]+/g, '-') // Replace non-alphanumeric with hyphens
    ?.replace(/^-+|-+$/g, '') // Remove leading/trailing hyphens
    || '';
} 