#!/usr/bin/env python3
"""
Update data/results.json and data/results.csv for ミニロト分析ナビ.

Runs weekly via GitHub Actions after the Tuesday MiniLoto draw.

소스 체인 (앞에서부터 순서대로 시도 — 전부 물료):
  1) 미즈호 공식 페이지 직접 (공식 소스. Akamai 차단 시 자동 실패 → 다음으로)
  2) 백넘버 공개 표 (정적 HTML — 주요 소스)
  3) 같은 표를 읽기 프록시(r.jina.ai) 경유로 마크다운 파싱 (2번이 막혔을 때)
  4) BACKUP_MINILOTO_URL (선택 시크릿으로 설정한 사용자 정의 소스)

삼중 확인: 숫자 범위·중복·갯수 검증(validate) + 회차 정규화 후 저장.
Always validate results before save.
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
RAKUTEN_URL = "https://takarakuji.rakuten.co.jp/backnumber/mini/"
JINA_PREFIX = "https://r.jina.ai/"
# Optional private fallback source. Set it as a GitHub repository secret or environment variable.
# Keep this empty in the public repository to avoid exposing any reference source.
BACKUP_URL = os.environ.get("BACKUP_MINILOTO_URL", "").strip()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja,en;q=0.8",
}


def as_int(v: Any) -> int:
    if v is None:
        return 0
    s = str(v).strip()
    if s in {"", "該当なし", "なし", "-"}:
        return 0
    digits = re.sub(r"[^\d]", "", s)  # '(12)', '22,278,000円', '**1,346口**' 등 → 숫자만 추출
    return int(digits) if digits else 0


def norm_date(s: str) -> str:
    """'2026/08/04' → '2026/8/4' (기존 데이터 형식과 통일)."""
    m = re.match(r"\s*(\d{4})[/-](\d{1,2})[/-](\d{1,2})\s*$", str(s))
    if not m:
        return str(s).strip()
    y, mo, d = (int(x) for x in m.groups())
    return f"{y}/{mo}/{d}"


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
        "date": norm_date(row["date"]),
        "nums": sorted([int(n) for n in row["nums"]]),
        "bonus": int(row["bonus"]),
    }
    if "winners" in row:
        out["winners"] = {f"r{i}": as_int(row["winners"].get(f"r{i}")) for i in range(1, 5)}
    if "prizes" in row:
        out["prizes"] = {f"r{i}": as_int(row["prizes"].get(f"r{i}")) for i in range(1, 5)}
    validate(out)
    return out


def fetch_url(url: str, timeout: int = 30) -> str:
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return r.text


# --------------------------------------------------------------------------
# 공개 백넘버 표 파서 (HTML 원본 / 프록시 마크다운 두 형식 모두 지원)
# --------------------------------------------------------------------------
def parse_backnumber_html(html: str) -> list[dict[str, Any]]:
    """정적 HTML의 당월 추첨 테이블 전부 파싱 (여러 회차 누적 시 모두 반환)."""
    rows: list[dict[str, Any]] = []
    for tbody in re.findall(r"<tbody>(.*?)</tbody>", html, re.S):
        dm = re.search(r"回号</th>\s*<th[^>]*>\s*第\s*(\d+)\s*回\s*</th>", tbody)
        tm = re.search(r"抽せん日</th>\s*<td[^>]*>\s*([\d/]+)\s*</td>", tbody)
        nm = re.search(r"本数字(.*?)</tr>", tbody, re.S)
        if not (dm and tm and nm):
            continue
        cells = re.findall(r'loto-font-large">([^<]+)</span>', nm.group(1))
        if len(cells) != 6:
            continue
        nums = [as_int(c) for c in cells[:5]]
        bonus = as_int(cells[5])
        rank_rows = re.findall(
            r"<th>\s*([1-4])等\s*</th>\s*<td[^>]*>\s*([^<]*?)\s*</td>\s*<td[^>]*>\s*(?:<b>)?\s*([^<]*?)\s*(?:</b>)?\s*</td>",
            tbody,
        )
        winners: dict[str, int] = {}
        prizes: dict[str, int] = {}
        for rk, wcell, pcell in rank_rows:
            winners[f"r{rk}"] = as_int(wcell)
            prizes[f"r{rk}"] = as_int(pcell)
        row: dict[str, Any] = {
            "draw": int(dm.group(1)),
            "date": tm.group(1),
            "nums": nums,
            "bonus": bonus,
            "source": "backnumber-table",
        }
        if winners and prizes:
            row["winners"] = winners
            row["prizes"] = prizes
        rows.append(normalize(row))
    return rows


def parse_backnumber_markdown(md: str) -> list[dict[str, Any]]:
    """읽기 프록시(jina) 마크다운 표 파싱.
    예: '| 回号 | 第1398回 |' / '| 本数字 ( )はボーナス数字 | 15 | 16 | 26 | 27 | 31 | (12) |'
    """
    rows: list[dict[str, Any]] = []
    chunks = re.split(r"\|\s*回号\s*\|", md)[1:]
    for chunk in chunks:
        dm = re.match(r"\s*第\s*(\d+)\s*回\s*\|", chunk)
        tm = re.search(r"抽せん日\s*\|\s*([\d/]+)", chunk)
        nm = re.search(r"本数字[^\n|]*\|([^\n]+)", chunk)
        if not (dm and tm and nm):
            continue
        cells = re.findall(r"\(?\b\d{1,2}\b\)?", nm.group(1))
        if len(cells) < 6:
            continue
        nums = [as_int(c) for c in cells[:5]]
        bonus = as_int(cells[5])
        rows.append(normalize({
            "draw": int(dm.group(1)),
            "date": tm.group(1),
            "nums": nums,
            "bonus": bonus,
            "source": "backnumber-table:proxy",
        }))
    return rows


def parse_backup_latest() -> dict[str, Any]:
    """Parse latest row from a configured compatible public result table."""
    if not BACKUP_URL:
        raise RuntimeError("BACKUP_MINILOTO_URL is not configured")
    html = fetch_url(BACKUP_URL)
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
    """Official page best-effort parser (page body is loaded dynamically by JS).

    Usually fails on CI (Akamai blocks datacenter IPs or JS table is empty),
    in which case the caller moves on to the next source. Kept first so that
    the official page is used automatically whenever it becomes reachable.
    """
    html = fetch_url(MIZUHO_URL, timeout=20)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    if "表示に時間がかかっております" in text or "第" not in text:
        raise RuntimeError("official page results are dynamically loaded; skipping")
    raise RuntimeError("official parser: no reliable static results found")


def fetch_latest_rows() -> tuple[list[dict[str, Any]], str, list[str]]:
    errors: list[str] = []
    # ① 미즈호 공식 (현재는 동적 로딩이라 보통 실패 → 다음 소스로)
    try:
        row = parse_mizuho_latest()
        row["source"] = "mizuhobank"
        return [row], "mizuhobank", errors
    except Exception as e:  # noqa: BLE001
        errors.append(f"mizuhobank: {e}")
    # ② 공개 백넘버 표 직접 파싱 (정적 HTML — 주력 소스)
    try:
        rows = parse_backnumber_html(fetch_url(RAKUTEN_URL))
        if rows:
            return rows, "backnumber-table", errors
        raise RuntimeError("no current-month draws parsed (empty table)")
    except Exception as e:  # noqa: BLE001
        errors.append(f"backnumber-direct: {e}")
    # ③ 읽기 프록시 경유 마크다운 파싱
    try:
        rows = parse_backnumber_markdown(fetch_url(JINA_PREFIX + RAKUTEN_URL, timeout=60))
        if rows:
            return rows, "backnumber-table:proxy", errors
        raise RuntimeError("proxy parse returned no rows")
    except Exception as e:  # noqa: BLE001
        errors.append(f"backnumber-proxy: {e}")
    # ④ 사용자 정의 백업 소스 (시크릿 설정 시)
    try:
        row = parse_backup_latest()
        return [row], "backup:configured", errors
    except Exception as e:  # noqa: BLE001
        errors.append(f"backup: {e}")
    raise RuntimeError("all sources failed: " + " | ".join(errors))


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
    by_draw = {int(r["draw"]): r for r in rows}
    before_latest = max(by_draw, default=0)

    fetched, source, errors = fetch_latest_rows()
    updated: list[int] = []
    for row in fetched:
        old = by_draw.get(row["draw"])
        if old is None or any(str(old.get(k)) != str(row.get(k)) for k in ("date", "nums", "bonus")):
            by_draw[row["draw"]] = row
            updated.append(row["draw"])
    new_rows = list(by_draw.values())
    latest = max(new_rows, key=lambda r: r["draw"]) if new_rows else None

    meta = {
        "updatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": source,
        "fetchErrors": errors or None,
        "latestDraw": latest["draw"] if latest else 0,
        "latestDate": latest["date"] if latest else "",
        "changed": bool(updated),
        "updatedDraws": updated,
        "previousLatestDraw": before_latest,
    }
    # ★ 변화가 있을 때만 파일 저장 → 불필요한 커밋/재배포 방지
    if updated or not DATA_JSON.exists():
        save(new_rows, meta)
        print(f"saved new/updated draws: {updated}")
    else:
        print("no changes — data files left untouched (no commit will be made)")
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
