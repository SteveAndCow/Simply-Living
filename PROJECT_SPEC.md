# Simply Living Studios — Website Specification

> **Purpose**: This document is the source of truth for scaffolding and building the portfolio website. Claude Code should reference this for all design, structure, and technical decisions.

---

## 1. Overview

**Client**: Simply Living Studios  
**Type**: Video production and creative agency portfolio  
**Primary Work**: Music videos, clothing brand shoots (expanding to commercial)  
**Goal**: Showcase work with media-first presentation, smooth interactions, fast loading

---

## 2. Design Direction

### Color Palette
| Role | Value |
|------|-------|
| Background | `#000000` (black) |
| Primary text | `#FFFFFF` (white) |
| Secondary/muted | `#888888` or similar gray |
| Accents | White only — no additional colors |

### Typography
| Use | Font | Notes |
|-----|------|-------|
| Body copy, navigation, credits | Helvetica Neue / Helvetica / Arial | System stack fallback |
| Stylized headings, logo treatments | Cursive/script font | Suggest: Playfair Display, or find a distinctive script. Keep usage minimal. |

```css
/* Font stack suggestion */
--font-body: 'Helvetica Neue', Helvetica, Arial, sans-serif;
--font-display: 'Playfair Display', Georgia, serif; /* or chosen script */
```

### Overall Vibe
- **Editorial yet minimal** — content is the star
- Media (video, images) should dominate; UI should recede
- Smooth, intentional animations — not flashy
- Dark, cinematic feel befitting a video production studio

### Reference Sites

