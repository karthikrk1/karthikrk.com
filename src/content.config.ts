import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// Each project case study is one .md or .mdx file in src/content/projects/.
// The file name becomes the URL: payments-risk-warehouse.mdx -> /projects/payments-risk-warehouse/
const projects = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/projects' }),
  schema: z.object({
    title: z.string(),
    summary: z.string(),
    date: z.coerce.date(),
    tags: z.array(z.string()).default([]),
    repo: z.string().url().optional(),
    featured: z.boolean().default(false),
    // Lower numbers sort first.
    order: z.number().default(100),
    // Drafts show up in `npm run dev` but are left out of the production build.
    draft: z.boolean().default(false),
  }),
});

export const collections = { projects };
