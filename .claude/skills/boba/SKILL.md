# BOBA Daily Skill

觸發：「日報」「跑日報」「今天新聞」「珍奶」「BOBA」

---

## Pipeline

```
fetch → 選題撰稿 → 存檔 → send → image
```

### Step 1 — 抓資料
```bash
uv run python3 cli.py fetch
```
讀 stdout JSON → 確認 blacklist 條數、候選數、KOL 掃描數。

### Step 2 — 選題 + 撰稿
Claude 讀候選 JSON，依序參考：
- `prompts/format.md` — 8 則結構、TG/X 模板、排序原則
- `prompts/tone.md` — BOBA 語氣、禁用語
- `prompts/quality.md` — 品質自檢清單
- `prompts/daily-pipeline.md` — Phase 0-4 完整流程參考

撰稿完成後用 **Python Write 工具**（不用 bash heredoc）存到：
- `/tmp/boba_daily_tg.txt` — TG 長版（含來源連結）
- `/tmp/boba_daily_x.txt` — X 短版（無連結，結尾加 TG 頻道連結）

### Step 3 — 發送
```bash
uv run python3 cli.py send
```
驗編碼 → 發 @test3635（TG + X 版）→ 存 `history/`。

正式頻道需使用者確認後才跑：
```bash
uv run python3 cli.py send --channel official
```

### Step 4 — 配圖
Claude 依 `prompts/daily-images.md` 構思圖片 prompt（場景隱喻，非翻譯題），再執行：
```bash
uv run python3 cli.py image --date MMDD --prompt "..."
```
自動跑：生 16:9 → 裁 4:5 → carousel → sendPhoto @test3635。

---

## 補充來源：CoinDesk Scanner

CoinDesk 是 Tier 1 幣圈媒體但 OpenNews API 沒有覆蓋。用 agent-browser 抓取，可在 Phase 1 選題時補料。

```bash
cd /home/node/boba-cli

# 掃首頁標題 + 摘要（~10s）
bash scripts/scan_coindesk.sh

# 標題 + 每篇全文（~1.5min）
bash scripts/scan_coindesk.sh --full

# 只讀前 N 篇全文
bash scripts/scan_coindesk.sh --full --top 10

# 讀單篇全文
bash scripts/scan_coindesk.sh --read "<coindesk-url>"
```

輸出：`/tmp/boba_coindesk_candidates.json`

欄位：`source`, `title`, `content`（摘要）, `url`, `date`, `category`, `body`（全文）, `word_count`

---

## 快速指令
```bash
uv run python3 cli.py status   # 查今天進度
uv run python3 cli.py fetch    # 抓資料
uv run python3 cli.py send     # 發測試頻道
uv run python3 cli.py image --date MMDD --prompt "..."
bash scripts/scan_coindesk.sh --full --top 10  # CoinDesk 補料
```
