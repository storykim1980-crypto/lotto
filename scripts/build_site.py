#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build static deploy folder for Cloudflare Pages.

Only public files are copied to ./public so internal docs, updater scripts,
GitHub workflow files, and notes are not served as website assets.

빌드 내용:
  - index.html + 정책/안내 페이지 7개 (애드센스 심사 대응)
  - data/ (results.json / results.csv / last_updated.json)
  - ads.txt (Google AdSense 게시자 확인용 — 필수, 루트에 위치해야 함)
  - robots.txt / sitemap.xml / _headers
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
DOMAIN = "https://miniloto-navi.com"

# 공개할 HTML 페이지 목록 (메인 + 정책/안내)
PAGES = [
    ("index.html",      "1.0",  "weekly"),
    ("about.html",      "0.5",  "monthly"),
    ("privacy.html",    "0.4",  "yearly"),
    ("terms.html",      "0.4",  "yearly"),
    ("cookies.html",    "0.4",  "yearly"),
    ("ads-policy.html", "0.4",  "yearly"),
    ("disclaimer.html", "0.4",  "yearly"),
    ("contact.html",    "0.5",  "yearly"),
]

# Google AdSense 게시자 ID (ads.txt 는 도메인 루트 /ads.txt 로 접근 가능해야 함)
ADS_PUB_ID = "pub-3122957517118825"


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main() -> None:
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    PUBLIC.mkdir(parents=True, exist_ok=True)

    for name, _priority, _freq in PAGES:
        copy_file(ROOT / name, PUBLIC / name)

    data_src = ROOT / "data"
    data_dst = PUBLIC / "data"
    data_dst.mkdir(parents=True, exist_ok=True)
    for name in ["results.json", "results.csv", "last_updated.json"]:
        copy_file(data_src / name, data_dst / name)

    (PUBLIC / "ads.txt").write_text(
        f"google.com, {ADS_PUB_ID}, DIRECT, f08c47fec0942fa0\n",
        encoding="utf-8",
    )

    (PUBLIC / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: https://miniloto-navi.com/sitemap.xml\n",
        encoding="utf-8",
    )

    urls = "\n".join(
        f"""  <url>
    <loc>{DOMAIN}/{'' if name == 'index.html' else name}</loc>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>"""
        for name, priority, freq in PAGES
    )
    (PUBLIC / "sitemap.xml").write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
""",
        encoding="utf-8",
    )

    # Cloudflare Pages supports _headers.
    # ※ AdSense 광고 로딩에 영향을 주지 않도록 CSP는 넣지 않습니다.
    (PUBLIC / "_headers").write_text(
        """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: geolocation=(), microphone=(), camera=()

/index.html
  Cache-Control: no-cache

/ads.txt
  Content-Type: text/plain; charset=utf-8
  Cache-Control: public, max-age=86400

/data/*
  Cache-Control: no-cache, no-store, must-revalidate
""",
        encoding="utf-8",
    )

    print(f"Built {PUBLIC}")
    for p in sorted(PUBLIC.rglob('*')):
        if p.is_file():
            print(' -', p.relative_to(PUBLIC))


if __name__ == "__main__":
    main()
