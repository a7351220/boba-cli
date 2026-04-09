#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Run with: .venv/bin/python3 cli.py  (or: python3 cli.py if venv activated)
"""
boba-cli — BOBA Daily Pipeline CLI

用法:
  python3 cli.py fetch             # Phase 0+1: 抓資料
  python3 cli.py send              # Phase 4:   發送
  python3 cli.py image             # Phase 5:   生圖
  python3 cli.py status            # 查今天進度
"""

import argparse
import os
import sys
from datetime import date
from pathlib import Path

# ── .env 載入 ──────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
env_file = BASE_DIR / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ[k.strip()] = v.strip()  # .env 優先於 shell 全域變數

# ── subcommands ────────────────────────────────────────────────

def cmd_fetch(args):
    """Phase 0+1: 讀歷史建 blacklist + 並行抓新聞"""
    from scripts.fetch_news import main as fetch_main
    from datetime import date as _date
    d = _date.fromisoformat(args.date) if args.date else None
    fetch_main(d)


def cmd_send(args):
    """Phase 4: TG 發送 + 存檔"""
    from scripts.send_tg import main as send_main
    from datetime import date as _date
    d = _date.fromisoformat(args.date) if args.date else None
    send_main(
        channel=args.channel,
        tg_file=args.tg_file,
        x_file=args.x_file,
        target_date=d,
    )


def cmd_image(args):
    """Phase 5: 生圖 + Carousel + 發 @test3635"""
    from scripts.image import main as image_main
    mmdd  = args.date  # MMDD
    label = args.label or f"{int(mmdd[:2])}/{int(mmdd[2:])}"
    image_main(
        mmdd=mmdd,
        date_label=label,
        prompt=args.prompt,
        x_file=args.x_file,
        skip_carousel=args.skip_carousel,
    )


def cmd_status(args):
    """查今天 pipeline 各步驟是否完成"""
    from datetime import date as _date
    today = _date.fromisoformat(args.date) if args.date else _date.today()
    mmdd  = today.strftime("%m%d")

    checks = {
        "candidates JSON": Path(f"/tmp/boba_candidates_{today}.json"),
        "TG 文字":         Path("/tmp/boba_daily_tg.txt"),
        "X 文字":          Path("/tmp/boba_daily_x.txt"),
        "history 存檔":    BASE_DIR / f"history/{today}.txt",
        "16:9 主圖":       BASE_DIR / f"output/daily-{mmdd}-final.png",
        "IG Carousel":     BASE_DIR / f"output/ig-{mmdd}/slide-00-cover.png",
    }

    print(f"\n📋 BOBA Daily {today} 進度\n")
    all_done = True
    for label, path in checks.items():
        ok = path.exists()
        if not ok:
            all_done = False
        print(f"  {'✅' if ok else '⬜'} {label}")

    if all_done:
        print("\n🎉 全部完成！")
    else:
        todo = [l for l, p in checks.items() if not p.exists()]
        print(f"\n⏳ 待完成：{', '.join(todo)}")
    print()


# ── CLI 入口 ───────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="boba",
        description="BOBA Daily Pipeline CLI",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # fetch
    f = sub.add_parser("fetch", help="Phase 0+1: 抓資料 + 建 blacklist")
    f.add_argument("--date", help="YYYY-MM-DD（預設今天）")

    # send
    s = sub.add_parser("send", help="Phase 4: TG 發送 + 存檔")
    s.add_argument("--channel", default="test", choices=["test", "official"],
                   help="test=@test3635（預設）| official=@bobadaoann")
    s.add_argument("--tg-file", default="/tmp/boba_daily_tg.txt")
    s.add_argument("--x-file",  default="/tmp/boba_daily_x.txt")
    s.add_argument("--date", help="YYYY-MM-DD（存檔用，預設今天）")

    # image
    i = sub.add_parser("image", help="Phase 5: 生圖 + Carousel + 發 @test3635")
    i.add_argument("--date", required=True, help="MMDD 格式，如 0408")
    i.add_argument("--label", help="顯示用日期，如 '4/8'（可省略，自動推導）")
    i.add_argument("--prompt", required=True, help="AI 生圖 Prompt（英文）")
    i.add_argument("--x-file", default="/tmp/boba_daily_x.txt")
    i.add_argument("--skip-carousel", action="store_true")

    # status
    st = sub.add_parser("status", help="查今天 pipeline 進度")
    st.add_argument("--date", help="YYYY-MM-DD（預設今天）")

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "fetch":  cmd_fetch,
        "send":   cmd_send,
        "image":  cmd_image,
        "status": cmd_status,
    }
    dispatch[args.cmd](args)


if __name__ == "__main__":
    main()
