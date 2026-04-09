"""
Phase 5: 生圖 + Carousel + 發送（完全本地，不依賴 content-studio）
- scripts/generate-daily-image.sh（refs 指向本地 img/）
- ImageMagick 右偏裁 4:5
- scripts/daily-ig-carousel.py
- 結尾 slide 複製前一天
- sendPhoto 發 @test3635
"""

import json
import os
import subprocess
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path

BASE_DIR   = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"
BOT_TOKEN  = os.environ["TELEGRAM_BOT_TOKEN"]
TEST_CHAT   = "@test3635"


def run(cmd: list, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kwargs)


def generate_16x9(mmdd: str, date_label: str, prompt: str) -> Path:
    draft  = OUTPUT_DIR / f"drafts/daily-{mmdd}.png"
    final  = OUTPUT_DIR / f"daily-{mmdd}-final.png"
    script = BASE_DIR / "scripts/generate-daily-image.sh"

    r = run([str(script), mmdd, date_label, prompt, str(final)],
            cwd=str(BASE_DIR))
    print(r.stdout.strip() or f"✅ 16:9 生成：{final}", file=sys.stderr)
    return final


def crop_4x5(mmdd: str) -> Path:
    """從 16:9 草稿右偏裁 4:5（Pepe 在右側）"""
    draft = OUTPUT_DIR / f"drafts/daily-{mmdd}.png"
    out   = OUTPUT_DIR / f"drafts/daily-{mmdd}-ig-base.png"

    # 取得尺寸
    r = run(["identify", "-format", "%wx%h", str(draft)])
    w, h = map(int, r.stdout.strip().split("x"))

    target_w = int(h * 4 / 5)
    # 右偏：讓 Pepe 入鏡
    left = min(w - target_w, int(w * 0.38))

    run(["convert", str(draft),
         "-crop", f"{target_w}x{h}+{left}+0",
         "+repage",
         "-resize", "1080x1350!",
         str(out)])
    print(f"✅ 4:5 裁切完成：{out}", file=sys.stderr)
    return out


def generate_carousel(mmdd: str, date_label: str,
                       x_file: str = "/tmp/boba_daily_x.txt") -> Path:
    ig_dir  = OUTPUT_DIR / f"ig-{mmdd}"
    ig_dir.mkdir(exist_ok=True)
    base    = OUTPUT_DIR / f"drafts/daily-{mmdd}-ig-base.png"
    script  = BASE_DIR / "scripts/daily-ig-carousel.py"

    run(["python3", str(script), x_file, str(base), date_label, str(ig_dir)],
        cwd=str(BASE_DIR))
    print(f"✅ Carousel 完成：{ig_dir}", file=sys.stderr)
    return ig_dir


def copy_ending_slide(mmdd: str) -> bool:
    ig_dir  = OUTPUT_DIR / f"ig-{mmdd}"
    dst     = ig_dir / "slide-ending.png"

    # 優先用 repo 內建的結尾圖
    bundled = BASE_DIR / "img/slide-ending.png"
    if bundled.exists():
        run(["cp", str(bundled), str(dst)])
        print(f"✅ 結尾 slide 複製（內建）：{dst}", file=sys.stderr)
        return True

    # 退而求其次：前一天的輸出
    today     = date(int("20" + mmdd[:2] if len(mmdd) == 4 else mmdd[:4]),
                     int(mmdd[-4:-2]) if len(mmdd) > 4 else int(mmdd[:2]),
                     int(mmdd[-2:]))
    prev_mmdd = (today - timedelta(days=1)).strftime("%m%d")
    src       = OUTPUT_DIR / f"ig-{prev_mmdd}/slide-ending.png"
    if src.exists():
        run(["cp", str(src), str(dst)])
        print(f"✅ 結尾 slide 複製（前一天）：{dst}", file=sys.stderr)
        return True

    print(f"⚠️  找不到結尾 slide", file=sys.stderr)
    return False


