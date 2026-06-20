# Cloudinary Asset Setup

This site uses Cloudinary for media delivery and Astro content files for project data.
Cloudinary should own the asset files. The project markdown files should reference those
assets by stable Cloudinary public ID.

## Current Integration

- Cloud name: `dx2hfd9cp`
- URL helpers: `src/lib/cloudinary.ts`
- Project content: `src/content/projects/*.md`
- Public ID format in content files: no file extension, for example `projects/lady/hero`

The app does not query Cloudinary at build time. Every asset that appears on the site must
be referenced explicitly from a project content file.

## Recommended Cloudinary Folder Structure

Use one root folder for the portfolio so placeholder/sample assets are easy to separate
from production assets:

```text
simply-living/
  projects/
    lady/
      hero.mp4
      full.mp4
      thumb.jpg
      hover.mp4
      gallery/
        01.jpg
        02.jpg
      bts/
        01.mp4
        02.jpg
    sunkissed/
      hero.mp4
      full.mp4
      thumb.jpg
      hover.mp4
      gallery/
      bts/
    heaven/
      hero.mp4
      full.mp4
      thumb.jpg
      hover.mp4
      gallery/
      bts/
    one-call/
      hero.mp4
      full.mp4
      thumb.jpg
      hover.mp4
      gallery/
      bts/
  brand/
    logo-white.svg
    logo-mark.svg
placeholders/
  video-placeholder.mp4
  image-placeholder.jpg
```

Use these public IDs in content:

```yaml
heroVideo: "simply-living/projects/lady/hero"
fullVideo: "simply-living/projects/lady/full"
thumbnail: "simply-living/projects/lady/thumb"
thumbnailGif: "simply-living/projects/lady/hover"
gallery:
  - "simply-living/projects/lady/gallery/01"
  - "simply-living/projects/lady/gallery/02"
btsMedia:
  - { type: "video", id: "simply-living/projects/lady/bts/01", alt: "Behind the scenes clip from Lady", layout: "wide" }
```

Keep placeholder assets under the top-level `placeholders/` folder, outside
`simply-living/`. Do not mix placeholders into project folders unless the placeholder is
intentionally standing in for a specific missing asset and is named clearly, for example
`missing-thumb`.

## Naming Rules

- Use lowercase kebab-case for project folders and filenames.
- Keep public IDs stable after publishing. Renaming a public ID changes the delivery URL.
- Do not include file extensions in Astro content IDs.
- Use fixed role names for files that the site expects: `hero`, `full`, `thumb`, `hover`.
- Use numbered filenames for ordered media: `01`, `02`, `03`.
- Avoid duplicate filenames in different project folders unless your Cloudinary upload
  preset preserves the folder path in the public ID.

## Dropbox Workflow

Do not upload raw Dropbox files directly if they might exceed the Cloudinary account upload
limits. Cloudinary applies upload-size limits to the original file before incoming
transformations run.

Use this workflow instead:

1. Pick assets from Dropbox into a local source folder.
2. Run the local compression script.
3. Upload the optimized output folder to Cloudinary.

Cloudinary CLI can sync a local folder to Cloudinary, including a Dropbox folder, but the
Dropbox files must physically exist on disk. Online-only Dropbox files will not upload.

Suggested local Dropbox folder:

```text
~/Dropbox/Simply Living Cloudinary/simply-living/
```

Keep the Dropbox folder structure identical to the Cloudinary structure above.

Before syncing, make the folder available offline in Dropbox:

1. In Finder, right-click the `Simply Living Cloudinary` folder.
2. Select `Make Available Offline`.
3. Wait for Dropbox to finish downloading all files locally.

Prepare upload-ready copies:

```sh
./scripts/prepare-cloudinary-assets.py \
  /Users/stephencao/Downloads/SL_SITE_ASSETS \
  output/cloudinary-upload-ready
```

The script:

- Treats each top-level folder as a project.
- Normalizes known project slugs such as `Lady` -> `lady`, `SUN-KISSED` ->
  `sunkissed`, and `One Call` -> `one-call`.
