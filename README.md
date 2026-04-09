# boba-cli

BOBA Daily Pipeline CLI — 讓 Claude 在對話裡用乾淨的指令跑完日報全流程。

Claude 負責判斷（選題、撰稿、配圖 prompt），CLI 負責執行（抓資料、TG 發送、生圖）。

---

## 安裝

### 需求

- macOS 或 Ubuntu
- [Claude Code](https://claude.ai/code)（撰稿步驟需要）

### 一鍵安裝

```bash
git clone https://github.com/a7351220/boba-cli
cd boba-cli
cp .env.example .env
```

填入 `.env` 裡的 5 個 token（見下方說明），然後：

```bash
./setup.sh
```

腳本會自動安裝：uv、ImageMagick、Node.js、Bun、Chrome/Chromium、Noto Sans TC 字型、Python 依賴。

---

## 環境變數（`.env`）

| 變數 | 用途 | 取得方式 |
|------|------|---------|
| `TELEGRAM_BOT_TOKEN` | 發送 TG 訊息和圖片 | [@BotFather](https://t.me/BotFather) 建立 Bot |
| `GEMINI_API_KEY` | AI 生圖（Gemini Flash） | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `BLOCKBEATS_API_KEY` | 抓 BlockBeats 快訊 | BlockBeats API 申請 |
| `OPENNEWS_TOKEN` | 抓聚合新聞 | 6551.io 申請 |
| `TWITTER_TOKEN` | 抓 KOL 推文 | 6551.io 申請 |

---

## 使用方式

### 快速開始（在 Claude Code 裡輸入）

```
幫我跑日報
```

Claude 會自動執行完整流程。

### 手動執行各步驟

```bash
# 查今天進度
uv run python3 cli.py status

# Phase 1：抓資料（BlockBeats + OpenNews + 15 KOL）
uv run python3 cli.py fetch

# Phase 4：發送到測試頻道 @test3635
uv run python3 cli.py send

# Phase 4：發送到正式頻道（需先確認）
uv run python3 cli.py send --channel official

# Phase 5：生圖 + IG Carousel
uv run python3 cli.py image --date MMDD --prompt "..."
```

---

## 日報 Pipeline

```
fetch → Claude 選題撰稿 → send → image
```

1. **fetch** — 並行抓 BlockBeats + OpenNews + 15 KOL，讀 `history/` 建 blacklist，輸出候選 JSON
2. **Claude 撰稿** — 依 `prompts/` 規範選 8 則新聞，寫 TG 版 + X 版，存到 `/tmp/boba_daily_tg.txt` 和 `/tmp/boba_daily_x.txt`
3. **send** — 驗 UTF-8 → 發 TG → 存 `history/{YYYY-MM-DD}.txt`
4. **image** — Claude 構思場景 prompt → 生 16:9 主圖 → 裁 4:5 → IG Carousel（10 張）→ sendPhoto → 發 IG 文案

---

## 目錄結構

```
boba-cli/
├── cli.py                        主入口
├── setup.sh                      一鍵安裝腳本
├── pyproject.toml                依賴（uv 管理）
├── .env.example                  環境變數範本
├── scripts/
│   ├── fetch_news.py             抓資料（BlockBeats + OpenNews + Twitter KOL）
│   ├── send_tg.py                TG 發送 + 存檔
│   ├── image.py                  生圖流程串接
│   ├── generate-daily-image.sh   16:9 AI 生圖 + overlay
│   ├── daily-overlay.sh          品牌 overlay（ImageMagick）
│   └── daily-ig-carousel.py      IG Carousel 產生器（Chrome headless）
├── tools/
│   └── baoyu-image-gen/          AI 生圖工具（Gemini Flash）
├── img/
│   ├── fonts/NotoSansTC.ttf      內建字型（跨平台）
│   └── ...                       品牌素材（Pepe ref × 4、Penny ref × 2、logo）
├── prompts/                      Claude 撰稿規範
│   ├── format.md                 8 則格式、TG/X 模板
│   ├── tone.md                   BOBA 語氣五原則、禁用語
│   ├── quality.md                品質自檢清單
│   ├── config.md                 品牌資訊、頻道帳號
│   ├── daily-pipeline.md         Phase 0–4 完整流程
│   ├── daily-images.md           Phase 5 配圖 SOP（場景庫）
│   └── news-research/            KOL 名冊、選題過濾、來源品質
├── history/                      日報存檔（git 忽略）
└── output/                       圖片輸出（git 忽略）
    ├── drafts/                   AI 底圖
    └── ig-{MMDD}/                Carousel slides
```

---

## API 來源

| 服務 | 用途 |
|------|------|
| BlockBeats | 幣圈快訊 / 24h 新聞 |
| OpenNews (6551.io) | 加密新聞聚合搜尋 |
| Twitter (6551.io) | KOL 推文掃描（15 帳號） |
| Telegram Bot API | 發送訊息和圖片到頻道 |
| Google Gemini Flash | AI 生圖（16:9 + 4:5） |