def generate_ig_caption(mmdd: str, date_label: str,
                        x_file: str = "/tmp/boba_daily_x.txt") -> Path:
    """從 X 版文字解析 hook + 標題，生成 IG 文案並存檔"""
    ig_dir = OUTPUT_DIR / f"ig-{mmdd}"
    ig_dir.mkdir(exist_ok=True)
    out = ig_dir / "ig-caption.txt"

    text = Path(x_file).read_text(encoding="utf-8")
    lines = text.splitlines()

    # 取 hook：header 之後第一個非空、非 ——— 的段落
    hook = ""
    passed_header = False
    for line in lines:
        stripped = line.strip()
        if not passed_header:
            if stripped.startswith("🧋"):
                passed_header = True
            continue
        if not stripped or stripped.startswith("———"):
            if hook:
                break
            continue
        hook += stripped + " "
    hook = hook.strip().rstrip("👇🧵").strip()

    # 取各則標題（1️⃣ ~ 8️⃣ 後面的文字）
    number_emojis = {"1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣"}
    titles = []
    for line in lines:
        for em in number_emojis:
            if line.startswith(em):
                title = line[len(em):].strip()
                if title:
                    titles.append(f"{em} {title}")
                break

    title_block = "\n".join(titles) if titles else ""
    n = len(titles)

    # 動態 hashtag：從標題抓關鍵字
    dynamic_tags = []
    title_concat = " ".join(titles).upper()
    tag_map = {
        "ETH": "#ETH", "ETHEREUM": "#ETH",
        "SOL": "#SOL", "SOLANA": "#SOL",
        "ETF": "#ETF", "MSBT": "#MSBT",
        "STRATEGY": "#Strategy", "SAYLOR": "#Saylor",
        "PEPE": "#PEPE", "STABLECOIN": "#Stablecoin",
        "穩定幣": "#穩定幣", "伊朗": "#伊朗",
        "黃金": "#黃金", "DEFI": "#DeFi",
    }
    for key, tag in tag_map.items():
        if key in title_concat and tag not in dynamic_tags:
            dynamic_tags.append(tag)
    dynamic_str = " ".join(dynamic_tags[:3])

    caption = f"""🧋 珍奶科技日報 BOBA Daily｜{date_label}

{hook}

今天 {n} 則重點整理好了，滑過去看 👉

{title_block}

💬 你最關注哪一則？留言告訴我們！
📲 完整版每日快報 → Telegram @bobadaolfg（連結在 bio）

·
·
·

#加密貨幣 #比特幣 #BTC #區塊鏈 #投資理財 #每日新聞 #幣圈日報 #DeFi #Web3 #台灣投資 #BOBADAO #珍奶科技日報 #crypto #bitcoin {dynamic_str}"""

    out.write_text(caption.strip(), encoding="utf-8")
    print(f"✅ IG 文案已存：{out}", file=sys.stderr)
    return out


def send_photos(mmdd: str) -> None:
    """sendPhoto 全部圖片到 @test3635，最後 sendMessage IG 文案"""
    main_img = OUTPUT_DIR / f"daily-{mmdd}-final.png"
    ig_dir   = OUTPUT_DIR / f"ig-{mmdd}"

    slides = (["slide-00-cover.png"]
              + [f"slide-0{i}.png" for i in range(1, 9)]
              + ["slide-ending.png"])

    all_imgs = [main_img] + [ig_dir / s for s in slides]

    for img in all_imgs:
        if not img.exists():
            print(f"⚠️  找不到：{img}", file=sys.stderr)
            continue
        _send_one(str(img))

    # 發 IG 文案
    caption_file = ig_dir / "ig-caption.txt"
    if caption_file.exists():
        _send_message(caption_file.read_text(encoding="utf-8"))
        print("✅ IG 文案已發送", file=sys.stderr)


def _send_message(text: str) -> None:
    payload = json.dumps({"chat_id": TEST_CHAT, "text": text}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.loads(r.read())
    if not res.get("ok"):
        print(f"❌ sendMessage 失敗：{res}", file=sys.stderr)


def _send_one(path: str) -> None:
    with open(path, "rb") as f:
        data = f.read()
    boundary = b"----Boundary"
    body = (b"--" + boundary + b"\r\n"
            b'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
            + TEST_CHAT.encode() + b"\r\n"
            b"--" + boundary + b"\r\n"
            b'Content-Disposition: form-data; name="photo"; filename="img.png"\r\n'
            b"Content-Type: image/png\r\n\r\n"
            + data + b"\r\n"
            b"--" + boundary + b"--\r\n")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary.decode()}"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        res = json.loads(r.read())
    name = Path(path).name
    print(f"{'✅' if res.get('ok') else '❌'} {name}")


def main(mmdd: str, date_label: str, prompt: str,
         x_file: str = "/tmp/boba_daily_x.txt",
         skip_carousel: bool = False):
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "drafts").mkdir(exist_ok=True)

    print("▶ Step 1: 生成 16:9 主圖...", file=sys.stderr)
    generate_16x9(mmdd, date_label, prompt)

    print("▶ Step 2: 裁切 4:5 底圖...", file=sys.stderr)
    crop_4x5(mmdd)

    if not skip_carousel:
        print("▶ Step 3: 生成 IG Carousel...", file=sys.stderr)
        generate_carousel(mmdd, date_label, x_file)

        print("▶ Step 4: 複製結尾 slide...", file=sys.stderr)
        copy_ending_slide(mmdd)

        print("▶ Step 5: 生成 IG 文案...", file=sys.stderr)
        generate_ig_caption(mmdd, date_label, x_file)

    print("▶ Step 6: 發送到 @test3635...", file=sys.stderr)
    send_photos(mmdd)

    print("✅ Phase 5 完成", file=sys.stderr)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--date", required=True, help="MMDD 格式，如 0408")
    p.add_argument("--label", help="顯示用日期，如 '4/8'（預設從 --date 推導）")
    p.add_argument("--prompt", required=True, help="AI 生圖 Prompt（英文）")
    p.add_argument("--x-file", default="/tmp/boba_daily_x.txt")
    p.add_argument("--skip-carousel", action="store_true")
    args = p.parse_args()

    mmdd = args.date
    label = args.label or f"{int(mmdd[:2])}/{int(mmdd[2:])}"
    main(mmdd, label, args.prompt, args.x_file, args.skip_carousel)
