#!/bin/bash
# Skills Plugin - Installation Script
# Run with: ./scripts/install.sh

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           Skills Plugin - Installation Script                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}📁 Project root:${NC} $PROJECT_ROOT"
echo ""

# =============================================================================
# Check Python Version
# =============================================================================
echo -e "${BLUE}🐍 Checking Python version...${NC}"

# Find best available Python
PYTHON_CMD=""
for cmd in python3.12 python3.11 python3.10 python3; do
    if command -v $cmd &> /dev/null; then
        version=$($cmd -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        major=$(echo $version | cut -d. -f1)
        minor=$(echo $version | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
            PYTHON_CMD=$cmd
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}❌ Python 3.10+ is required but not found.${NC}"
    echo ""
    echo "Please install Python 3.10 or higher:"
    echo "  macOS:   brew install python@3.12"
    echo "  Ubuntu:  sudo apt install python3.12"
    echo "  Windows: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version)
echo -e "${GREEN}✓ Found: $PYTHON_VERSION ($PYTHON_CMD)${NC}"
echo ""

# =============================================================================
# Check pip
# =============================================================================
echo -e "${BLUE}📦 Checking pip...${NC}"

if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo -e "${YELLOW}⚠ pip not found, installing...${NC}"
    $PYTHON_CMD -m ensurepip --upgrade
fi

PIP_VERSION=$($PYTHON_CMD -m pip --version)
echo -e "${GREEN}✓ $PIP_VERSION${NC}"
echo ""

# =============================================================================
# Install Dependencies
# =============================================================================
echo -e "${BLUE}📥 Installing Python dependencies...${NC}"
echo ""

$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r "$PROJECT_ROOT/requirements.txt"

echo ""
echo -e "${GREEN}✓ Dependencies installed successfully!${NC}"
echo ""

# =============================================================================
# Verify Installation
# =============================================================================
echo -e "${BLUE}🔍 Verifying installation...${NC}"
echo ""

# Test imports
FAILED=0

test_import() {
    local module=$1
    local name=$2
    if $PYTHON_CMD -c "import $module" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $name"
    else
        echo -e "  ${RED}✗${NC} $name - import failed"
        FAILED=1
    fi
}

test_import "google.genai" "google-genai (AI generation)"
test_import "matplotlib" "matplotlib (chart generation)"
test_import "numpy" "numpy (data processing)"
test_import "pptx" "python-pptx (slide generation)"
test_import "PIL" "Pillow (image processing)"

echo ""

if [ $FAILED -eq 1 ]; then
    echo -e "${RED}❌ Some packages failed to install. Please check the errors above.${NC}"
    exit 1
fi

# =============================================================================
# Check Optional: ffmpeg
# =============================================================================
echo -e "${BLUE}🎬 Checking optional tools...${NC}"
echo ""

if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -n1)
    echo -e "  ${GREEN}✓${NC} ffmpeg - $FFMPEG_VERSION"
else
    echo -e "  ${YELLOW}⚠${NC} ffmpeg not found (needed for media-utils)"
    echo "     Install with: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)"
fi

echo ""

# =============================================================================
# Check API Keys
# =============================================================================
echo -e "${BLUE}🔑 Checking API keys...${NC}"
echo ""

# Load .env files
for envfile in "$PROJECT_ROOT/.env" "$HOME/.config/skills/.env" "$HOME/.env"; do
    if [ -f "$envfile" ]; then
        source "$envfile" 2>/dev/null || true
    fi
done

check_key() {
    local key=$1
    local name=$2
    local url=$3
    if [ -n "${!key}" ]; then
        echo -e "  ${GREEN}✓${NC} $key is set"
    else
        echo -e "  ${YELLOW}○${NC} $key not set (optional)"
        echo "     Get key: $url"
    fi
}

check_key "GOOGLE_API_KEY" "Google AI" "https://aistudio.google.com/apikey"
check_key "OPENAI_API_KEY" "OpenAI" "https://platform.openai.com/api-keys"
check_key "ELEVENLABS_API_KEY" "ElevenLabs" "https://elevenlabs.io"
check_key "FAL_KEY" "Fal.ai" "https://fal.ai/dashboard/keys"

echo ""

# =============================================================================
# Done
# =============================================================================
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           ✓ Installation Complete!                          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Next steps:"
echo "  1. Set up API keys in .env (copy from env.example)"
echo "  2. Restart Claude Code to reload the plugin"
echo "  3. Try: 'generate an image of a sunset'"
echo ""