**A24 Films** (https://a24films.com/)
- Full-viewport hero carousel with featured projects
- Large cinematic imagery
- Minimal navigation, content-forward
- Project titles overlaid on imagery

**Junkie Studio** (https://junkie.studio/)
- Clean project list with hover states
- Individual project pages with:
  - Looping short clips
  - Breakdown of creative vision
  - Minimal text, visual-first
- Dark aesthetic, Toronto-based creative agency (same city context)

---

## 3. Site Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                         SITE MAP                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  HOME (single-page scroll experience)                          │
│  ├── Hero Section (A24-style carousel of featured works)       │
│  ├── About Teaser (brief intro, link to full about)            │
│  └── Contact CTA (shortcut to contact form)                    │
│                                                                 │
│  WORK (accessed via sidebar or defined section)                │
│  └── Project Grid (all projects, filterable later)             │
│                                                                 │
│  PROJECT PAGE (dynamic, one per project)                       │
│  ├── Hero video (short teaser, loops)                          │
│  ├── Project info (title, client, date, description)           │
│  ├── Process gallery (images)                                  │
│  ├── Credits (full crew list)                                  │
│  └── External link (YouTube/Vimeo for full video)              │
│                                                                 │
│  ABOUT                                                          │
│  ├── Studio story                                               │
│  ├── Team bios (3 people)                                       │
│  └── Client logos                                               │
│                                                                 │
│  CONTACT                                                        │
│  ├── Inquiry form (submits to email)                           │
│  └── Social links (Instagram primarily)                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Navigation
- **Collapsible sidebar** that acts as quick navigator
- Scrolling down the home page progresses through all main sections naturally
- Sidebar can jump to sections or pages
- Mobile: hamburger menu that reveals sidebar

---

## 4. Project Content Structure

### Content Collection Schema

```yaml
# src/content/config.ts schema
project:
  title: string (required)
  client: string (required)
  date: date (required)
  slug: string (auto from filename)
  
  # Media
  heroVideo: string (required) # Cloudinary public_id, short teaser <30s
  thumbnail: string (required) # Cloudinary public_id, for grid
  thumbnailGif: string (optional) # Cloudinary public_id, plays on hover
  gallery: array of strings (optional) # Cloudinary public_ids
  
  # Content
  description: string (short, 2-3 sentences)
  credits: array of { role: string, name: string }
  
  # External
  externalVideoUrl: string (optional) # Full YouTube/Vimeo link
  externalVideoEmbed: string (optional) # Embed URL if different
  
  # Meta
  featured: boolean (default: false) # Shows in hero carousel
  category: enum ['music-video', 'brand', 'commercial'] # For future filtering
  services: array of strings # e.g., ['direction', 'cinematography', 'editing']
```

### Example Project File

```mdx
---
title: "Midnight Drive"
client: "Artist Name"
date: 2024-06-15
heroVideo: "projects/midnight-drive/teaser"
thumbnail: "projects/midnight-drive/thumb"
thumbnailGif: "projects/midnight-drive/hover"
gallery:
  - "projects/midnight-drive/bts-01"
  - "projects/midnight-drive/bts-02"
  - "projects/midnight-drive/bts-03"
description: "A nocturnal visual journey through the city. Shot over three nights in downtown Toronto."
credits:
  - { role: "Director", name: "Name" }
  - { role: "DP", name: "Name" }
  - { role: "Editor", name: "Name" }
  - { role: "Colorist", name: "Name" }
externalVideoUrl: "https://www.youtube.com/watch?v=XXXXX"
featured: true
category: "music-video"
services: ["direction", "cinematography", "editing", "color"]
---

Optional extended description or story in markdown...
```

---

## 5. Key Interactions

| Interaction | Location | Implementation |
|-------------|----------|----------------|
| Video plays on hover | Work grid thumbnails | Svelte component, swap img→video on mouseenter |
| Video plays on scroll | Hero teasers, project pages | Intersection Observer, play when >50% visible |
| Smooth scroll | All sections | CSS `scroll-behavior: smooth` + JS for nav |
| Slide page transitions | Between pages | Svelte transitions or View Transitions API |
| Parallax | Text/media split sections | CSS transforms on scroll, subtle (10-20px) |

### Animation Guidelines
- **Timing**: 300-500ms for UI, 600-800ms for reveals
- **Easing**: `cubic-bezier(0.4, 0, 0.2, 1)` (ease-out) for most
- **Reveals**: Fade up (opacity + translateY) on scroll into view
- **Keep it subtle**: Animations should feel smooth, not attention-grabbing

---

## 6. Technical Stack

| Layer | Choice | Config Notes |
|-------|--------|--------------|
| Framework | Astro | Content collections, static-first |
| Interactive | Svelte | `client:visible` default hydration |
| Styling | Vanilla CSS + Tailwind utilities | CSS variables for design tokens |
| Animations | CSS + Intersection Observer | No animation library |
| Video/Images | Cloudinary | Cloud name: `dx2hfd9cp` |
| Forms | Email submission | Formspree or similar (free tier) |
| Deployment | Cloudflare Pages | Free tier |
| Analytics | Optional GA4 | Add later if needed |

### Cloudinary Configuration

```typescript
// src/lib/cloudinary.ts
export const CLOUD_NAME = 'dx2hfd9cp';

export function imageUrl(publicId: string, options?: {
  width?: number;
  quality?: number | 'auto';
  format?: 'auto' | 'webp' | 'avif';
}) {
  const transforms = [
    options?.width && `w_${options.width}`,
    `q_${options?.quality || 'auto'}`,
    `f_${options?.format || 'auto'}`,
  ].filter(Boolean).join(',');
  
  return `https://res.cloudinary.com/${CLOUD_NAME}/image/upload/${transforms}/${publicId}`;
}

export function videoUrl(publicId: string, options?: {
  width?: number;
  quality?: number | 'auto';
  format?: 'auto' | 'mp4' | 'webm';
}) {
  const transforms = [
    options?.width && `w_${options.width}`,
    `q_${options?.quality || 'auto'}`,
    `f_${options?.format || 'auto'}`,
  ].filter(Boolean).join(',');
  
  return `https://res.cloudinary.com/${CLOUD_NAME}/video/upload/${transforms}/${publicId}`;
}

export function videoPoster(publicId: string, options?: { width?: number }) {
  // Get poster frame from video
  return `https://res.cloudinary.com/${CLOUD_NAME}/video/upload/so_0,w_${options?.width || 800},f_auto,q_auto/${publicId}.jpg`;
}
```

---

## 7. Component Architecture

### Astro Components (Static)

| Component | Purpose |
|-----------|---------|
| `BaseLayout.astro` | HTML shell, meta, fonts, global styles |
| `ProjectLayout.astro` | Layout for individual project pages |
| `Header.astro` | Logo, sidebar toggle |
| `Footer.astro` | Copyright, social links |
| `ProjectCard.astro` | Grid item with hover video swap |
| `LazyImage.astro` | Cloudinary image with blur-up placeholder |
| `LazyVideo.astro` | Video with poster, lazy load, scroll-play |
| `SEO.astro` | Meta tags, OG image |

### Svelte Components (Interactive)

| Component | Hydration | Purpose |
|-----------|-----------|---------|
| `Navigation.svelte` | `client:load` | Sidebar, mobile menu, scroll spy |
| `HeroCarousel.svelte` | `client:load` | Featured projects carousel (above fold) |
| `VideoPlayer.svelte` | `client:visible` | Full video playback with controls |
| `ProjectGrid.svelte` | `client:visible` | Grid with hover video swap |
| `ContactForm.svelte` | `client:visible` | Form with validation, submission |
| `Gallery.svelte` | `client:visible` | Image gallery with lightbox |

---

## 8. Page Specifications

### Home Page (`/`)

```
┌─────────────────────────────────────────┐
│ [Logo]                    [Menu Toggle] │  <- Fixed header
├─────────────────────────────────────────┤
│                                         │
│         HERO CAROUSEL                   │  <- 100vh, featured projects
│     (A24-style full banners)            │     Video/image backgrounds
│                                         │     Project title overlay
│      [1] [2] [3] [4] indicators         │     Click → project page
│                                         │
├─────────────────────────────────────────┤
│                                         │
│         ABOUT TEASER                    │  <- Brief studio intro
│    "We are Simply Living Studios..."    │     Link to full about
│                                         │
├─────────────────────────────────────────┤
│                                         │
│         WORK GRID                       │  <- Recent projects
│    [  ] [  ] [  ]                       │     Hover → video plays
│    [  ] [  ] [  ]                       │     Click → project page
│                                         │
├─────────────────────────────────────────┤
│                                         │
│         CONTACT CTA                     │  <- "Let's work together"
│    [Get in Touch button]                │     Links to contact form
│                                         │
├─────────────────────────────────────────┤
│         FOOTER                          │
│    © 2024 Simply Living Studios         │
│    Instagram link                       │
└─────────────────────────────────────────┘
```

### Project Page (`/work/[slug]`)

```
┌─────────────────────────────────────────┐
│         HERO VIDEO                      │  <- Teaser, loops, muted
│    (full width, 60-80vh)                │     Plays on scroll
├─────────────────────────────────────────┤
│                                         │
│  Title                     Client       │  <- Project info
│  Date                      Category     │
│                                         │
│  Description text here...               │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│         GALLERY                         │  <- Process images
│    [img] [img] [img]                    │     Parallax on scroll
│                                         │
├─────────────────────────────────────────┤
│                                         │
│         CREDITS                         │  <- Full crew list
│    Director: Name                       │
│    DP: Name                             │
│    ...                                  │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│    [Watch Full Video on YouTube →]      │  <- External link
│                                         │
├─────────────────────────────────────────┤
│         FOOTER                          │
└─────────────────────────────────────────┘
```

### About Page (`/about`)

```
┌─────────────────────────────────────────┐
│         STUDIO STORY                    │
│    Headline (cursive font)              │
│    Body text...                         │
├─────────────────────────────────────────┤
│         TEAM                            │
│    [Photo]  [Photo]  [Photo]            │
│    Name     Name     Name               │
│    Role     Role     Role               │
│    Short bio text for each             │
├─────────────────────────────────────────┤
│         CLIENTS                         │
│    [logo] [logo] [logo] [logo]          │
└─────────────────────────────────────────┘
```

### Contact Page (`/contact`)

```
┌─────────────────────────────────────────┐
│         LET'S TALK                      │
│                                         │
│    Name: [____________]                 │
│    Email: [____________]                │
│    Project Type: [dropdown]             │
│    Message: [textarea_______]           │
│                                         │
│    [Send Inquiry]                       │
│                                         │
├─────────────────────────────────────────┤
│    Or reach us at:                      │
│    hello@simplylivingstudios.com        │
│    @simplylivingstudios (Instagram)     │
└─────────────────────────────────────────┘
```

---

## 9. Project File Structure

```
simply-living-studios/
├── src/
│   ├── components/
│   │   ├── astro/
│   │   │   ├── Header.astro
│   │   │   ├── Footer.astro
│   │   │   ├── ProjectCard.astro
│   │   │   ├── LazyImage.astro
│   │   │   ├── LazyVideo.astro
│   │   │   └── SEO.astro
│   │   └── svelte/
│   │       ├── Navigation.svelte
│   │       ├── HeroCarousel.svelte
│   │       ├── VideoPlayer.svelte
│   │       ├── ProjectGrid.svelte
│   │       ├── Gallery.svelte
│   │       └── ContactForm.svelte
│   ├── layouts/
│   │   ├── BaseLayout.astro
│   │   └── ProjectLayout.astro
│   ├── pages/
│   │   ├── index.astro
│   │   ├── about.astro
│   │   ├── contact.astro
│   │   └── work/
│   │       ├── index.astro
│   │       └── [...slug].astro
│   ├── content/
│   │   ├── config.ts
│   │   └── projects/
│   │       └── (project mdx files)
│   ├── styles/
│   │   ├── global.css
│   │   ├── variables.css
│   │   └── animations.css
│   ├── lib/
│   │   ├── cloudinary.ts
│   │   └── utils.ts
│   └── assets/
│       └── (local assets: logo, etc.)
├── public/
│   ├── fonts/
│   └── favicon.svg
├── astro.config.mjs
├── tailwind.config.mjs
├── tsconfig.json
├── package.json
└── PROJECT_SPEC.md (this file)
```

---

## 10. Placeholder Content for Scaffolding

Use these placeholder projects to build out the site before real assets are ready:

### Project 1: Music Video
```yaml
title: "Neon Dreams"
client: "Synthwave Artist"
date: 2024-08-01
category: "music-video"
description: "A retro-futuristic visual journey through neon-lit streets."
featured: true
```

### Project 2: Brand Shoot
```yaml
title: "Urban Collection"
client: "Streetwear Brand"
date: 2024-06-15
category: "brand"
description: "Lookbook for the Summer 2024 capsule collection."
featured: true
```

### Project 3: Music Video
```yaml
title: "Golden Hour"
client: "R&B Artist"
date: 2024-04-20
category: "music-video"
description: "Intimate performance piece shot during magic hour."
featured: false
```

For placeholder media, use:
- Cloudinary sample videos: `samples/sea-turtle`, `samples/elephants`
- Or placeholder service: https://picsum.photos for images
- Or solid color blocks with CSS

---

## 11. Implementation Phases

### Phase 1: Foundation (Do First)
1. Initialize Astro + Svelte + Tailwind
2. Set up CSS variables and global styles
3. Create BaseLayout with dark theme
4. Configure content collections schema
5. Set up Cloudinary helper functions

### Phase 2: Core Pages
1. Home page structure (without carousel functionality)
2. Basic project page template
3. About page
4. Contact page with form

### Phase 3: Components
1. Navigation/sidebar
2. Hero carousel (Svelte)
3. Project grid with hover states
4. Lazy video/image components
5. Contact form with validation

### Phase 4: Interactions
1. Scroll-triggered video playback
2. Page transitions
3. Parallax effects
4. Reveal animations

### Phase 5: Polish & Deploy
1. SEO and meta tags
2. Performance audit
3. Cloudflare Pages deployment
4. Real content integration

---

## 12. Notes for Claude Code

- **Don't wait for assets**: Build everything with placeholders first
- **Mobile-first**: Design for mobile, enhance for desktop
- **Performance budget**: Aim for <3s LCP, no layout shift
- **Accessibility**: Semantic HTML, ARIA where needed, keyboard nav
- **Keep it simple**: Fewer dependencies = easier maintenance
- When in doubt, reference the design direction and reference sites

---

*Last updated: January 2025*