- Writes images under `output/cloudinary-upload-ready/images/simply-living/...`.
- Writes videos under `output/cloudinary-upload-ready/videos/simply-living/...`.
- Converts images to upload-ready JPEG files under 9.5 MB when possible.
- Converts videos to upload-ready MP4 files under 95 MB when possible.
- Writes `output/cloudinary-upload-ready/manifest.csv` with the original source file,
  generated public ID, output file, and required upload preset.
- Leaves the original Dropbox files untouched.

If a full-length video still cannot fit under the target, host it on YouTube/Vimeo and use
Cloudinary only for the teaser, thumbnail, hover clip, gallery, and BTS media.

Upload prepared assets in two batches:

```sh
cld sync --push \
  output/cloudinary-upload-ready/images/simply-living \
  simply-living \
  -K \
  -o upload_preset simply_living_images

cld sync --push \
  output/cloudinary-upload-ready/videos/simply-living \
  simply-living \
  -K \
  -o upload_preset simply_living_videos
```

Use the image preset only for the `images/` root and the video preset only for the
`videos/` root.

## CLI Setup

The Cloudinary CLI is the best local tool for this project because it can upload folders,
sync folders, list assets, and call Admin/Upload API methods from the terminal.

Install:

```sh
brew install pipx
pipx install cloudinary-cli
```

Use `pipx` instead of `pip3 install cloudinary-cli` on Homebrew-managed macOS Python
installations. Homebrew marks its Python environment as externally managed, so direct
system-wide `pip` installs can fail with the PEP 668 `externally-managed-environment`
error.

Configure for the current shell session:

```sh
export CLOUDINARY_URL='cloudinary://<api_key>:<api_secret>@dx2hfd9cp'
```

Get the real value from Cloudinary Console settings. Do not commit it to this repo and do
not paste it into public logs.

Verify:

```sh
cld --version
cld config
```

This machine is not currently configured for direct Cloudinary access unless `cld` is
installed and `CLOUDINARY_URL` is set.

## Upload Preset

Create two signed upload presets so image uploads and video uploads can use different
incoming transformations:

- `simply_living_images`
- `simply_living_videos`

You can create or update them from this repo:

```sh
./scripts/setup-cloudinary-upload-presets.py
```

Recommended preset behavior:

- Use the uploaded filename as the public ID.
- Do not append a random unique suffix.
- Preserve the initial asset folder path in the public ID if the Cloudinary environment uses
  dynamic folders.
- Allow overwrite only for trusted signed uploads.
- Add a default tag such as `simply-living`.

Recommended image preset:

- Allowed formats: `jpg,jpeg,png,webp,avif`
- Incoming transformation: `c_limit,w_2500,h_2500,q_auto:eco`

Recommended video preset:

- Allowed formats: `mp4,mov,m4v,webm`
- Incoming transformation: `c_limit,w_1920,h_1080,q_auto:eco,vc_auto,f_mp4`

When creating presets with the Python SDK, pass incoming transformations as structured
options, not as a raw string. A raw string is interpreted as a named transformation.

Cloudinary account upload limits still apply to the original Dropbox file. Incoming
transformations can reduce the stored asset after upload, but they do not make an original
image over the account's image upload limit, or an original video over the account's video
upload limit, uploadable.

For free-tier discipline:

- Pre-compress source images locally before upload if they are over the account image upload
  limit. The preset cannot fix an image Cloudinary rejects before upload.
- Pre-compress videos locally before upload if they are over the account video upload limit.
- Prefer Cloudinary for short teasers, hover clips, gallery media, and BTS clips.
- Prefer YouTube or Vimeo for full-length music videos unless the final encoded file is
  comfortably under the account video upload limit.
- If the Upload Preset UI exposes `Max file size`, set the image preset to the account image
  limit and the video preset to the account video limit. This rejects oversize files early,
  but it does not compress them before upload.

The important outcome is that a file at:

```text
simply-living/projects/lady/hero.mp4
```

gets a public ID like:

