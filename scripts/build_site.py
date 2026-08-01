#!/usr/bin/env python3
"""Build static deploy folder for Cloudflare Pages.

Only public files are copied to ./public so internal docs, updater scripts,
GitHub workflow files, and notes are not served as website assets.
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
DOMAIN = "https://miniloto-navi.com"


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main() -> None:
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    PUBLIC.mkdir(parents=True, exist_ok=True)

    copy_file(ROOT / "index.html", PUBLIC / "index.html")

    data_src = ROOT / "data"
    data_dst = PUBLIC / "data"
    data_dst.mkdir(parents=True, exist_ok=True)
    for name in ["results.json", "results.csv", "last_updated.json"]:
        copy_file(data_src / name, data_dst / name)

    (PUBLIC / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: https://miniloto-navi.com/sitemap.xml\n",
        encoding="utf-8",
    )

    (PUBLIC / "sitemap.xml").write_text(
        f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">
  <url>
    <loc>{DOMAIN}/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
""",
        encoding="utf-8",
    )

    # Cloudflare Pages supports _headers.
    (PUBLIC / "_headers").write_text(
        """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: geolocation=(), microphone=(), camera=()

/index.html
  Cache-Control: no-cache

/data/*
  Cache-Control: no-cache, no-store, must-revalidate
""",
        encoding="utf-8",
    )

    print(f"Built {PUBLIC}")


if __name__ == "__main__":
    main()
