#!/bin/bash
# generate-daily-image.sh — boba-cli 本地版（refs 指向本地 img/）
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MMDD="${1:-}"; DATE_LABEL="${2:-}"; PROMPT="${3:-}"; OUTPUT="${4:-}"

[ -z "$MMDD" ] || [ -z "$DATE_LABEL" ] || [ -z "$PROMPT" ] && {
  echo "用法: $0 <MMDD> <date_label> <prompt> [output_path]"; exit 1; }

DRAFT_PATH="${REPO_ROOT}/output/drafts/daily-${MMDD}.png"
FINAL_PATH="${OUTPUT:-${REPO_ROOT}/output/daily-${MMDD}-final.png}"

# GEMINI_API_KEY：優先從 .env 讀
if [ -z "${GEMINI_API_KEY:-}" ] && [ -f "${REPO_ROOT}/.env" ]; then
  GEMINI_API_KEY=$(grep GEMINI_API_KEY "${REPO_ROOT}/.env" | cut -d= -f2)
  export GEMINI_API_KEY
fi
[ -z "${GEMINI_API_KEY:-}" ] && { echo "GEMINI_API_KEY 未設定"; exit 1; }

REF_1="${REPO_ROOT}/img/pepe3.png"
REF_2="${REPO_ROOT}/img/pepe.png"
REF_3="${REPO_ROOT}/img/pepe4.png"
REF_4="${REPO_ROOT}/img/penny1.jpg"
REF_5="${REPO_ROOT}/img/penny2.jpg"

for ref in "$REF_1" "$REF_2" "$REF_3" "$REF_4" "$REF_5"; do
  [ -f "$ref" ] || { echo "參考圖不存在: $ref"; exit 1; }
done

mkdir -p "$(dirname "$DRAFT_PATH")" "$(dirname "$FINAL_PATH")"

BAOYU="${REPO_ROOT}/tools/baoyu-image-gen/scripts/main.ts"

echo "Step 1: 生成 16:9 底圖..."
MAX_RETRIES=3; RETRY=0
while [ $RETRY -lt $MAX_RETRIES ]; do
  if npx -y bun "$BAOYU" \
    --prompt "$PROMPT" \
    --ref "$REF_1" "$REF_2" "$REF_3" "$REF_4" "$REF_5" \
    --provider google --model gemini-3.1-flash-image-preview \
    --ar 16:9 --imageSize 1K --image "$DRAFT_PATH"; then
    echo "底圖生成成功: $DRAFT_PATH"; break
  fi
  RETRY=$((RETRY+1)); echo "重試 ${RETRY}/${MAX_RETRIES}..."
done
[ $RETRY -eq $MAX_RETRIES ] && { echo "生圖失敗"; exit 1; }

echo "Step 2: 疊加品牌 overlay..."
"${REPO_ROOT}/scripts/daily-overlay.sh" "$DRAFT_PATH" "$DATE_LABEL" "$FINAL_PATH"

echo "✅ 日報配圖完成: $FINAL_PATH"
