# boba-cli

BOBA Daily Pipeline CLI。讓 Claude 在對話裡用乾淨的指令調用工具，不再手動管理 API call 和腳本路徑。

## 指令格式

所有指令用 `uv run python3 cli.py <subcommand>`：

```bash
uv run python3 cli.py status                          # 查今天進度
uv run python3 cli.py fetch                           # Phase 0+1：抓資料
uv run python3 cli.py send                            # Phase 4：發 @test3635
uv run python3 cli.py send --channel official         # Phase 4：發正式頻道（需使用者確認）
uv run python3 cli.py image --date MMDD --prompt "..." # Phase 5：生圖 + carousel
uv run python3 cli.py ingest                          # Wiki ingest（用 Sonnet 獨立跑）
uv run python3 cli.py ingest --date 2026-04-12        # 指定日期 ingest
```

## 日報 Pipeline

```
fetch → Claude 選題撰稿 → send → ingest → image
```

1. `fetch` — 抓 BlockBeats + OpenNews + 15 KOL，輸出候選 JSON（含 blacklist）
2. Claude 讀 JSON → 判斷選題 → 寫 TG 版 + X 版 → 用 Python Write 工具存成 `/tmp/boba_daily_tg.txt` 和 `/tmp/boba_daily_x.txt`
3. `send` — 驗 UTF-8 → 發 @test3635 → 存 `history/` → 自動同步到 `boba-wiki/raw/`
4. `ingest` — 用 Sonnet 獨立 session 把日報 ingest 進 boba-wiki（更新/建立 wiki pages）
5. `image` — Claude 構思 prompt → 生 16:9 → 裁 4:5 → carousel → sendPhoto

## 撰稿規範（Claude 撰稿時必讀）

| 檔案 | 用途 |
|------|------|
| `prompts/format.md` | 8 則固定格式、TG/X 模板、排序原則 |
| `prompts/tone.md` | BOBA 語氣五原則、禁用語清單 |
| `prompts/quality.md` | 品質自檢清單（來源、重複、語氣、格式） |
| `prompts/config.md` | 品牌資訊、頻道帳號、合作夥伴 |
| `prompts/daily-pipeline.md` | Phase 0-4 完整流程參考 |
| `prompts/daily-images.md` | Phase 5 配圖 SOP（Pepe/Penny lock、prompt 模板） |
| `prompts/news-research/kol-roster.md` | 15 個 KOL 帳號完整名冊 |
| `prompts/news-research/filtering.md` | 選題過濾標準 |
| `prompts/news-research/source-quality.md` | 來源品質評分規則 |

## 重要約束

- 固定 8 則，幣圈 ≥ 4 則
- 第一則必須是市場概況（BTC/ETH/ETF/恐懼指數）
- 每則 ≥1 專屬來源 URL，不可共用、不可媒體首頁
- 撰稿後用 Python（非 bash heredoc）寫入 `/tmp/boba_daily_tg.txt` 和 `/tmp/boba_daily_x.txt`
- `send --channel official` 必須等使用者確認後才執行

## 目錄結構

```
boba-cli/
├── cli.py              ← 主入口
├── pyproject.toml      ← uv 依賴管理（httpx）
├── .env                ← API keys（自動載入，.env 優先於 shell）
├── scripts/
│   ├── fetch_news.py   ← BlockBeats + OpenNews + Twitter KOL
│   ├── send_tg.py      ← TG 發送 + 存檔
│   └── image.py        ← 生圖 + carousel + sendPhoto
├── prompts/            ← 撰稿規範（從 content-studio 同步）
│   └── news-research/  ← KOL 名冊 + 選題過濾
├── history/            ← 日報存檔（.txt + metadata）
└── output/             ← 圖片輸出
    ├── drafts/         ← AI 底圖（無 overlay）
    └── ig-{MMDD}/      ← Carousel slides
```
