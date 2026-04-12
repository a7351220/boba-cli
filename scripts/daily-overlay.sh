#!/bin/bash
# BOBA Daily overlay — boba-cli 本地版
set -e
BASE_IMAGE="$1"; DATE="$2"; OUTPUT="${3:-${BASE_IMAGE%.png}-final.png}"
[ -z "$BASE_IMAGE" ] || [ -z "$DATE" ] && { echo "用法：$0 <base_image> <date> [output]"; exit 1; }
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOGO_SVG="$SCRIPT_DIR/../img/blue.webp"
FONT_MEDIUM="$SCRIPT_DIR/../img/fonts/NotoSansTC.ttf"
FONT_LIGHT="$SCRIPT_DIR/../img/fonts/NotoSansTC.ttf"
WIDTH=1280; HEIGHT=720
RESIZED_TMP="/tmp/boba_overlay_resized_$$.png"
# 偵測底圖比例：如果是直式，用模糊背景填充而非硬裁
SRC_DIMS=$(identify -format "%wx%h" "$BASE_IMAGE")
SRC_W=${SRC_DIMS%x*}; SRC_H=${SRC_DIMS#*x}
if [ "$((SRC_W * 100 / SRC_H))" -lt 140 ]; then
  # 直式圖：先做模糊放大背景，再把原圖 fit 疊上去
  convert "$BASE_IMAGE" -resize "${WIDTH}x${HEIGHT}^" -gravity center -extent "${WIDTH}x${HEIGHT}" -blur 0x20 -brightness-contrast -30x0 "/tmp/boba_overlay_bg_$$.png"
  convert "/tmp/boba_overlay_bg_$$.png" \
    \( "$BASE_IMAGE" -resize "${WIDTH}x${HEIGHT}" \) \
    -gravity center -composite "$RESIZED_TMP"
  rm -f "/tmp/boba_overlay_bg_$$.png"
else
  # 橫式圖：正常裁切
  convert "$BASE_IMAGE" -resize "${WIDTH}x${HEIGHT}^" -gravity center -extent "${WIDTH}x${HEIGHT}" "$RESIZED_TMP"
fi
BAR_HEIGHT=$((HEIGHT*25/100))
LOGO_HEIGHT=$((BAR_HEIGHT*20/100))
TITLE_SIZE=$((BAR_HEIGHT*16/100))
DATE_SIZE=$((BAR_HEIGHT*12/100))
LOGO_TMP="/tmp/boba_overlay_logo_$$.png"
EMOJI_SRC="$SCRIPT_DIR/../img/boba-emoji.png"
EMOJI_SIZE=$((TITLE_SIZE + 4))
EMOJI_TMP="/tmp/boba_overlay_emoji_$$.png"
convert "$LOGO_SVG" -background none -trim +repage -resize "x${LOGO_HEIGHT}" "$LOGO_TMP"
convert "$EMOJI_SRC" -background none -resize "${EMOJI_SIZE}x${EMOJI_SIZE}" "$EMOJI_TMP"
# 計算標題文字寬度以定位左右 emoji
TITLE_TEXT="珍奶科技日報 BOBA Daily"
TITLE_W=$(convert -font "$FONT_MEDIUM" -pointsize "$TITLE_SIZE" label:"$TITLE_TEXT" -format "%w" info: 2>/dev/null || echo 400)
EMOJI_OFFSET_X=$(( (TITLE_W / 2) + EMOJI_SIZE / 2 + 8 ))
EMOJI_Y=$((BAR_HEIGHT*22/100 + EMOJI_SIZE/4))
convert "$RESIZED_TMP" \
  \( -size "${WIDTH}x${BAR_HEIGHT}" xc:none \
     -draw "fill rgba(0,0,0,0.85) rectangle 0,$((BAR_HEIGHT*40/100)) ${WIDTH},${BAR_HEIGHT}" \
     -draw "fill rgba(0,0,0,0.6) rectangle 0,$((BAR_HEIGHT*30/100)) ${WIDTH},$((BAR_HEIGHT*40/100))" \
     -draw "fill rgba(0,0,0,0.3) rectangle 0,$((BAR_HEIGHT*20/100)) ${WIDTH},$((BAR_HEIGHT*30/100))" \
     -draw "fill rgba(0,0,0,0.1) rectangle 0,$((BAR_HEIGHT*10/100)) ${WIDTH},$((BAR_HEIGHT*20/100))" \
  \) -gravity south -composite \
  \( "$LOGO_TMP" \) -gravity south -geometry "+0+$((BAR_HEIGHT*45/100))" -composite \
  -gravity south -fill white -font "$FONT_MEDIUM" -pointsize "$TITLE_SIZE" \
  -annotate "+0+$((BAR_HEIGHT*22/100))" "$TITLE_TEXT" \
  \( "$EMOJI_TMP" \) -gravity south -geometry "-${EMOJI_OFFSET_X}+${EMOJI_Y}" -composite \
  \( "$EMOJI_TMP" \) -gravity south -geometry "+${EMOJI_OFFSET_X}+${EMOJI_Y}" -composite \
  -gravity south -fill "rgba(255,255,255,0.6)" -font "$FONT_LIGHT" -pointsize "$DATE_SIZE" \
  -annotate "+0+$((BAR_HEIGHT*7/100))" "${DATE}" \
  "$OUTPUT"
rm -f "$LOGO_TMP" "$RESIZED_TMP" "$EMOJI_TMP"
echo "✅ 日報配圖已生成：$OUTPUT"
