import { defineCollection, z } from 'astro:content';

const projectMedia = z.object({
  type: z.enum(['image', 'video']),
  id: z.string(),
  alt: z.string().optional(),
  caption: z.string().optional(),
  layout: z.enum(['small', 'medium', 'large', 'wide']).optional(),
});

const projectsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    // Basic Info
    title: z.string(),
    displayTitle: z.string().optional(),
    client: z.string(),
    date: z.date(),

    // Media
    heroVideo: z.string().optional(), // Cloudinary public_id for short teaser video (<30s)
    fullVideo: z.string().optional(), // Cloudinary public_id for the full-screen player video
    fullVideoDuration: z.number().positive().optional(), // Stable duration in seconds for custom player UI
    heroImage: z.string().optional(), // Cloudinary public_id for image-first projects
    thumbnail: z.string(), // Cloudinary public_id for grid thumbnail
    thumbnailGif: z.string().optional(), // Cloudinary public_id for hover animation
    gallery: z.array(z.string()).optional(), // Array of Cloudinary public_ids for process images
    btsMedia: z.array(projectMedia).default([]),

    // Content
    description: z.string(), // Short description, 2-3 sentences
    info: z
      .object({
        text: z.array(z.string()).default([]),
        media: z.array(projectMedia).default([]),
      })
      .optional(),
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
