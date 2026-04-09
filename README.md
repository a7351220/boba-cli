# boba-cli

BOBA Daily Pipeline CLI — 讓 Claude 在對話裡用乾淨的指令跑完日報全流程。

## 設計理念

Claude 負責判斷（選題、撰稿、配圖 prompt），CLI 負責執行（API 抓資料、TG 發送、生圖腳本）。對話裡不再需要寫 inline bash 或管理散落的路徑。

## 安裝

```bash
# 需要：Python 3.11+、uv、ImageMagick、Node.js（npx/bun）
brew install uv imagemagick

git clone ... && cd boba-cli
cp .env.example .env   # 填入 API keys
uv sync
```

## 指令

```bash
uv run python3 cli.py status                           # 查今天 pipeline 進度
uv run python3 cli.py fetch                            # Phase 0+1：抓資料 + 建 blacklist
uv run python3 cli.py send                             # Phase 4：發 @test3635
uv run python3 cli.py send --channel official          # Phase 4：發正式頻道（TG only）
uv run python3 cli.py image --date MMDD --prompt "..." # Phase 5：生圖 + carousel
```

## 日報流程

```
fetch → Claude 選題撰稿 → send → image
```

1. **fetch** — 並行抓 BlockBeats + OpenNews + 15 KOL，讀 `history/` 最近 2 天建 blacklist，輸出候選 JSON（stdout + `/tmp/boba_candidates_{date}.json`）
2. **Claude 撰稿** — 讀候選 JSON，依 `prompts/` 規範寫 TG 版 + X 版，用 Write 工具存到 `/tmp/boba_daily_tg.txt` 和 `/tmp/boba_daily_x.txt`
3. **send** — 驗 UTF-8 → 發 TG → 存 `history/{YYYY-MM-DD}.txt`
4. **image** — Claude 構思場景 prompt → 生 16:9 主圖 → 裁 4:5 → IG Carousel → sendPhoto

## 目錄結構

```
boba-cli/
├── cli.py                  主入口
├── pyproject.toml          依賴（uv 管理）
├── .env                    API keys（不進版控）
├── .env.example            設定範本
├── scripts/
│   ├── fetch_news.py       BlockBeats + OpenNews + Twitter KOL
│   ├── send_tg.py          TG 發送 + 存檔
│   ├── image.py            生圖流程串接
│   ├── generate-daily-image.sh  16:9 AI 生圖 + overlay
│   ├── daily-overlay.sh    品牌 overlay（ImageMagick）
│   └── daily-ig-carousel.py     IG Carousel 產生器
├── tools/
│   └── baoyu-image-gen/    AI 生圖工具（Gemini Flash）
├── img/                    品牌素材（Pepe ref × 3、Penny ref × 2、logo）
├── prompts/                撰稿規範
│   ├── format.md           8 則格式、TG/X 模板
│   ├── tone.md             BOBA 語氣五原則、禁用語
│   ├── quality.md          品質自檢清單
│   ├── config.md           品牌資訊、頻道帳號
│   ├── daily-pipeline.md   Phase 0–4 完整流程
│   ├── daily-images.md     Phase 5 配圖 SOP
│   └── news-research/      KOL 名冊、選題過濾、來源品質
├── history/                日報存檔（.txt + metadata）
└── output/                 圖片輸出
    ├── drafts/             AI 底圖（無 overlay）
    └── ig-{MMDD}/          Carousel slides
```

## 環境變數

見 `.env.example`。所有 key 從環境變數讀取，不 hardcode。`.env` 優先於 shell 全域變數。

## API 來源

| 服務 | 用途 | Token |
|------|------|-------|
| BlockBeats | 快訊 / 24h 新聞 | `BLOCKBEATS_API_KEY` |
| OpenNews (6551.io) | 加密新聞搜尋 | `OPENNEWS_TOKEN` |
| Twitter (6551.io) | KOL 推文 × 15 帳號 | `TWITTER_TOKEN` |
| Telegram Bot API | 發送到 @test3635 / @bobadaoann | `TELEGRAM_BOT_TOKEN` |
| Google Gemini Flash | AI 生圖 | `GEMINI_API_KEY` |
