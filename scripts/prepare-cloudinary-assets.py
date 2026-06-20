#!/usr/bin/env python3
"""Prepare local/Dropbox assets for Cloudinary free-tier uploads.

The script preserves the source folder structure, writes optimized copies to a separate
output folder, and leaves originals untouched.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".tif", ".tiff"}
VIDEO_EXTENSIONS = {".mov", ".mp4", ".m4v", ".webm"}

IMAGE_LIMIT_BYTES = 9_500_000
VIDEO_LIMIT_BYTES = 95_000_000

PROJECT_SLUG_HINTS = {
    "lady": "lady",
    "sun-kissed": "sunkissed",
    "sunkissed": "sunkissed",
    "heaven": "heaven",
    "one call": "one-call",
    "onecall": "one-call",
}


def run(command: list[str]) -> None:
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def ffmpeg_available() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("ffmpeg is required. Install with: brew install ffmpeg", file=sys.stderr)
        raise SystemExit(1)
    return ffmpeg


def size_mb(path: Path) -> float:
    return path.stat().st_size / 1_000_000


def slugify(value: str) -> str:
    normalized = value.lower().replace("&", " and ")
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    return normalized.strip("-")


def project_slug(folder_name: str) -> str:
    lower = folder_name.lower()
    for hint, slug in PROJECT_SLUG_HINTS.items():
        if hint in lower:
            return slug
    return slugify(folder_name.split(" - ")[0])


def public_id_for(project: str, media_type: str, sequence: int) -> str:
    section = "gallery" if media_type == "image" else "bts"
    return f"simply-living/projects/{project}/{section}/{sequence:02d}"


def output_path_for(output: Path, project: str, media_type: str, sequence: int) -> Path:
    preset_root = "images" if media_type == "image" else "videos"
    extension = ".jpg" if media_type == "image" else ".mp4"
    return output / preset_root / f"{public_id_for(project, media_type, sequence)}{extension}"


def optimize_image(ffmpeg: str, source: Path, destination: Path) -> bool:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_suffix(".tmp.jpg")
    qualities = [3, 5, 8, 12, 18, 24, 30]
    dimensions = [2500, 2200, 1800, 1400, 1100]

    for dimension in dimensions:
        for quality in qualities:
            if temp.exists():
                temp.unlink()
            vf = (
                f"scale='min({dimension},iw)':'min({dimension},ih)':"
                "force_original_aspect_ratio=decrease"
            )
            command = [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(source),
                "-vf",
                vf,
                "-frames:v",
                "1",
                "-q:v",
                str(quality),
                str(temp),
            ]
            try:
                run(command)
            except subprocess.CalledProcessError as error:
                print(f"Image failed: {source} ({error.stderr.decode(errors='ignore').strip()})")
                return False

            if temp.exists() and temp.stat().st_size <= IMAGE_LIMIT_BYTES:
                temp.replace(destination)
                print(f"image {source} -> {destination} ({size_mb(destination):.1f} MB)")
                return True

    if temp.exists():
        temp.replace(destination)
    print(
        f"image still over target: {destination} ({size_mb(destination):.1f} MB). "
        "Review manually before uploading."
    )
    return destination.exists() and destination.stat().st_size <= IMAGE_LIMIT_BYTES


def optimize_video(ffmpeg: str, source: Path, destination: Path) -> bool:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_suffix(".tmp.mp4")
    crfs = [23, 27, 31, 35, 39]
    boxes = [(1920, 1080), (1600, 900), (1280, 720), (960, 540)]

    for width, height in boxes:
        for crf in crfs:
            if temp.exists():
                temp.unlink()
            vf = (
                f"scale='min({width},iw)':'min({height},ih)':"
                "force_original_aspect_ratio=decrease,"
                "scale=trunc(iw/2)*2:trunc(ih/2)*2"
            )
            command = [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(source),
                "-vf",
                vf,
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                str(crf),
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-movflags",
                "+faststart",
                str(temp),
            ]
            try:
                run(command)
            except subprocess.CalledProcessError as error:
                print(f"Video failed: {source} ({error.stderr.decode(errors='ignore').strip()})")
                return False

            if temp.exists() and temp.stat().st_size <= VIDEO_LIMIT_BYTES:
                temp.replace(destination)
                print(f"video {source} -> {destination} ({size_mb(destination):.1f} MB)")
                return True

    if temp.exists():
        temp.replace(destination)
    print(
        f"video still over target: {destination} ({size_mb(destination):.1f} MB). "
        "Use YouTube/Vimeo or trim the source before uploading to Cloudinary."
    )
    return destination.exists() and destination.stat().st_size <= VIDEO_LIMIT_BYTES


def iter_assets(source: Path) -> list[Path]:
    paths: list[Path] = []
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        if path.name.startswith(".") or path.name.startswith("._"):
            continue
        if path.suffix.lower() in IMAGE_EXTENSIONS | VIDEO_EXTENSIONS:
            paths.append(path)
    return sorted(paths)


def build_asset_plan(source: Path) -> list[dict[str, object]]:
    plan: list[dict[str, object]] = []
    project_dirs = sorted([path for path in source.iterdir() if path.is_dir()])
    if not project_dirs:
        project_dirs = [source]

    for project_dir in project_dirs:
        slug = project_slug(project_dir.name)
        image_sequence = 1
        video_sequence = 1

        for asset in iter_assets(project_dir):
            suffix = asset.suffix.lower()
            if suffix in IMAGE_EXTENSIONS:
                media_type = "image"
                sequence = image_sequence
                image_sequence += 1
                preset = "simply_living_images"
            elif suffix in VIDEO_EXTENSIONS:
                media_type = "video"
                sequence = video_sequence
                video_sequence += 1
                preset = "simply_living_videos"
            else:
                continue

            public_id = public_id_for(slug, media_type, sequence)
            plan.append(
                {
                    "source": asset,
                    "project_folder": project_dir.name,
                    "project_slug": slug,
                    "media_type": media_type,
                    "sequence": sequence,
                    "public_id": public_id,
                    "upload_preset": preset,
                }
            )

    return plan


def write_manifest(output: Path, rows: list[dict[str, object]]) -> None:
    manifest = output / "manifest.csv"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "status",
        "project_folder",
        "project_slug",
        "media_type",
        "sequence",
        "source",
        "source_size_mb",
        "output",
        "output_size_mb",
        "public_id",
        "upload_preset",
    ]
    with manifest.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare upload-ready Cloudinary assets.")
    parser.add_argument("source", type=Path, help="Source folder, such as a local Dropbox folder")
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        default=Path("output/cloudinary-upload-ready"),
        help="Output folder for optimized copies",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write the planned manifest without compressing files",
    )
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    output = args.output.expanduser().resolve()

    if not source.is_dir():
        print(f"Source folder does not exist: {source}", file=sys.stderr)
        return 1

    ffmpeg = ffmpeg_available()
    plan = build_asset_plan(source)
    if not plan:
        print(f"No supported image/video assets found under {source}")
        return 0

    if args.dry_run:
        manifest_rows = []
        for item in plan:
            asset = item["source"]
            assert isinstance(asset, Path)
            media_type = item["media_type"]
            assert isinstance(media_type, str)
            project = item["project_slug"]
            assert isinstance(project, str)
            sequence = item["sequence"]
            assert isinstance(sequence, int)
            destination = output_path_for(output, project, media_type, sequence)
            manifest_rows.append(
                {
                    "status": "planned",
                    "project_folder": item["project_folder"],
                    "project_slug": project,
                    "media_type": media_type,
                    "sequence": f"{sequence:02d}",
                    "source": str(asset),
                    "source_size_mb": f"{size_mb(asset):.2f}",
                    "output": str(destination),
                    "output_size_mb": "",
                    "public_id": item["public_id"],
                    "upload_preset": item["upload_preset"],
                }
            )
        write_manifest(output, manifest_rows)
        print(f"Dry run complete. Planned {len(manifest_rows)} asset(s).")
        print(f"Manifest: {output / 'manifest.csv'}")
        return 0

    failures = 0
    manifest_rows: list[dict[str, object]] = []
    for item in plan:
        asset = item["source"]
        assert isinstance(asset, Path)
        media_type = item["media_type"]
        assert isinstance(media_type, str)
        project = item["project_slug"]
        assert isinstance(project, str)
        sequence = item["sequence"]
        assert isinstance(sequence, int)
        destination = output_path_for(output, project, media_type, sequence)

        if media_type == "image":
            ok = optimize_image(ffmpeg, asset, destination)
        elif media_type == "video":
            ok = optimize_video(ffmpeg, asset, destination)
        else:
            continue

        failures += 0 if ok else 1
        manifest_rows.append(
            {
                "status": "ready" if ok else "review",
                "project_folder": item["project_folder"],
                "project_slug": project,
                "media_type": media_type,
                "sequence": f"{sequence:02d}",
                "source": str(asset),
                "source_size_mb": f"{size_mb(asset):.2f}",
                "output": str(destination) if destination.exists() else "",
                "output_size_mb": f"{size_mb(destination):.2f}" if destination.exists() else "",
                "public_id": item["public_id"],
                "upload_preset": item["upload_preset"],
            }
        )

    write_manifest(output, manifest_rows)
    print(f"Done. Upload-ready folder: {output}")
    print(f"Manifest: {output / 'manifest.csv'}")
    if failures:
        print(f"{failures} file(s) still need manual review before Cloudinary upload.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
