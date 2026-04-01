# Device Framer

Wrap screen recordings and screenshots in photorealistic iPhone device frames with drop shadow and background. A lightweight open-source alternative to the compositing features in Screen Studio.

![Example](https://img.shields.io/badge/devices-12-blue) ![Example](https://img.shields.io/badge/colors-44-green) ![Example](https://img.shields.io/badge/video_%2B_image-supported-orange)

## Features

- **12 iPhone models** from iPhone 13 mini to iPhone 17 Pro Max
- **44 color variants** — titanium, ultramarine, cosmic orange, deep purple, and more
- **Video + image support** — auto-detects from file extension
- **Photorealistic frames** from Apple Developer Resources
- **Drop shadow** with configurable blur and opacity
- **Pixel-perfect masking** — screen mask extracted from each frame's actual alpha channel
- **Background color** — any hex color
- **Scaling** — output at any size from thumbnail to native resolution
- **Audio passthrough** on video

## Quick Start

```bash
# Install dependency
pip install Pillow

# Frame a screenshot
python3 scripts/frame_video.py screenshot.png -o framed.png \
  -d iphone-16-pro --color natural-titanium --bg '#0f172a'

# Frame a screen recording
python3 scripts/frame_video.py recording.mp4 -o framed.mp4 \
  -d iphone-17-pro --color cosmic-orange --bg '#1a1a2e' --scale 0.5
```

## Available Devices

```
$ python3 scripts/frame_video.py --list-devices

iphone-17-pro-max     colors: cosmic-orange, deep-blue, silver
iphone-17-pro         colors: cosmic-orange, deep-blue, silver
iphone-16-pro-max     colors: black-titanium, desert-titanium, natural-titanium, white-titanium
iphone-16-pro         colors: black-titanium, desert-titanium, natural-titanium, white-titanium
iphone-16-plus        colors: black, pink, teal, ultramarine, white
iphone-16             colors: black, pink, teal, ultramarine, white
iphone-15-pro-max     colors: black-titanium, blue-titanium, natural-titanium, white-titanium
iphone-14-pro-max     colors: deep-purple, gold, silver, space-black
iphone-13-mini        colors: black, blue, pink, red, starlight
iphone-air            colors: cloud-white, light-gold, sky-blue, space-black
iphone-xs-max         colors: space-gray
iphone-xs             colors: silver, space-gray
```

## All Options

```
usage: frame_video.py [-h] [-o OUTPUT] [-d DEVICE] [--color COLOR]
                      [--bg BG] [--no-shadow] [--shadow-blur N]
                      [--shadow-opacity N] [--padding N] [--scale S]
                      [-q QUALITY] [--no-audio] [--list-devices]
                      input

Options:
  -d, --device       Device model (default: iphone-16-pro)
  --color            Device color variant
  --bg               Background hex color (default: #0a0a0a)
  --no-shadow        Disable drop shadow
  --shadow-blur      Shadow blur radius (default: 50)
  --shadow-opacity   Shadow opacity 0-255 (default: 80)
  --padding          Padding around device in px (default: 100)
  --scale            Scale factor, e.g. 0.5 (default: native)
  -q, --quality      Video quality: high/medium/low (default: high)
  --no-audio         Strip audio from video output
```

## Examples

```bash
# iPhone 17 Pro in Cosmic Orange on dark background
python3 scripts/frame_video.py app.png -o mockup.png \
  -d iphone-17-pro --color cosmic-orange --bg '#1a1a2e' --scale 0.5

# iPhone 16 in Ultramarine, stealth dark
python3 scripts/frame_video.py screen.mp4 -o demo.mp4 \
  -d iphone-16 --color ultramarine --bg '#0a0a0a' --scale 0.5

# iPhone Air on a light background
python3 scripts/frame_video.py home.png -o showcase.png \
  -d iphone-air --color sky-blue --bg '#f0f4f8' --padding 120

# No shadow, no audio, fast encode
python3 scripts/frame_video.py tutorial.mp4 -o quick.mp4 \
  --no-shadow --no-audio -q low --scale 0.3
```

## How It Works

The frame PNGs have transparent screen areas with opaque bezels. The script:

1. Extracts a pixel-perfect screen mask from the frame's alpha channel using flood-fill (separating interior screen transparency from exterior device-outline transparency)
2. Scales the input content to fit the screen area
3. Applies the screen mask to the content (rounded corners)
4. Composites layers: **background → drop shadow → masked content → frame overlay**

Images are composited with Pillow (instant). Videos use ffmpeg's `filter_complex` for single-pass encoding with h264/aac.

## Dependencies

- **Python 3** with **Pillow** and **NumPy**
- **ffmpeg** (only needed for video inputs)

## Project Structure

```
device-framer/
├── README.md
├── SKILL.md              # Claude skill metadata
├── scripts/
│   └── frame_video.py    # Main script (handles both video and image)
└── frames/               # 44 device frame PNGs
    ├── 17 Pro - *.png
    ├── 17 Pro Max - *.png
    ├── 16 Pro - *.png
    ├── 16 Pro Max - *.png
    ├── 16 Plus - *.png
    ├── 16 - *.png
    ├── 15 Pro Max - *.png
    ├── 14 Pro Max - *.png
    ├── 13 mini - *.png
    ├── Air - *.png
    └── iPhone-XS-*.png
```

## Credits

- Modern device frames from [jamesjingyi/mockup-device-frames](https://github.com/jamesjingyi/mockup-device-frames), sourced from [Apple Developer Resources](https://developer.apple.com/design/resources/)
- Classic XS/XS Max frames from [t9mike/iphone_overlay](https://github.com/t9mike/iphone_overlay) (Apache 2.0)
- Original ffmpeg overlay approach inspired by t9mike/iphone_overlay

## License

Scripts are MIT. Device frame PNGs are from Apple Developer Resources — see Apple's terms for redistribution guidelines. Classic XS frames are Apache 2.0 from t9mike.
