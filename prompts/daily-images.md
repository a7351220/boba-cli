# 日報配圖 + IG Carousel（Phase 5）

> Phase 5 完整流程：AI 生圖 → 16:9 overlay → IG Carousel → 結尾 → IG 文案。

---

## Step 0：構思 Prompt（先想再生）

**核心原則**：場景必須是「有敘事感的廣角環境」，用畫面隱喻新聞主題，**不要把新聞直譯成圖示**（像「BTC 漲 → 多螢幕綠 K 線」這種翻譯題太無聊）。

| 規則 | 說明 |
|------|------|
| 1. 場景氛圍 | 用台灣日常場景的「氛圍」呼應今天新聞的情緒，**不需要一一對應到具體新聞**。只要畫面感覺對了就夠。不要把新聞道具塞進畫面（沒有K線圖、沒有比特幣符號、沒有船模型） |
| 2. 環境為主 | 廣角鏡頭，Pepe **只占畫面 25-30%**，整個場景說故事。**禁止 Pepe 大頭特寫** |
| 3. Pepe 在側 | Pepe 站在右側或左側 1/3，3/4 角度半身，融入場景，不是肖像照 |
| 4. 細節豐富 | 招牌、燈籠、機車、霧氣、街燈、電線、貓、招牌反光、湯鍋蒸氣——讓畫面有層次 |
| 5. 場景輪替 | **每天必須選不同場景**，嚴禁連續兩天用同類型（便利商店 / 騎樓 / 夜市）。見下方場景庫 |

> **每天回顧前 3 天的圖**，場景/時段/光線都要不同。連續兩天同場景類型 = 失敗。

---

## 台灣場景庫（每次從裡面選，不要重複）

每次選場景時，從下方清單選一個**前 3 天都沒用過**的類型，再加入當天的光線和天氣。

**室外街景**
- 傳統市場（菜市場）早晨開市前，攤販在卸貨擺攤
- 夜市巷口，攤販收攤後的清晨清場
- 廟口廣場，早晨有人在拜拜、有香煙
- 學校旁的文具店/早餐店，上學前的清晨人潮
- 老社區巷弄，機車、盆栽、晾衣服、電線桿
- 河濱公園，清晨跑步的人、遠方城市天際線
- 山上茶園梯田，霧氣、早晨陽光斜射
- 漁港碼頭，漁船、海鷗、清晨卸貨
- 台鐵小站月台，等車的人、鐵軌延伸遠方
- 公車站牌，雨天或清晨、少數等車的人

**室內或半室內**
- 傳統早餐店（燒餅油條/蛋餅店），煎台蒸氣
- 麵攤/滷肉飯小店，夜晚或清晨的燈光
- 老理髮廳，轉燈柱、椅子、老鏡子
- 書店或租書店，書架、燈光、安靜的讀者
- 電玩店/柏青哥式遊戲場，霓虹燈、機台聲
- 老茶行，茶罐、木架、溫暖燈光
- 傳統中藥行，大抽屜牆面、老秤
- 捷運站廳（非月台），光線、人流

**時段與天氣多樣化**
- 黎明前（深藍色調）、拂曉（橘紫）、清晨（金黃）、午後（強白光）、傍晚（橘紅）、夜晚（霓虹）
- 晴天、陰天薄霧、梅雨、颱風前夕、冬天冷風

---

## 風格（固定，不輪替）

固定為「Studio Ghibli 風 clean cartoon line illustration」：

```
Clean digital cartoon illustration with bold black outlines,
flat colors with soft cell shading, classic anime/manga linework,
Studio Ghibli style cozy atmosphere, rich environmental detail.
```

**禁用畫風關鍵字**（會破壞品質與角色辨識度）：
- ❌ `chibi` / `kawaii super-deformed` / `giant head small body`
- ❌ `manga panel composition` / `speed lines` / `film grain`
- ❌ `cinematic 35mm photography` / `cyberpunk neon` / `watercolor` / `pixel art` / `ukiyo-e`

**參考圖必看**：`boba/output/daily-0327-final.png`、`daily-0330-final.png`、`daily-0407-final.png`

---

## Pepe 角色 Lock（每次必加，不可省）

Pepe 不是普通綠青蛙。**Model 預設「frog=綠色」會把 Pepe 畫錯**，所以 prompt 必須強制鎖死：

```
Boba Pepe (matching the first 3 reference images exactly):
BEIGE/TAN/CREAM colored body and head (NOT GREEN, NOT a normal frog),
LARGE irregular dark brown cow-like patches/spots scattered across head and body,
very large round white eyes with large black round pupils and white sparkle reflections,
a LONG horizontal orange beak/snout extending forward (like a duckbill),
dark brown hooded sweatshirt, plump round body, classic Pepe proportions.
ONLY ONE Pepe in the entire frame, no duplicates.
```

**結尾固定加 negative anchor**：
```
CRITICAL: Pepe is BEIGE with brown spots and a LONG ORANGE BEAK,
NOT a green frog, NOT a generic cute cartoon frog. ONLY ONE Pepe.
```

---

## Penny 電視主播彩蛋（固定）

Penny 用 ref 圖鎖定 + 出現在背景電視/螢幕內，**不要做成卡通人物坐 Pepe 旁邊**。

```
Through one of the convenience store / cafe windows, a wall-mounted TV
inside shows a financial news broadcast.
CRITICAL: The news anchor on the TV is a cartoon portrait of the specific
young Asian woman from the penny1 and penny2 reference images —
same delicate face, long straight dark hair with bangs, gentle expression —
drawn in the same cartoon style with bold outlines, sitting at a typical
newsroom desk.
```

---

## Prompt 完整模板

