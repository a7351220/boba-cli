# KOL 名冊

> 本檔案為 `news-research` Skill 的補充資料。
> 主流程請參考 `SKILL.md`。

---

## 全量名冊（每次 SCAN/TRACK 都掃）

> 來源：使用者的 Twitter list `@minghua6699/news`，目前 21 個帳號。
> 所有消費端 Skill 引用此名冊，不再各自維護 KOL 列表。

| # | 帳號 | 名稱 | 類型 | 價值 | API 備註 |
|---|------|------|------|------|---------|
| 1 | `KobeissiLetter` | The Kobeissi Letter | 宏觀市場分析 | 數據圖表、市場評論、趨勢統計，資料密度極高 | ✅ `get_twitter_user_tweets` |
| 2 | `tradfi` | tradfi news | 即時新聞速報 | 彭博/路透等級的 breaking headlines，宏觀+地緣 | ✅ `get_twitter_user_tweets` |
| 3 | `EricBalchunas` | Eric Balchunas | ETF 專家 | Bloomberg Senior ETF Analyst，ETF 審批/資金流第一手 | ✅ `get_twitter_user_tweets` |
| 4 | `JSeyff` | James Seyffart | ETF/加密分析 | Bloomberg ETF + Crypto analyst，機構動向 | ✅ `get_twitter_user_tweets` |
| 5 | `EleanorTerrett` | Eleanor Terrett | 加密監管記者 | 前 Fox Business，SEC/CFTC 監管動態第一手 | ✅ `get_twitter_user_tweets` |
| 6 | `DegenerateNews` | DEGEN NEWS | 加密新聞速報 | 加密產業新聞 + Polymarket 驅動，速度快 | ✅ `get_twitter_user_tweets` |
| 7 | `LDNCryptoClub` | LondonCryptoClub | 加密宏觀分析 | 44 年央行/宏觀交易經驗，BTC 宏觀敘事 | ⚠️ 需用 `search_twitter_advanced(from_user=...)` |
| 8 | `aixbt_agent` | aixbt | AI Agent 分析 | AI 自動分析加密市場，鏈上數據+協議營收 | ✅ `get_twitter_user_tweets` |
| 9 | `DefiantNews` | The Defiant | DeFi 媒體 | DeFi 深度報導、協議更新、開發者訪談 | ✅ `get_twitter_user_tweets` |
| 10 | `followin_io_zh` | Followin 中文 | 中文加密聚合 | 加密新聞聚合+KOL 觀點整理，華語視角 | ✅ `get_twitter_user_tweets` |
| 11 | `lanhubiji` | 藍狐筆記 | 中文加密分析 | 長期價值投資視角、敘事分析、生態觀察 | ✅ `get_twitter_user_tweets` |
| 12 | `BinanceResearch` | Binance Research | 機構研究 | 幣安研究院，月報/專題報告/數據分析，機構級深度 | ✅ `get_twitter_user_tweets` |
| 13 | `WSJmarkets` | WSJ Markets | TradFi 市場 | 華爾街日報市場版，美股/債券/商品即時新聞 | ✅ `get_twitter_user_tweets` |
| 14 | `BitcoinMagazine` | Bitcoin Magazine | BTC 媒體 | BTC 生態新聞、ETF 動態、機構買入速報 | ✅ `get_twitter_user_tweets` |
| 15 | `alphanonceStaff` | alphanonce Intern | 量化/宏觀分析 | 深度量化觀點、Druckenmiller 等大佬追蹤 | ⚠️ 需用 `search_twitter_advanced(from_user=...)` |
| 16 | `dlnews` | DL News | 加密媒體 | 加密貨幣 & DeFi 新聞分析，準確客觀 | ✅ `get_twitter_user_tweets` |
| 17 | `MilkRoad` | Milk Road | 加密/宏觀/AI | Crypto、macro、AI 投資資訊，受眾廣 | ✅ `get_twitter_user_tweets` |
| 18 | `HYPERDailyTK` | Hyperliquid Daily | Hyperliquid 生態 | HYPE 生態日報、交易數據、空投追蹤 | ✅ `get_twitter_user_tweets` |
| 19 | `WatcherGuru` | Watcher.Guru | 加密/金融速報 | 全方位加密 & 金融即時新聞，速度快 | ✅ `get_twitter_user_tweets` |
| 20 | `testingcatalog` | TestingCatalog News | AI 新聞 | AI 產品動態報導，虛擬助理驅動 | ✅ `get_twitter_user_tweets` |
| 21 | `WuBlockchain` | Wu Blockchain | 亞洲加密新聞 | Colin Wu 吳說區塊鏈，亞洲加密重要新聞 | ✅ `get_twitter_user_tweets` |

### 已移除（2026-03-30 精簡）

| 帳號 | 移除原因 |
|------|---------|
| `tier10k` | 活躍度極低，最後有料推 3/10 |
| `breadnbutter247` | 已停更，最後發文 2025 年 12 月 |
| `definalist` | 發文稀疏，內容價值低 |
| `BlockBeatsAsia` | 跟 BlockBeats 快訊（L1b）完全重複 |
| `TechFlowPost` | 只貼連結無內文，無法提取資訊 |
| `MuyaoShen` | 發文極少，多數是個人生活 |

---

## API 呼叫策略

```
For each kol in 全量名冊:
  If API 備註 == "✅":
    get_twitter_user_tweets(username=kol, limit=15)
  Else (⚠️ 帳號):
    search_twitter_advanced(from_user=kol, limit=15, product="Latest")
```

---

## 動態補充（依當週人物新增）

除了固定名冊，依當週新聞中出現的關鍵人物，用 `search_twitter_advanced` 動態搜尋：
- 例：Arthur Hayes（`CryptoHayes`）、Michael Saylor（`saylor`）、SEC Chair、Fed 相關人物
- 這些不在固定名冊中，但可依需求臨時加入搜尋
