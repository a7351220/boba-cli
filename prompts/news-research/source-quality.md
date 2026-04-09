# 來源品質與交叉驗證

> 本檔案為 `news-research` Skill 的補充資料。
> 主流程請參考 `SKILL.md`。

---

## 來源品質分級

### 第一梯隊（優先使用）

| 類別 | 來源 |
|------|------|
| 國際財經 | CNBC, Bloomberg, Reuters, Financial Times, Wall Street Journal |
| 深度分析 | Fortune, CNN Business, The Economist |
| 加密貨幣 | CoinDesk, The Block, BlockBeats（律動）, Crypto.com Research, CoinShares, Messari |
| 研究機構 | Goldman Sachs, Morgan Stanley, Oxford Economics, JPMorgan |
| 台灣 | 經濟日報, 鉅亨網, 財訊, 工商時報 |
| 農業/商品 | Pro Farmer, FAO, AHDB, USDA |

### 第二梯隊（可用但要交叉驗證）

- Substack 研究員 → 觀點有價值但要標明是個人分析
- Twitter/X 上的分析師 → 可以引用觀點但要追到原始數據驗證
- 中文財經媒體的翻譯報導 → 要回去找英文原文確認

### 不要用

- 來源不明的「業內人士透露」
- SEO 農場文章（內容空洞、標題黨、沒有原始來源）
- 超過一週的舊報導（除非做歷史對比）

---

## 交叉驗證規則

| 驗證條件 | 結論 |
|---------|------|
| OpenNews + BlockBeats + Twitter 都提到 | 重要性高，優先推薦 |
| OpenNews + Messari 同時出現 | 重要性高，L1 雙來源交叉驗證已達標 |
| OpenNews + BlockBeats 同時出現 | 重要性高，L1a + L1b 交叉驗證已達標 |
| BlockBeats 重要快訊 + Twitter KOL 發言 | 重要性高，適合做觀點型內容 |
| 只有一個來源但 AI score ≥ 70 或 likes > 500 | 值得推薦 |
| Messari mindshare 24h 飆升但 OpenNews/BlockBeats/Twitter 沒提到 | 新興訊號，用 WebSearch 確認是否有實質事件 |
| BlockBeats 深度文章有報導但 OpenNews 沒有 | 有價值，BlockBeats 原創分析可作為觀點來源 |
| 只有一個來源且 score < 50 | 需要 WebSearch 二次確認 |
| 數字（價格、漲跌幅）在不同來源不一致 | 用 Messari asset metrics、BlockBeats 市場數據或 WebSearch 確認最新值 |
| BlockBeats 情緒指標與 Twitter 輿論方向矛盾 | 有反差價值，適合做對立觀點內容 |

**規則：任何候選主題至少要有 2 層工具的交叉驗證才能推薦。Messari 算獨立一層（L1.5），BlockBeats 快訊/文章算 L1b，BlockBeats 市場數據算 L1.5。**
