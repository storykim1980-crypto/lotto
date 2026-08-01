#!/usr/bin/env python3
"""
Update data/results.json and data/results.csv for ミニロト分析ナビ.

Recommended use: GitHub Actions scheduled after Tuesday MiniLoto draw.
Primary target is the official Mizuho MiniLoto page. Because Mizuho may
block non-browser requests or load data dynamically, this script also supports
fallback parsing from a public result page. Always validate results before save.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
DATA_JSON = ROOT / "data" / "results.json"
DATA_CSV = ROOT / "data" / "results.csv"
META_JSON = ROOT / "data" / "last_updated.json"

MIZUHO_URL = "https://www.mizuhobank.co.jp/takarakuji/check/loto/miniloto/index.html"
# Optional private fallback source. Set it as a GitHub repository secret or environment variable.
# Keep this empty in the public repository to avoid exposing any reference source.
BACKUP_URL = os.environ.get("BACKUP_MINILOTO_URL", "").strip()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MinilotoBunsekiOuBot/1.0; +https://example.com)",
    "Accept-Language": "ja,en;q=0.8",
}


def as_int(v: Any) -> int:
    if v is None:
        return 0
    s = str(v).replace(",", "").replace("円", "").replace("口", "").strip()
    if s in {"", "該当なし", "なし", "-"}:
        return 0
    return int(s)


def load_current() -> list[dict[str, Any]]:
    if DATA_JSON.exists():
        return json.loads(DATA_JSON.read_text(encoding="utf-8"))
    return []


def validate(row: dict[str, Any]) -> None:
    nums = [int(n) for n in row["nums"]]
    bonus = int(row["bonus"])
    if len(nums) != 5:
        raise ValueError(f"main nums must be 5: {nums}")
    if len(set(nums)) != 5:
        raise ValueError(f"duplicated main nums: {nums}")
    if any(n < 1 or n > 31 for n in nums):
        raise ValueError(f"main num out of range: {nums}")
    if not (1 <= bonus <= 31):
        raise ValueError(f"bonus out of range: {bonus}")
    if bonus in nums:
        raise ValueError(f"bonus duplicated with main nums: {bonus} in {nums}")
    for key in ("winners", "prizes"):
        if key in row:
            for r in ("r1", "r2", "r3", "r4"):
                if int(row[key].get(r, 0)) < 0:
                    raise ValueError(f"negative {key}.{r}")


def normalize(row: dict[str, Any]) -> dict[str, Any]:
    out = {
        "draw": int(row["draw"]),
        "date": str(row["date"]).strip(),
        "nums": sorted([int(n) for n in row["nums"]]),
        "bonus": int(row["bonus"]),
    }
    if "winners" in row:
        out["winners"] = {f"r{i}": as_int(row["winners"].get(f"r{i}")) for i in range(1, 5)}
    if "prizes" in row:
        out["prizes"] = {f"r{i}": as_int(row["prizes"].get(f"r{i}")) for i in range(1, 5)}
    validate(out)
    return out


def fetch_url(url: str, params: dict[str, str] | None = None) -> str:
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


def parse_backup_latest() -> dict[str, Any]:
    """Parse latest row from a configured compatible public result table."""
    if not BACKUP_URL:
        raise RuntimeError("BACKUP_MINILOTO_URL is not configured")
    html = fetch_url(BACKUP_URL, {"Order[page]": "1", "Order[limit]": "100", "Order[order]": "desc"})
    pat = re.compile(
        r'<tr[^>]*>\s*<td class="right">\s*(\d+)\s*</td>\s*'
        r'<td>\s*([^<]+)\s*</td>\s*'
        r'<td>\s*(\d+)\s*</td>\s*<td>\s*(\d+)\s*</td>\s*<td>\s*(\d+)\s*</td>\s*<td>\s*(\d+)\s*</td>\s*<td>\s*(\d+)\s*</td>\s*'
        r'<td>\s*(\d+)\s*</td>\s*'
        r'<td class="right">\s*([\d,]+)\s*</td>\s*<td class="right">\s*([\d,]+)\s*</td>\s*<td class="right">\s*([\d,]+)\s*</td>\s*<td class="right">\s*([\d,]+)\s*</td>\s*'
        r'<td class="right">\s*([\d,]+)\s*</td>\s*<td class="right">\s*([\d,]+)\s*</td>\s*<td class="right">\s*([\d,]+)\s*</td>\s*<td class="right">\s*([\d,]+)\s*</td>\s*</tr>',
        re.S,
    )
    m = pat.search(html)
    if not m:
        raise RuntimeError("backup source latest row not found")
    g = m.groups()
    row = {
        "draw": int(g[0]),
        "date": g[1].strip(),
        "nums": [int(x) for x in g[2:7]],
        "bonus": int(g[7]),
        "winners": {"r1": as_int(g[8]), "r2": as_int(g[9]), "r3": as_int(g[10]), "r4": as_int(g[11])},
        "prizes": {"r1": as_int(g[12]), "r2": as_int(g[13]), "r3": as_int(g[14]), "r4": as_int(g[15])},
        "source": "backup:configured",
    }
    return normalize(row)


def parse_mizuho_latest() -> dict[str, Any]:
    """Best-effort official page parser.

    Mizuho can return 403 or dynamically load the results. If official parsing
    fails, caller should fall back and keep metadata clear.
    """
    html = fetch_url(MIZUHO_URL)
    # The official page may include rendered table text in some environments.
    # This relaxed parser searches around Japanese labels.
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    draw_m = re.search(r"第\s*(\d+)\s*回", text)
    nums = [int(n) for n in re.findall(r"\b(\d{1,2})\b", text) if 1 <= int(n) <= 31]
    if not draw_m or len(nums) < 6:
        raise RuntimeError("official page could not be parsed; likely dynamic or blocked")
    # This generic parser is intentionally conservative. If the official page
    # structure changes, customize here after inspecting page source.
    raise RuntimeError("official parser placeholder: customize with current Mizuho DOM/API")


def fetch_latest() -> tuple[dict[str, Any], str, str | None]:
    official_error = None
    try:
        row = parse_mizuho_latest()
        row["source"] = "mizuhobank"
        return row, "mizuhobank", None
    except Exception as e:  # noqa: BLE001
        official_error = str(e)
        print(f"[warn] official fetch failed: {official_error}", file=sys.stderr)
    row = parse_backup_latest()
    return row, "backup:configured", official_error


def save(rows: list[dict[str, Any]], meta: dict[str, Any]) -> None:
    rows = sorted([normalize(r) for r in rows], key=lambda r: r["draw"])
    DATA_JSON.parent.mkdir(parents=True, exist_ok=True)
    DATA_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    with DATA_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["draw", "date", "n1", "n2", "n3", "n4", "n5", "bonus", "w1", "w2", "w3", "w4", "p1", "p2", "p3", "p4"])
        for r in rows:
            w.writerow([
                r["draw"], r["date"], *[f"{n:02d}" for n in r["nums"]], f"{r['bonus']:02d}",
                r.get("winners", {}).get("r1", 0), r.get("winners", {}).get("r2", 0), r.get("winners", {}).get("r3", 0), r.get("winners", {}).get("r4", 0),
                r.get("prizes", {}).get("r1", 0), r.get("prizes", {}).get("r2", 0), r.get("prizes", {}).get("r3", 0), r.get("prizes", {}).get("r4", 0),
            ])
    META_JSON.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    rows = load_current()
    before_latest = max((int(r["draw"]) for r in rows), default=0)
    latest, source, official_error = fetch_latest()
    validate(latest)
    by_draw = {int(r["draw"]): r for r in rows}
    old = by_draw.get(latest["draw"])
    by_draw[latest["draw"]] = latest
    new_rows = list(by_draw.values())
    meta = {
        "updatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": source,
        "officialError": official_error,
        "latestDraw": latest["draw"],
        "latestDate": latest["date"],
        "changed": old != latest,
        "previousLatestDraw": before_latest,
    }
    save(new_rows, meta)
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
