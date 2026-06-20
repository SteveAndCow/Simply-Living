#!/usr/bin/env bash
set -euo pipefail

if ! command -v cld >/dev/null 2>&1; then
  echo "Cloudinary CLI is not installed or not on PATH. Install with: brew install pipx && pipx install cloudinary-cli" >&2
  exit 1
fi

if [ -z "${CLOUDINARY_URL:-}" ] && command -v launchctl >/dev/null 2>&1; then
  launchctl_cloudinary_url="$(launchctl getenv CLOUDINARY_URL 2>/dev/null || true)"
  if [ -n "${launchctl_cloudinary_url}" ]; then
    export CLOUDINARY_URL="${launchctl_cloudinary_url}"
  fi
fi

if [ -z "${CLOUDINARY_URL:-}" ]; then
  echo "CLOUDINARY_URL is not set in this shell." >&2
  echo "Export it first, or set it with launchctl, then rerun this script." >&2
  exit 1
fi

folders=(
  "simply-living"
  "simply-living/projects"
  "simply-living/projects/lady"
  "simply-living/projects/lady/gallery"
  "simply-living/projects/lady/bts"
  "simply-living/projects/sunkissed"
  "simply-living/projects/sunkissed/gallery"
  "simply-living/projects/sunkissed/bts"
  "simply-living/projects/heaven"
  "simply-living/projects/heaven/gallery"
  "simply-living/projects/heaven/bts"
  "simply-living/projects/one-call"
  "simply-living/projects/one-call/gallery"
  "simply-living/projects/one-call/bts"
  "simply-living/brand"
  "placeholders"
)

for folder in "${folders[@]}"; do
  echo "Creating folder: ${folder}"
  output="$(cld admin create_folder "${folder}" 2>&1)" || {
    if printf '%s' "${output}" | grep -Eiq 'already|exist'; then
      echo "Already exists: ${folder}"
      continue
    fi

    printf '%s\n' "${output}" >&2
    exit 1
  }
done

echo "Done. Current top-level folders:"
cld admin root_folders