```text
simply-living/projects/lady/hero
```

If Cloudinary is in dynamic folder mode and the preset does not prepend the asset folder to
the public ID, the Media Library folder can look correct while the delivery public ID is
only `hero`, which will not match this site's content files.

## Sync Commands

Create the Cloudinary folder scaffold:

```sh
./scripts/setup-cloudinary-folders.sh
```

Preview the source folder first:

```sh
find "$HOME/Dropbox/Simply Living Cloudinary/simply-living" -maxdepth 4 -type f | sort
```

Push Dropbox assets to Cloudinary:

```sh
cld sync --push \
  "$HOME/Dropbox/Simply Living Cloudinary/simply-living" \
  simply-living \
  -o upload_preset simply_living_images \
  -o tags simply-living
```

Safer first run when you do not want the CLI to delete remote-only files:

```sh
cld sync --push \
  "$HOME/Dropbox/Simply Living Cloudinary/simply-living" \
  simply-living \
  -K \
  -o upload_preset simply_living_images \
  -o tags simply-living
```

Use `-K` while the structure is still being cleaned up. Remove it only when the Dropbox
folder is intentionally the complete source of truth for that Cloudinary folder.

Pull Cloudinary assets back to Dropbox:

```sh
cld sync --pull \
  "$HOME/Dropbox/Simply Living Cloudinary/simply-living" \
  simply-living
```

List assets after upload:

```sh
cld search 'folder:simply-living/* OR asset_folder:simply-living/*'
```

## Updating Project Content

After uploading assets, update the matching project markdown file:

```yaml
heroVideo: "simply-living/projects/lady/hero"
fullVideo: "simply-living/projects/lady/full"
thumbnail: "simply-living/projects/lady/thumb"
thumbnailGif: "simply-living/projects/lady/hover"
```

Then run:

```sh
npm run build
```

If an asset does not render, check these first:

- The public ID in Cloudinary exactly matches the content file.
- The content ID does not include a file extension.
- The resource type is correct: videos must be Cloudinary video assets, images must be image assets.
- The asset is not restricted/private.
- The upload preset did not append a random suffix to the public ID.

## Structured Metadata

You do not need structured metadata for the site to work. The Astro content collection
already stores project title, client, date, category, services, credits, descriptions, and
site layout choices.

Use Cloudinary structured metadata only if the Media Library needs better search, review,
rights, or workflow management outside the codebase.

Recommended minimal fields if you want DAM-style organization:

| Field label | External ID | Type | Purpose |
| --- | --- | --- | --- |
| Project slug | `project_slug` | Text or enum | Connect assets to `src/content/projects/<slug>.md` |
| Asset role | `asset_role` | Enum | `hero`, `full`, `thumbnail`, `hover`, `gallery`, `bts`, `brand`, `placeholder` |
| Publish status | `publish_status` | Enum | `draft`, `review`, `approved`, `archived` |
| Rights status | `rights_status` | Enum | `unknown`, `cleared`, `restricted`, `expired` |
| Credit | `credit` | Text | Photographer, DP, editor, or source note |
| Project date | `project_date` | Date | Useful for sorting/filtering in Cloudinary |

Do not duplicate all Astro project fields into Cloudinary. That creates two sources of
truth. Keep site rendering data in markdown, and use Cloudinary metadata for asset-library
operations.

## Can Codex Interact With Cloudinary?

Yes, once credentials are configured locally. The practical options are:

- Cloudinary CLI with `CLOUDINARY_URL`, best for listing, syncing, uploading, and metadata checks.
- Cloudinary Admin/Upload REST APIs, useful for scripted setup or metadata-field creation.
- Cloudinary SDKs, useful if this repo later needs build-time automation.

Codex should not receive or store Cloudinary secrets in committed files. For a one-off
session, export `CLOUDINARY_URL` in the shell or provide a temporary credential through a
safe local secret mechanism, then ask Codex to run read-only checks or a specific upload.

Before Codex changes the Cloudinary account, confirm the exact operation, target folder,
and whether deletion/overwrite is allowed.
