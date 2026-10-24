import { getCollection, type CollectionEntry } from 'astro:content';

export type Project = CollectionEntry<'projects'>;

/** Published projects, sorted by `order` then newest first. Drafts are included only in dev. */
export async function getProjects(): Promise<Project[]> {
  const projects = await getCollection('projects', ({ data }) =>
    import.meta.env.PROD ? !data.draft : true,
  );
  return projects.sort(
    (a, b) =>
      a.data.order - b.data.order || b.data.date.getTime() - a.data.date.getTime(),
  );
}
