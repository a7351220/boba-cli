"""
Phase 0+1: 讀歷史建 blacklist + 並行抓 BlockBeats / OpenNews / Twitter KOL
輸出: candidates JSON (stdout + /tmp/boba_candidates_{date}.json)
"""

import asyncio
import json
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path

import httpx

# ── 設定 ──────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
HISTORY_DIR = BASE_DIR / "history"

BLOCKBEATS_KEY = os.environ["BLOCKBEATS_API_KEY"]
OPENNEWS_TOKEN = os.environ["OPENNEWS_TOKEN"]
TWITTER_TOKEN  = os.environ["TWITTER_TOKEN"]
API_BASE       = "https://ai.6551.io"

KOL_LIST = [
    "KobeissiLetter", "tradfi", "EricBalchunas", "JSeyff",
    "EleanorTerrett", "DegenerateNews", "aixbt_agent", "DefiantNews",
    "followin_io_zh", "lanhubiji", "BinanceResearch", "WSJmarkets",
    "BitcoinMagazine", "alphanonceStaff", "lookonchain",
    "dlnews", "MilkRoad", "HYPERDailyTK", "WatcherGuru",
    "testingcatalog", "WuBlockchain",
]

# ── Phase 0: blacklist ────────────────────────────────────────

def build_blacklist(today: date) -> list[str]:
    """讀最近 2 天歷史，提取已報導關鍵字"""
    keywords = []
    for delta in (1, 2):
        d = today - timedelta(days=delta)
        path = HISTORY_DIR / f"{d}.txt"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        # 提取各則標題（emoji 數字後的文字）
        titles = re.findall(r'[1-8]️⃣\s+(.+)', text)
        keywords.extend(titles)
    return keywords

# ── API helpers ───────────────────────────────────────────────

async def fetch_blockbeats(client: httpx.AsyncClient) -> list[dict]:
    resp = await client.get(
        "https://api.theblockbeats.news/v1/open-api/open-flash",
        params={"size": 50, "page": 1, "lang": "cht"},
        headers={"Authorization": f"Bearer {BLOCKBEATS_KEY}"},
        timeout=20,
    )
    data = resp.json()
    items = data.get("data", {}).get("data", []) if isinstance(data.get("data"), dict) else []
    return [
        {
            "source": "blockbeats",
            "title": i.get("title", ""),
            "content": i.get("content", ""),
            "url": i.get("link") or i.get("url", ""),
            "ts": i.get("create_time", ""),
        }
        for i in items
        if i.get("title") and (i.get("link") or i.get("url"))
    ]


async def fetch_opennews(client: httpx.AsyncClient) -> list[dict]:
    resp = await client.post(
        f"{API_BASE}/open/news_search",
        json={"limit": 50, "page": 1},
        headers={"Authorization": f"Bearer {OPENNEWS_TOKEN}"},
        timeout=20,
    )
    data = resp.json()
    raw = data.get("data", {})
    items = raw if isinstance(raw, list) else raw.get("data", raw.get("list", []))
    return [
        {
            "source": "opennews",
            "title": i.get("text", "") or i.get("title", ""),
            "content": i.get("description", ""),
            "url": i.get("link", ""),
            "ts": i.get("ts", ""),
        }
        for i in items
        if (i.get("text") or i.get("title")) and i.get("link")
    ]


async def fetch_kol_tweets(client: httpx.AsyncClient, username: str) -> list[dict]:
    try:
        resp = await client.post(
            f"{API_BASE}/open/twitter_user_tweets",
            json={"username": username, "maxResults": 10, "product": "Latest",
                  "includeReplies": False, "includeRetweets": False},
            headers={"Authorization": f"Bearer {TWITTER_TOKEN}"},
            timeout=15,
        )
        data = resp.json()
        tweets = data.get("data", []) if data.get("success") else []
        return [
            {
                "source": f"twitter/{username}",
                "title": t.get("text", "")[:120],
                "content": t.get("text", ""),
                "url": f"https://x.com/i/status/{t['id']}",
                "ts": t.get("createdAt", ""),
            }
            for t in tweets
            if t.get("text") and t.get("id")
        ]
    except Exception:
        return []


# ── 主流程 ────────────────────────────────────────────────────

async def run(target_date: date) -> dict:
    blacklist = build_blacklist(target_date)

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            fetch_blockbeats(client),
            fetch_opennews(client),
            *[fetch_kol_tweets(client, kol) for kol in KOL_LIST],
            return_exceptions=True,
        )

    bb_items    = results[0] if not isinstance(results[0], Exception) else []
    on_items    = results[1] if not isinstance(results[1], Exception) else []
    kol_items   = []
    for r in results[2:]:
        if not isinstance(r, Exception):
            kol_items.extend(r)

    all_items = bb_items + on_items + kol_items

    # 過濾掉無 URL 的
    all_items = [i for i in all_items if i.get("url")]

    output = {
        "date": str(target_date),
        "blacklist": blacklist,
        "stats": {
            "blockbeats": len(bb_items),
            "opennews": len(on_items),
            "kol_scanned": sum(1 for r in results[2:] if not isinstance(r, Exception)),
            "kol_total": len(KOL_LIST),
            "total_candidates": len(all_items),
        },
        "candidates": all_items,
    }
    return output


def main(target_date: date | None = None):
    if target_date is None:
        target_date = date.today()

    result = asyncio.run(run(target_date))

    # 存 /tmp
    tmp_path = f"/tmp/boba_candidates_{target_date}.json"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # stdout 輸出（Claude 讀這個）
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n# 已存至 {tmp_path}", file=sys.stderr)
    print(f"# BlockBeats: {result['stats']['blockbeats']} 則", file=sys.stderr)
    print(f"# OpenNews:   {result['stats']['opennews']} 則", file=sys.stderr)
    print(f"# KOL:        {result['stats']['kol_scanned']}/{result['stats']['kol_total']} 帳號掃描", file=sys.stderr)
    print(f"# 總候選:      {result['stats']['total_candidates']} 則", file=sys.stderr)
    print(f"# Blacklist:  {len(result['blacklist'])} 條", file=sys.stderr)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--date", help="YYYY-MM-DD", default=None)
    args = p.parse_args()
    d = date.fromisoformat(args.date) if args.date else None
    main(d)
