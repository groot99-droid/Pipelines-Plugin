"""Assisted mode: no credentials, no API. Print what to upload and where; the human does the posting."""
from __future__ import annotations

from videoeditor.publish.package import PostPackage

UPLOAD_PAGES = {
    "youtube": "https://www.youtube.com/upload",
    "tiktok": "https://www.tiktok.com/tiktokstudio/upload",
    "instagram": "https://www.instagram.com/",
    "x": "https://x.com/compose/post",
    "linkedin": "https://www.linkedin.com/feed/",
    "bluesky": "https://bsky.app/",
    "mastodon": None,   # instance-specific
}


def checklist(pkg: PostPackage, platform: str, instance: str | None = None) -> str:
    url = UPLOAD_PAGES.get(platform) or instance or "(open your Mastodon instance)"
    v = pkg.for_platform(platform)
    lines = [
        f"== {platform}: post it yourself ==",
        f"1. Open: {url}",
        f"2. Upload: {pkg.video}",
    ]
    if v.get("title"):
        lines.append(f"3. Title: {v['title']}")
    lines.append(f"{'4' if v.get('title') else '3'}. Caption (copy below):")
    lines.append("---")
    lines.append(pkg.full_text(platform))
    lines.append("---")
    if pkg.ai_generated:
        lines.append("Note: mark this as AI-generated / synthetic if the platform asks.")
    if pkg.branded_content:
        lines.append("Note: toggle the paid-partnership / branded-content disclosure.")
    return "\n".join(lines)
