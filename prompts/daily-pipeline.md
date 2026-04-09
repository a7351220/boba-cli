# 日報 Pipeline（Phase 0-4）

> 資料蒐集 → 撰稿 → 品檢 → 發送。
> 配圖流程見 `daily-images.md`。

---

## Phase 0 — 讀取前兩天日報 + 建立黑名單（必做）

**開始搜尋前，先讀 `boba/history/` 裡最近兩天的日報。**

- 讀最近 2 天（不是只讀 1 天），避免重複近期已報導的主題
- 產出 **blacklist**：列出前兩天所有已報導事件的關鍵字/主題
- 延續性事件必須有**新進展或新數字**才能放，否則列入 blacklist
- **核心數字重複 = 重複**：即使角度不同，如果 >50% 的關鍵數字跟前兩天相同（例如同一筆交易、同一個成本數據），視為重複，不放
- 前幾天的數字可作為今天「變動幅度」的對照基準

**輸出（內部使用，不顯示給使用者）：**
```
blacklist:
- [事件關鍵字] — 已於 MM/DD 報導，無新進展
...
```

---

## Phase 1 — 資料蒐集 + 選題

> **優先順序：結構化 JSON > 晨掃 Markdown > 自己跑 SCAN。**

### Step 1：檢查現有資料來源

1. **結構化數據中心**：`memory/daily/{YYYY-MM-DD}/crypto.json`、`macro.json`、`tech.json`
2. **晨掃 Markdown**：`memory/morning-scan-{YYYY-MM-DD}.md`
3. **自己跑 SCAN**：若以上都沒有，執行下方完整三波搜尋

> 不論用哪個來源，Phase 1 結束後都必須有足夠候選素材才能進 Phase 2。

### Step 2：三波搜尋（僅在無現有資料時執行）

執行 `news-research` Skill 的 SCAN 模式（Wave 1→2→3），**不可跳步驟**。
詳細 API 呼叫清單和 KOL 名冊見 `news-research` Skill。

### 選題標準
- 時間窗口：前一天 UTC 12:00 ~ 今天早上
- 數字變動優先、影響錢包優先、正負平衡
- **自動排除 Phase 0 blacklist 中的事件**
- **沒有來源 URL 的主題不列入候選**

### 搜尋驗證表（內部記錄）

```
| 層 | 工具 | 呼叫數 | 找到候選數 |
|----|------|--------|-----------|
| L1a | OpenNews | ? | ? |
| L1b | BlockBeats | ? | ? |
| L2 | Twitter KOL | ?/22 | ? |
| L3 | WebSearch | ? | — |
DATA_RICH 佔比：?%
```

> DATA_RICH < 60% 或 KOL < 15/22 → 自動補搜（最多 1 次）。

---

## Phase 2 — 撰稿（只寫 TG 版，Twitter 版自動壓縮）

1. 讀 `tone.md` → 語氣基準
2. 讀 `format.md` → 寫作原則 + 交付格式
4. **逐則檢查 blacklist**：重複且無新進展 → 移除
5. **逐則檢查來源 URL**：每則 ≥1 URL，沒有的不放
6. **固定 8 則**（不多不少）——素材多就整合，不要拆成 9 則。IG Carousel 頁數跟則數綁定，多一則就多一頁，破壞版面一致性
7. 只手寫 **TG 版**（長版，含來源連結）
7. **Twitter/X 版自動壓縮**：從 TG 版機械式產出——保留標題 + 開頭 + 關鍵數字，移除來源連結，每則壓到 2-4 句。不需要另外手寫。

---

## Phase 3 — 自動品質檢查（不問使用者）

讀 `quality-checklist.md` → 逐項自檢，自動修復最多 **2 次**，不需使用者確認。

---

## Phase 4 — 發送（品質 PASS 後）

> **測試頻道 @test3635**：發三則（TG 長版 + Twitter 短版 + 配圖），方便預覽。
> **正式頻道 @bobadaoann**：只發 TG 長版，不發 Twitter 版和配圖。Twitter 版是給 X 用的，配圖是給 IG ���的，發到正式頻道會洗版。
> **容錯規則**：TG 版發送成功 = 主流程完成。Twitter 版或配圖如因 rate limit / error 失敗，記錄原因後繼續後續步驟，不卡住 pipeline。

1. **寫檔**：用 Write 工具（非 bash heredoc）寫入 `/tmp/boba_daily_tg.txt` 和 `/tmp/boba_daily_x.txt`
2. **驗證**：用 Python 檢查 `\ufffd` 數量 = 0，不通過不發送
3. 讀 `send-telegram` Skill → 發送 TG 版 + Twitter 版到 **@test3635**
4. **使用者確認後**，只發 **TG 版**到 **@bobadaoann** 正式頻道（必須等使用者同意）
5. 配圖用 `sendPhoto` API 補發到 **@test3635**（不發正式頻道）
6. **不重複發送**：
   - `sendPhoto` 必須用 `timeout=120000` 以上，避免被系統自動放到背景
   - 如果被放到背景，**等 task-notification 回來確認狀態**再決定是否重試
   - 絕不在沒有確認前次失敗的情況下重發
7. 存檔到 `boba/history/{YYYY-MM-DD}.txt`，末尾附加 metadata

### 存檔 metadata

在歷史檔末尾附加 HTML 註解（TG 不會顯示）：

```html
<!-- BOBA-DAILY-META
search_verified: true
source: {scan | morning-scan | structured-json}
l1a_calls: {OpenNews 呼叫數}
l1b_calls: {BlockBeats 快訊/文章呼叫數}
l2_kol_scanned: {掃描帳號數}/22
l3_calls: {WebSearch 呼叫數}
data_rich_pct: {DATA_RICH 佔比}
blacklist_excluded: {被 blacklist 排除的主題數}
quality_retries: {品質檢查重試次數}
generated: {ISO 8601 時間戳}
-->
```

| 欄位 | 最低要求 |
|------|---------|
| l1a_calls | ≥ 1 |
| l1b_calls | ≥ 1 |
| l2_kol_scanned | ≥ 15/22 |
| data_rich_pct | ≥ 60% |

用晨掃時記錄 `source: morning-scan`，不需滿足 call 數門檻。
**不加 metadata → hook 會擋住存檔。**
