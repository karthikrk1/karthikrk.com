# karthikrk.com

Source for [karthikrk.com](https://karthikrk.com), my personal site: a short intro, project case studies and my résumé.

Built with [Astro](https://astro.build) as a fully static site (no client-side JavaScript), with MDX for case studies and an automatic sitemap.

## Run it locally

Requires Node 22 or later.

```sh
npm install
npm run dev       # http://localhost:4321
npm run build     # production build to ./dist/
npm run preview   # serve ./dist/ locally
```

## Where things live

```text
src/
├── site.ts                 # name, role, description, résumé path, social links
├── layouts/Base.astro      # page shell: <head> tags, header, nav, footer
├── pages/
│   ├── index.astro         # home: intro, featured projects, experience
│   ├── projects/index.astro
│   ├── projects/[slug].astro  # one page per case study
│   └── 404.astro
├── content.config.ts       # schema for project case studies
├── content/projects/       # one .md/.mdx file per case study
├── lib/projects.ts         # loads and sorts case studies
└── styles/global.css
public/                     # served as-is: résumé PDF, icons, social preview image
```

- **Your details** (name, role, links): edit `src/site.ts`.
- **Experience list:** edit the `experience` array in `src/pages/index.astro`.
- **Résumé:** replace `public/resume.pdf`.

## Adding a case study

Create `src/content/projects/<slug>.mdx`. The file name becomes the URL (`/projects/<slug>/`).

```yaml
---
title: My project
summary: One sentence shown on cards and in search results.
date: 2026-10-01
tags: [dbt, SQL]
repo: https://github.com/karthikrk1/my-project   # optional
featured: true    # show on the home page (up to 3)
order: 1          # lower sorts first
draft: true       # visible in `npm run dev`, left out of the live site
---
```

Set `draft: false` when it's ready to publish. Images go in `public/images/` and are referenced as `/images/<file>`.

## Deploy

Pushing to `main` runs `.github/workflows/deploy.yml`:
1. builds the site;
2. syncs `dist/` to S3, with long-lived caching for hashed assets in `_astro/` and 5-minute caching for everything else;
3. clears the CloudFront cache.

It can also be run by hand from the Actions tab. It needs these repository secrets: `AWS_ROLE_ARN` (assumed through GitHub OIDC), `S3_BUCKET` and `CLOUDFRONT_DISTRIBUTION_ID`.
