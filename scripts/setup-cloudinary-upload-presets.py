#!/usr/bin/env python3
"""Create or update Simply Living Cloudinary upload presets.

Requires CLOUDINARY_URL in the environment.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from typing import Any


def relaunch_with_cloudinary_sdk() -> None:
    try:
        import cloudinary  # noqa: F401
        import cloudinary.api  # noqa: F401
        return
    except ImportError:
        pass

    pipx_python = os.path.expanduser("~/.local/pipx/venvs/cloudinary-cli/bin/python")
    if os.path.exists(pipx_python) and os.path.abspath(sys.executable) != pipx_python:
        os.execv(pipx_python, [pipx_python, *sys.argv])

    if shutil.which("pipx"):
        print(
            "Cloudinary SDK is not importable. Install the CLI with: "
            "pipx install cloudinary-cli",
            file=sys.stderr,
        )
    else:
        print(
            "Cloudinary SDK is not importable and pipx is not on PATH. Install with: "
            "brew install pipx && pipx install cloudinary-cli",
            file=sys.stderr,
        )
    sys.exit(1)


def load_launchctl_env() -> None:
    if os.environ.get("CLOUDINARY_URL") or not shutil.which("launchctl"):
        return

    result = subprocess.run(
        ["launchctl", "getenv", "CLOUDINARY_URL"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    value = result.stdout.strip()
    if value:
        os.environ["CLOUDINARY_URL"] = value


def upsert_upload_preset(name: str, options: dict[str, Any]) -> None:
    import cloudinary.api
    from cloudinary.exceptions import NotFound

    try:
        cloudinary.api.upload_preset(name)
        cloudinary.api.update_upload_preset(name, **options)
        print(f"Updated upload preset: {name}")
    except NotFound:
        cloudinary.api.create_upload_preset(name=name, **options)
        print(f"Created upload preset: {name}")


def main() -> int:
    load_launchctl_env()
    if not os.environ.get("CLOUDINARY_URL"):
        print(
            "CLOUDINARY_URL is not set in this shell. Export it first, or set it "
            "with launchctl, then rerun this script.",
            file=sys.stderr,
        )
        return 1

    relaunch_with_cloudinary_sdk()

    common_options: dict[str, Any] = {
        "unsigned": False,
        "use_filename": True,
        "unique_filename": False,
        "use_asset_folder_as_public_id_prefix": True,
        "use_filename_as_display_name": True,
        "overwrite": True,
        "tags": ["simply-living"],
    }

    upsert_upload_preset(
        "simply_living_images",
        {
            **common_options,
            "allowed_formats": ["jpg", "jpeg", "png", "webp", "avif"],
            "transformation": [
                {
                    "crop": "limit",
                    "width": 2500,
                    "height": 2500,
                    "quality": "auto:eco",
                }
            ],
        },
    )
    upsert_upload_preset(
        "simply_living_videos",
        {
            **common_options,
            "allowed_formats": ["mp4", "mov", "m4v", "webm"],
            "transformation": [
                {
                    "crop": "limit",
                    "width": 1920,
                    "height": 1080,
                    "quality": "auto:eco",
                    "video_codec": "auto",
                    "fetch_format": "mp4",
                }
            ],
        },
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
