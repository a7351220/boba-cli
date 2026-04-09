#!/bin/bash
# BOBA Daily overlay — boba-cli 本地版
set -e
BASE_IMAGE="$1"; DATE="$2"; OUTPUT="${3:-${BASE_IMAGE%.png}-final.png}"
[ -z "$BASE_IMAGE" ] || [ -z "$DATE" ] && { echo "用法：$0 <base_image> <date> [output]"; exit 1; }
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOGO_SVG="$SCRIPT_DIR/../img/blue.svg"
FONT_MEDIUM="$SCRIPT_DIR/../img/fonts/NotoSansTC.ttf"
FONT_LIGHT="$SCRIPT_DIR/../img/fonts/NotoSansTC.ttf"
WIDTH=1280; HEIGHT=720
RESIZED_TMP="/tmp/boba_overlay_resized_$$.png"
magick "$BASE_IMAGE" -resize "${WIDTH}x${HEIGHT}^" -gravity center -extent "${WIDTH}x${HEIGHT}" "$RESIZED_TMP"
BAR_HEIGHT=$((HEIGHT*25/100))
LOGO_HEIGHT=$((BAR_HEIGHT*20/100))
TITLE_SIZE=$((BAR_HEIGHT*16/100))
DATE_SIZE=$((BAR_HEIGHT*12/100))
LOGO_TMP="/tmp/boba_overlay_logo_$$.png"
magick -background none -density 200 "$LOGO_SVG" -trim +repage -resize "x${LOGO_HEIGHT}" "$LOGO_TMP"
magick "$RESIZED_TMP" \
  \( -size "${WIDTH}x${BAR_HEIGHT}" xc:none \
     -draw "fill rgba(0,0,0,0.85) rectangle 0,$((BAR_HEIGHT*40/100)) ${WIDTH},${BAR_HEIGHT}" \
     -draw "fill rgba(0,0,0,0.6) rectangle 0,$((BAR_HEIGHT*30/100)) ${WIDTH},$((BAR_HEIGHT*40/100))" \
     -draw "fill rgba(0,0,0,0.3) rectangle 0,$((BAR_HEIGHT*20/100)) ${WIDTH},$((BAR_HEIGHT*30/100))" \
     -draw "fill rgba(0,0,0,0.1) rectangle 0,$((BAR_HEIGHT*10/100)) ${WIDTH},$((BAR_HEIGHT*20/100))" \
  \) -gravity south -composite \
  \( "$LOGO_TMP" \) -gravity south -geometry "+0+$((BAR_HEIGHT*45/100))" -composite \
  -gravity south -fill white -font "$FONT_MEDIUM" -pointsize "$TITLE_SIZE" \
  -annotate "+0+$((BAR_HEIGHT*22/100))" "珍奶科技日報 BOBA Daily" \
  -gravity south -fill "rgba(255,255,255,0.6)" -font "$FONT_LIGHT" -pointsize "$DATE_SIZE" \
  -annotate "+0+$((BAR_HEIGHT*7/100))" "${DATE}" \
  "$OUTPUT"
rm -f "$LOGO_TMP" "$RESIZED_TMP"
echo "✅ 日報配圖已生成：$OUTPUT"
