#!/usr/bin/env bash
# scan_coindesk.sh — 用 agent-browser 抓 CoinDesk 頭條 + 全文
#
# 用法:
#   bash scripts/scan_coindesk.sh                    # 只抓標題（快，~10s）
#   bash scripts/scan_coindesk.sh --full             # 標題 + 全文
#   bash scripts/scan_coindesk.sh --full --top 10    # 只讀前 10 篇全文
#   bash scripts/scan_coindesk.sh --read URL         # 讀單篇全文
#
# 輸出: /tmp/boba_coindesk_candidates.json

set -euo pipefail
export CHROME_PATH=/usr/bin/chromium
AB="npx agent-browser"

FULL=false
TOP=25
READ_URL=""
OUT="/tmp/boba_coindesk_candidates.json"
TMP="/tmp/_coindesk_article.json"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --full)  FULL=true; shift ;;
    --top)   TOP="$2"; shift 2 ;;
    --read)  READ_URL="$2"; shift 2 ;;
    -o)      OUT="$2"; shift 2 ;;
    *)       OUT="$1"; shift ;;
  esac
done

# JS to extract article content (single line, returns JSON string)
EXTRACT='(()=>{const h=(document.querySelector("h1")||{}).textContent||"";const te=document.querySelector("time");const t=te?te.getAttribute("datetime")||"":"";const ps=[...document.querySelectorAll(".document-body p, article p, [data-module-name] p")].map(p=>p.textContent.trim()).filter(t=>t.length>20&&!t.includes("Disclosure")&&!t.includes("editorial policies")&&!t.includes("CoinDesk is an award")&&!t.includes("Bullish (NYSE")&&!t.includes("set of principles"));return JSON.stringify({title:h.trim(),time:t,paragraphs:ps.length,words:ps.join(" ").split(/\s+/).length,body:ps.join("\n\n")})})()'

# Read article: open URL, eval extract, save to file
read_article() {
  local url="$1" outfile="$2"
  $AB open "$url" >/dev/null 2>&1
  local raw
  raw=$($AB eval "$EXTRACT" 2>/dev/null || echo '""')
  node -e "
    let s = process.argv[1];
    if (s.startsWith('\"')) try { s = JSON.parse(s); } catch(e) {}
    let d; try { d = JSON.parse(s); } catch(e) { d = {}; }
    require('fs').writeFileSync(process.argv[2], JSON.stringify(d, null, 2));
  " "$raw" "$outfile"
}

# ── --read: single article ─────────────────────────────────
if [[ -n "$READ_URL" ]]; then
  echo "📖 Reading: $READ_URL" >&2
  read_article "$READ_URL" "$TMP"
  node -e "
    const d = JSON.parse(require('fs').readFileSync(process.argv[1], 'utf8'));
    console.log('📰 ' + (d.title || '(no title)'));
    console.log('📅 ' + (d.time || ''));
    console.log('📊 ' + (d.paragraphs||0) + ' paragraphs, ' + (d.words||0) + ' words');
    console.log('─'.repeat(60));
    console.log(d.body || '(empty)');
  " "$TMP"
  $AB close >/dev/null 2>&1 || true
  rm -f "$TMP"
  exit 0
fi

# ── Headline scan ──────────────────────────────────────────
echo "🌐 Opening CoinDesk..." >&2
$AB open https://www.coindesk.com >/dev/null 2>&1

echo "📜 Scrolling..." >&2
$AB scroll down 1500 >/dev/null 2>&1
sleep 1

echo "🔍 Extracting headlines..." >&2
RAW=$($AB eval 'JSON.stringify([...document.querySelectorAll("a")].filter(a=>{const h=a.href,t=(a.textContent||"").trim();return h.includes("coindesk.com/")&&t.length>30&&!h.includes("/tag/")&&!h.includes("/author/")&&!h.includes("/price/")&&!h.includes("/video/")&&!h.includes("/press-release/")&&!h.includes("/sponsored")&&!h.includes("/research")&&!h.includes("/videos/")&&h.match(/\/\d{4}\/\d{2}\/\d{2}\//)}).map(a=>({title:(a.textContent||"").trim().split("\n").map(s=>s.trim()).filter(s=>s.length>0).join(" "),url:a.href})).filter((v,i,arr)=>arr.findIndex(x=>x.url===v.url)===i).slice(0,'"$TOP"'))' 2>/dev/null)

RAW=$(echo "$RAW" | sed 's/^"//;s/"$//' | sed 's/\\"/"/g' | sed 's/\\\\/\\/g')

echo "📦 Parsing..." >&2
node -e "
const raw = JSON.parse(process.argv[1]);
const results = raw.map(item => {
  const full = item.title;
  const parts = full.split(/(?<=[a-z.?!])(?=[A-Z][a-z])/);
  const title = parts[0].trim();
  const content = parts.slice(1).join('').trim();
  const dm = item.url.match(/\/(\d{4})\/(\d{2})\/(\d{2})\//);
  const date = dm ? dm[1]+'-'+dm[2]+'-'+dm[3] : '';
  const cm = item.url.match(/coindesk\.com\/(\w+)\//);
  const category = cm ? cm[1] : 'unknown';
  return { source:'coindesk-web', title, content, url:item.url, date, category, body:'' };
});
require('fs').writeFileSync(process.argv[2], JSON.stringify(results, null, 2));
console.log('✅ ' + results.length + ' articles extracted');
results.forEach((r,i) => console.log('  ' + (i+1) + '. [' + r.category + '] ' + r.title));
" "$RAW" "$OUT" >&2

# ── --full: read each article body ─────────────────────────
if [[ "$FULL" == "true" ]]; then
  echo "" >&2
  echo "📖 Reading full articles..." >&2
  COUNT=$(node -e "console.log(JSON.parse(require('fs').readFileSync('$OUT','utf8')).length)")
  FILLED=0

  for i in $(seq 0 $((COUNT - 1))); do
    INFO=$(node -e "const d=JSON.parse(require('fs').readFileSync('$OUT','utf8'))[$i];console.log(d.url+'|||'+d.title.slice(0,55))")
    URL="${INFO%%|||*}"
    TITLE="${INFO##*|||}"
    echo "  [$((i+1))/$COUNT] $TITLE..." >&2

    read_article "$URL" "$TMP" 2>/dev/null || true

    node -e "
      try {
        const a = JSON.parse(require('fs').readFileSync(process.argv[1],'utf8'));
        const d = JSON.parse(require('fs').readFileSync(process.argv[2],'utf8'));
        const i = parseInt(process.argv[3]);
        if (a.body) { d[i].body = a.body; d[i].word_count = a.words||0; }
        require('fs').writeFileSync(process.argv[2], JSON.stringify(d, null, 2));
      } catch(e) {}
    " "$TMP" "$OUT" "$i" 2>/dev/null || true

    HAS=$(node -e "try{console.log(JSON.parse(require('fs').readFileSync('$OUT','utf8'))[$i].body?1:0)}catch(e){console.log(0)}")
    [[ "$HAS" == "1" ]] && FILLED=$((FILLED + 1))
  done

  echo "" >&2
  echo "✅ Full text: $FILLED/$COUNT articles" >&2
fi

$AB close >/dev/null 2>&1 || true
rm -f "$TMP"
echo "📄 Output: $OUT" >&2
