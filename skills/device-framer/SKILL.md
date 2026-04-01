---
name: device-framer
description: Wrap screen recordings and screenshots in photorealistic iPhone device frames with drop shadow and background. Use this skill whenever the user uploads a screen recording (MP4, MOV, etc.) or screenshot (PNG, JPG, etc.) and wants it placed inside a phone mockup, device frame, or device bezel. Also trigger when the user mentions "device frame", "phone mockup", "iPhone frame", "app demo", "wrap in device", "Screen Studio", "mockup video", "app store screenshot", or wants to make a screen recording or screenshot look polished/professional. Supports 12 iPhone models from iPhone 13 mini to iPhone 17 Pro Max with 44 color variants. Handles both video (ffmpeg) and image (Pillow) inputs automatically.
---

# Device Framer

Wraps screen recordings and screenshots in photorealistic iPhone device frames with drop shadow, rounded corners, and a configurable background. Supports 12 devices with 44 color variants.

## Quick Start

```bash
SKILL_DIR="/path/to/this/skill"
cp -r "$SKILL_DIR/scripts" /home/claude/device-framer-scripts
cp -r "$SKILL_DIR/frames" /home/claude/device-framer-frames
pip install Pillow --break-system-packages 2>/dev/null || true

python3 /home/claude/device-framer-scripts/frame_video.py INPUT_FILE \
  -o /mnt/user-data/outputs/framed_output.mp4 \
  -d iphone-16-pro --color black-titanium --bg '#0a0a0a' \
  --padding 100 --scale 0.5
```

Auto-detects video vs image from extension. Video → MP4, Image → PNG.

## Available Devices

| Device | Colors |
|--------|--------|
| `iphone-17-pro-max` | cosmic-orange, deep-blue, silver |
| `iphone-17-pro` | cosmic-orange, deep-blue, silver |
| `iphone-16-pro-max` | black-titanium, natural-titanium, white-titanium, desert-titanium |
| `iphone-16-pro` *(default)* | black-titanium, natural-titanium, white-titanium, desert-titanium |
| `iphone-16-plus` | black, pink, teal, ultramarine, white |
| `iphone-16` | black, pink, teal, ultramarine, white |
| `iphone-15-pro-max` | black-titanium, natural-titanium, white-titanium, blue-titanium |
| `iphone-14-pro-max` | deep-purple, gold, silver, space-black |
| `iphone-13-mini` | black, blue, pink, red, starlight |
| `iphone-air` | cloud-white, light-gold, sky-blue, space-black |
| `iphone-xs-max` | space-gray |
| `iphone-xs` | space-gray, silver |

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `-d, --device` | `iphone-16-pro` | Device model |
| `--color` | first color | Device color variant |
| `--bg` | `#0a0a0a` | Background color (hex) |
| `--no-shadow` | (shadow on) | Disable drop shadow |
| `--shadow-blur` | `50` | Shadow blur radius |
| `--shadow-opacity` | `80` | Shadow opacity (0-255) |
| `--padding` | `100` | Padding around device (px) |
| `--scale` | (native) | Scale factor (e.g. `0.5`) |
| `-q, --quality` | `high` | Video: `high`/`medium`/`low` |
| `--no-audio` | (keep) | Strip audio (video only) |
| `--list-devices` | — | Show all devices and colors |

## Recommended Settings

**Scale:** `0.5` for most uses. Omit for native resolution.

**Good combos:**
- `--device iphone-17-pro --color cosmic-orange --bg '#1a1a2e'`
- `--device iphone-16-pro --color natural-titanium --bg '#0f172a'`
- `--device iphone-16 --color ultramarine --bg '#0a0a0a'`
- `--device iphone-air --color sky-blue --bg '#f0f4f8'`
- `--device iphone-14-pro-max --color deep-purple --bg '#0a0a0a'`

## How It Works

Frame PNGs have transparent screen areas. The script extracts a pixel-perfect screen mask from each frame's alpha channel (flood-fill to separate interior screen from exterior transparency), then composites: background → shadow → content (masked) → frame overlay.

**Images:** Pillow compositing (instant). **Videos:** ffmpeg filter_complex single-pass.

## Interaction Guide

1. Auto-detect input type from extension
2. If user doesn't specify a device, ask or default to iPhone 16 Pro
3. If user doesn't specify color, use the default (first listed)
4. Recommend `--scale 0.5` and dark background
5. Run the script, present the output

## Credits

- Modern frames from [jamesjingyi/mockup-device-frames](https://github.com/jamesjingyi/mockup-device-frames) (Apple Developer Resources)
- Classic XS/XS Max frames from [t9mike/iphone_overlay](https://github.com/t9mike/iphone_overlay) (Apache 2.0)