```
Wide cinematic environment shot of {台灣場景} at {時段}, in clean digital
cartoon illustration with bold black outlines, Studio Ghibli style cozy
atmosphere. The composition is ENVIRONMENT-FOCUSED — the wide scene takes
up most of the frame, with rich atmospheric details.

ONLY ONE small character — Boba Pepe — standing on the {左/右} side of the
frame, occupying ONLY about 25-30% of the frame width, integrated INTO the
scene, NOT a close-up, NOT a face shot. Shown from a slight 3/4 angle,
half-body visible. He is {動作 — 拿珍奶/吃早餐/騎機車/看遠方} with a
{表情 — 期待/平靜/疑惑/緊張} expression.

[Pepe 角色 lock 段落 — 見上方]

THE SCENE: {細節豐富的場景描述 — 招牌、燈、機車、霧氣、店家、街景}.
{敘事道具 — 用畫面隱喻今日新聞 hook}.

[Penny 電視主播段落 — 見上方]

Mood: {氛圍詞 — 期待/不安/疲憊/振奮}.
Color palette: {主色調 — 拂曉橘紫/深夜霓虹/雨夜冷色}.

[結尾固定 negative anchor — 見上方]

Absolutely NO text NO numbers NO labels NO words NO logos.
```

**參考圖固定 5 張**：`pepe3.png` `pepe.png` `pepe4.png` `penny1.jpg` `penny2.jpg`
（已內建在 `scripts/boba/generate-daily-image.sh`）

---

## Step 1 + 2：生成 16:9 底圖 + 疊加品牌 overlay

```bash
cd /Users/xieminghua/content-studio
./scripts/boba/generate-daily-image.sh {MMDD} "{M/DD}" "{Step 0 的 prompt}"
```

> 腳本自動處理：API key、5 張 ref（pepe×3 + penny×2）、AI 生圖（Flash, 重試 3 次）、overlay 疊加。
> 產出：`boba/output/daily-{MMDD}-final.png`

**硬性規則**：用 Flash（$0.039），禁止 Pro。失敗重試同 model 最多 3 次。

---

## Step 3：生成 IG Carousel

**先生成 4:5 底圖**（同 Step 0 prompt，改 `--ar 4:5`）：
```bash
npx -y bun scallop/.agents/skills/baoyu-image-gen/scripts/main.ts \
  --prompt "{同 Step 0}" \
  --ref boba/img/pepe3.png boba/img/pepe.png boba/img/pepe4.png \
        boba/img/penny1.jpg boba/img/penny2.jpg \
  --provider google --model gemini-3.1-flash-image-preview \
  --ar 4:5 --imageSize 1K \
  --image boba/output/drafts/daily-{MMDD}-ig-base.png
```

**跑 carousel 腳本**：
```bash
cd /Users/xieminghua/content-studio/boba
python3 scripts/daily-ig-carousel.py \
  /tmp/boba_daily_x.txt \
  output/drafts/daily-{MMDD}-ig-base.png \
  "{M/DD}" \
  output/ig-{MMDD}/
```

**設計風格**（HTML/CSS，固定不改）：
- 全屏背景：AI 底圖 blur(10px) + brightness(0.28)
- 前景白字：標題 44px bold + 段落 29px regular
- 珊瑚粉 accent：badge `#FF8374` + divider
- 底部品牌列：BOBA DAO logo + 珍奶科技日報 + @bobadao_lfg + 頁碼
- 封面：4:5 AI 圖 + 漸層 + 日期 badge + hook 標題 + 滑動提示

**產出**：`slide-00-cover.png` ~ `slide-08.png`

---

## Step 4：結尾 slide

固定模板，可直接複製上次的 `slide-ending.png`：
```bash
cp boba/output/ig-{前一天MMDD}/slide-ending.png boba/output/ig-{MMDD}/
```

---

## Step 5：IG 文案

```
🧋 珍奶科技日報 BOBA Daily｜{M/DD}

{hook 摘要}

今天 {N} 則重點整理好了，滑過去看 👉

1️⃣ {標題1}
...
8️⃣ {標題8}

💬 你最關注哪一則？留言告訴我們！
📲 完整版每日快報 → Telegram @bobadaolfg（連結在 bio）

·
·
·

#加密貨幣 #比特幣 #BTC #區塊鏈 #投資理財 #每日新聞 #幣圈日報 #DeFi #Web3 #台灣投資 #BOBADAO #珍奶科技日報 #crypto #bitcoin #{當天關鍵字}
```

**存檔**：`boba/output/ig-{MMDD}/ig-caption.txt`

---

## 發送到 TG

依序發到 @test3635：
1. 16:9 主圖用 `sendPhoto`
2. carousel slides（封面 + 8 內容 + 結尾）用 `sendPhoto`
3. IG 文案用 `sendMessage`

**用 `timeout=120000` 以上**避免被系統自動放到背景，被放到背景就**等 task-notification 確認狀態**再決定是否重試，**絕不在沒確認前次失敗就重發**。

---

## 配圖約束總表

- ✅ 必須帶 5 張 ref（pepe×3 + penny×2），腳本已內建
- ✅ Pepe 占畫面 25-30%，**禁止大頭特寫**
- ✅ 場景隱喻新聞主題，**禁止直接畫圖表/螢幕**
- ✅ Pepe 角色 lock 段落 + negative anchor 必加
- ✅ Penny 必須在背景電視/螢幕當主播
- ✅ prompt 結尾必加 `NO text NO labels NO words`
- ✅ 用 `--imageSize 1K`、`--model gemini-3.1-flash-image-preview`
- ✅ overlay / HTML 模板固定，不改設計
