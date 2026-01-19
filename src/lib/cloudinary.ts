// Cloudinary Configuration
export const CLOUD_NAME = 'dx2hfd9cp';

interface ImageOptions {
  width?: number;
  quality?: number | 'auto';
  format?: 'auto' | 'webp' | 'avif' | 'jpg' | 'png';
}

interface VideoOptions {
  width?: number;
  quality?: number | 'auto';
  format?: 'auto' | 'mp4' | 'webm';
}

/**
 * Generate optimized Cloudinary image URL
 * @param publicId - Cloudinary public ID (e.g., "projects/midnight-drive/thumb")
 * @param options - Transformation options
 * @returns Cloudinary image URL
 */
export function imageUrl(publicId: string, options?: ImageOptions): string {
  const transforms = [
    options?.width && `w_${options.width}`,
    `q_${options?.quality || 'auto'}`,
    `f_${options?.format || 'auto'}`,
  ]
    .filter(Boolean)
    .join(',');

  return `https://res.cloudinary.com/${CLOUD_NAME}/image/upload/${transforms}/${publicId}`;
}

/**
 * Generate optimized Cloudinary video URL
 * @param publicId - Cloudinary public ID (e.g., "projects/midnight-drive/teaser")
 * @param options - Transformation options
 * @returns Cloudinary video URL
 */
export function videoUrl(publicId: string, options?: VideoOptions): string {
  const transforms = [
    options?.width && `w_${options.width}`,
    `q_${options?.quality || 'auto'}`,
    `f_${options?.format || 'auto'}`,
  ]
    .filter(Boolean)
    .join(',');

  return `https://res.cloudinary.com/${CLOUD_NAME}/video/upload/${transforms}/${publicId}`;
}

/**
 * Generate poster frame (thumbnail) from Cloudinary video
 * @param publicId - Cloudinary video public ID
 * @param options - Transformation options
 * @returns Cloudinary poster image URL
 */
export function videoPoster(
  publicId: string,
  options?: { width?: number; time?: number }
): string {
  const width = options?.width || 800;
  const time = options?.time || 0; // Frame time in seconds

  return `https://res.cloudinary.com/${CLOUD_NAME}/video/upload/so_${time},w_${width},f_auto,q_auto/${publicId}.jpg`;
}

/**
 * Generate responsive image srcset for Cloudinary images
 * @param publicId - Cloudinary public ID
 * @param widths - Array of widths for srcset
 * @returns srcset string
 */
export function imageSrcSet(publicId: string, widths: number[] = [400, 800, 1200, 1600]): string {
  return widths
    .map((width) => `${imageUrl(publicId, { width })} ${width}w`)
    .join(', ');
}
