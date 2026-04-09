#!/bin/bash
# BOBA CLI 環境安裝腳本（macOS + Ubuntu）
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

ok()   { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
fail() { echo -e "${RED}❌ $1${NC}"; exit 1; }
step() { echo -e "\n${YELLOW}▶ $1${NC}"; }

# ── 偵測作業系統 ─────────────────────────────────────────────
if [[ "$OSTYPE" == "darwin"* ]]; then
  OS="macos"
elif [[ -f /etc/os-release ]] && grep -qi ubuntu /etc/os-release; then
  OS="ubuntu"
else
  fail "不支援的作業系統（僅支援 macOS / Ubuntu）"
fi

echo "=============================="
echo "  BOBA CLI 環境安裝（$OS）"
echo "=============================="

# ── 1. 套件管理器 ────────────────────────────────────────────
if [[ "$OS" == "macos" ]]; then
  step "檢查 Homebrew"
  if ! command -v brew &>/dev/null; then
    warn "Homebrew 未安裝，正在安裝..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    [ -f /opt/homebrew/bin/brew ] && eval "$(/opt/homebrew/bin/brew shellenv)"
  fi
  ok "Homebrew $(brew --version | head -1)"
else
  step "更新 apt"
  sudo apt-get update -qq
  ok "apt 已更新"
fi

# ── 2. uv ─────────────────────────────────────────────────────
step "檢查 uv（Python 套件管理）"
if ! command -v uv &>/dev/null; then
  warn "uv 未安裝，正在安裝..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
ok "uv $(uv --version)"

# ── 3. ImageMagick ────────────────────────────────────────────
step "檢查 ImageMagick"
if ! command -v magick &>/dev/null; then
  warn "ImageMagick 未安裝，正在安裝..."
  if [[ "$OS" == "macos" ]]; then
    brew install imagemagick
  else
    sudo apt-get install -y imagemagick
  fi
fi
ok "ImageMagick $(magick --version | head -1)"

# ── 4. Node.js ────────────────────────────────────────────────
step "檢查 Node.js"
if ! command -v node &>/dev/null; then
  warn "Node.js 未安裝，正在安裝..."
  if [[ "$OS" == "macos" ]]; then
    brew install node
  else
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
  fi
fi
ok "Node.js $(node --version)"

# ── 5. Bun ────────────────────────────────────────────────────
step "檢查 Bun"
if ! command -v bun &>/dev/null; then
  warn "Bun 未安裝，正在安裝..."
  curl -fsSL https://bun.sh/install | bash
  export PATH="$HOME/.bun/bin:$PATH"
fi
ok "Bun $(bun --version)"

# ── 6. Chrome / Chromium ─────────────────────────────────────
step "檢查 Chrome / Chromium"
if [[ "$OS" == "macos" ]]; then
  CHROME_PATH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  if [ ! -f "$CHROME_PATH" ]; then
    warn "找不到 Google Chrome，安裝 Chromium..."
    brew install --cask chromium 2>/dev/null || warn "請手動安裝 Google Chrome：https://www.google.com/chrome/"
  else
    ok "Google Chrome 已安裝"
  fi
else
  if ! command -v google-chrome &>/dev/null && ! command -v chromium-browser &>/dev/null && ! command -v chromium &>/dev/null; then
    warn "安裝 Chromium..."
    sudo apt-get install -y chromium-browser 2>/dev/null || \
    sudo apt-get install -y chromium 2>/dev/null || \
    warn "請手動安裝 Chromium：sudo apt install chromium-browser"
  else
    ok "Chrome/Chromium 已安裝"
  fi
  # Ubuntu headless 需要這些
  sudo apt-get install -y \
    libgconf-2-4 libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libasound2 2>/dev/null || true
fi

# ── 7. Python 依賴（httpx）────────────────────────────────────
step "安裝 Python 依賴"
cd "$REPO_DIR"
uv sync
ok "Python 依賴安裝完成"

# ── 8. 字型（Noto Sans TC）────────────────────────────────────
step "檢查字型"
FONT_DIR="$REPO_DIR/img/fonts"
FONT_FILE="$FONT_DIR/NotoSansTC.ttf"
mkdir -p "$FONT_DIR"
if [ ! -f "$FONT_FILE" ]; then
  warn "下載 Noto Sans TC 字型..."
  curl -fsSL \
    "https://github.com/google/fonts/raw/main/ofl/notosanstc/NotoSansTC%5Bwght%5D.ttf" \
    -o "$FONT_FILE"
  ok "字型下載完成：$FONT_FILE"
else
  ok "字型已存在：$FONT_FILE"
fi

# ── 9. .env 設定 ──────────────────────────────────────────────
step "檢查 .env"
ENV_FILE="$REPO_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
  cp "$REPO_DIR/.env.example" "$ENV_FILE"
  echo ""
  warn ".env 已從範本建立，請填入以下 Token："
  echo ""
  echo "  編輯：nano $ENV_FILE"
  echo ""
  echo "  必填項目："
  echo "    TELEGRAM_BOT_TOKEN   — TG Bot Token（@BotFather 取得）"
  echo "    GEMINI_API_KEY       — Google AI Studio 取得"
  echo "    BLOCKBEATS_API_KEY   — BlockBeats API"
  echo "    OPENNEWS_TOKEN       — OpenNews Token"
  echo "    TWITTER_TOKEN        — Twitter/X Token"
  echo ""
else
  ok ".env 已存在"
fi

# ── 完成 ──────────────────────────────────────────────────────
echo ""
echo "=============================="
ok "安裝完成！"
echo "=============================="
echo ""
echo "快速測試："
echo "  uv run python3 cli.py status"
echo ""
echo "如果 .env 已填好，直接跑日報："
echo "  uv run python3 cli.py fetch"
echo ""
