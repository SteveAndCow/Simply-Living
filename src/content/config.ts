import { defineCollection, z } from 'astro:content';

const projectsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    // Basic Info
    title: z.string(),
    client: z.string(),
    date: z.date(),

    // Media
    heroVideo: z.string(), // Cloudinary public_id for short teaser video (<30s)
    thumbnail: z.string(), // Cloudinary public_id for grid thumbnail
    thumbnailGif: z.string().optional(), // Cloudinary public_id for hover animation
    gallery: z.array(z.string()).optional(), // Array of Cloudinary public_ids for process images

    // Content
    description: z.string(), // Short description, 2-3 sentences
    credits: z.array(
      z.object({
        role: z.string(), // e.g., "Director", "DP", "Editor"
        name: z.string(),
      })
    ),

    // External Links
    externalVideoUrl: z.string().url().optional(), // Full YouTube/Vimeo link
    externalVideoEmbed: z.string().url().optional(), // Embed URL if different

    // Meta
    featured: z.boolean().default(false), // Shows in hero carousel
    category: z.enum(['music-video', 'brand', 'commercial']),
    services: z.array(z.string()), // e.g., ['direction', 'cinematography', 'editing']
  }),
});

export const collections = {
  projects: projectsCollection,
};
