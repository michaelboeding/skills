#!/usr/bin/env python3
"""
Device Framer — extended from github.com/t9mike/iphone_overlay (Apache 2.0)

Wraps screen recordings AND screenshots in iPhone device frames
with drop shadow and configurable background.

Supports:
  - Video input  → MP4 output  (via ffmpeg)
  - Image input  → PNG output  (via Pillow)
  - Auto-detect based on file extension
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageChops

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FRAMES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "frames")

VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".flv", ".wmv", ".gif"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif", ".heic"}

# ── Device Registry ──────────────────────────────────────────────────────────
# Frame PNGs from jamesjingyi/mockup-device-frames (Apple Developer Resources)
# Classic frames from t9mike/iphone_overlay (Apache 2.0)
DEVICES = {
    "iphone-17-pro-max": {
        "filename": "17 Pro Max - Silver.png", "frame_size": (1520, 3068),
        "screen_box": (100, 100, 1320, 2868), "screen_res": (1320, 2868), "cr": 95,
        "colors": {"cosmic-orange": "17 Pro Max - Cosmic Orange.png", "deep-blue": "17 Pro Max - Deep Blue.png", "silver": "17 Pro Max - Silver.png"},
        "label": "iPhone 17 Pro Max",
    },
    "iphone-17-pro": {
        "filename": "17 Pro - Silver.png", "frame_size": (1406, 2822),
        "screen_box": (100, 100, 1206, 2622), "screen_res": (1206, 2622), "cr": 95,
        "colors": {"cosmic-orange": "17 Pro - Cosmic Orange.png", "deep-blue": "17 Pro - Deep Blue.png", "silver": "17 Pro - Silver.png"},
        "label": "iPhone 17 Pro",
    },
    "iphone-16-pro-max": {
        "filename": "16 Pro Max - Black Titanium.png", "frame_size": (1520, 3068),
        "screen_box": (100, 100, 1320, 2868), "screen_res": (1320, 2868), "cr": 95,
        "colors": {"black-titanium": "16 Pro Max - Black Titanium.png", "natural-titanium": "16 Pro Max - Natural Titanium.png", "white-titanium": "16 Pro Max - White Titanium.png", "desert-titanium": "16 Pro Max - Desert Titanium.png"},
        "label": "iPhone 16 Pro Max",
    },
    "iphone-16-pro": {
        "filename": "16 Pro - Black Titanium.png", "frame_size": (1406, 2822),
        "screen_box": (102, 100, 1206, 2622), "screen_res": (1206, 2622), "cr": 95,
        "colors": {"black-titanium": "16 Pro - Black Titanium.png", "natural-titanium": "16 Pro - Natural Titanium.png", "white-titanium": "16 Pro - White Titanium.png", "desert-titanium": "16 Pro - Desert Titanium.png"},
        "label": "iPhone 16 Pro",
    },
    "iphone-16-plus": {
        "filename": "16 Plus - Black.png", "frame_size": (1490, 2996),
        "screen_box": (100, 100, 1290, 2796), "screen_res": (1290, 2796), "cr": 95,
        "colors": {"black": "16 Plus - Black.png", "pink": "16 Plus - Pink.png", "teal": "16 Plus - Teal.png", "ultramarine": "16 Plus - Ultramarine.png", "white": "16 Plus - White.png"},
        "label": "iPhone 16 Plus",
    },
    "iphone-16": {
        "filename": "16 - Black.png", "frame_size": (1379, 2756),
        "screen_box": (100, 100, 1179, 2556), "screen_res": (1179, 2556), "cr": 95,
        "colors": {"black": "16 - Black.png", "pink": "16 - Pink.png", "teal": "16 - Teal.png", "ultramarine": "16 - Ultramarine.png", "white": "16 - White.png"},
        "label": "iPhone 16",
    },
    "iphone-15-pro-max": {
        "filename": "15 Pro Max - Black Titanium.png", "frame_size": (1490, 2996),
        "screen_box": (99, 100, 1290, 2796), "screen_res": (1290, 2796), "cr": 95,
        "colors": {"black-titanium": "15 Pro Max - Black Titanium.png", "natural-titanium": "15 Pro Max - Natural Titanium.png", "white-titanium": "15 Pro Max - White Titanium.png", "blue-titanium": "15 Pro Max - Blue Titanium.png"},
        "label": "iPhone 15 Pro Max",
    },
    "iphone-14-pro-max": {
        "filename": "14 Pro Max - Space Black.png", "frame_size": (1490, 2996),
        "screen_box": (101, 98, 1290, 2796), "screen_res": (1290, 2796), "cr": 95,
        "colors": {"deep-purple": "14 Pro Max - Deep Purple.png", "gold": "14 Pro Max - Gold.png", "silver": "14 Pro Max - Silver.png", "space-black": "14 Pro Max - Space Black.png"},
        "label": "iPhone 14 Pro Max",
    },
    "iphone-13-mini": {
        "filename": "13 mini - Black.png", "frame_size": (1280, 2540),
        "screen_box": (100, 210, 1080, 2230), "screen_res": (1080, 2230), "cr": 95,
        "colors": {"black": "13 mini - Black.png", "blue": "13 mini - Blue.png", "pink": "13 mini - Pink.png", "red": "13 mini - Product (RED).png", "starlight": "13 mini - Starlight.png"},
        "label": "iPhone 13 mini",
    },
    "iphone-air": {
        "filename": "Air - Space Black.png", "frame_size": (1490, 2996),
        "screen_box": (100, 100, 1290, 2796), "screen_res": (1290, 2796), "cr": 95,
        "colors": {"cloud-white": "Air - Cloud White.png", "light-gold": "Air - Light Gold.png", "sky-blue": "Air - Sky Blue.png", "space-black": "Air - Space Black.png"},
        "label": "iPhone Air",
    },
    "iphone-xs-max": {
        "filename": "iPhone-XS-Max-Portrait-Space-Gray.png", "frame_size": (1032, 2050),
        "screen_box": (72, 129, 886, 1856), "screen_res": (1242, 2688), "cr": 0,
        "colors": {"space-gray": "iPhone-XS-Max-Portrait-Space-Gray.png"},
        "label": "iPhone XS Max",
    },
    "iphone-xs": {
        "filename": "iPhone-XS-Portrait-Space-Gray.png", "frame_size": (1044, 2062),
        "screen_box": (79, 142, 885, 1848), "screen_res": (1125, 2436), "cr": 0,
        "colors": {"space-gray": "iPhone-XS-Portrait-Space-Gray.png", "silver": "iPhone-XS-Portrait-Silver.png"},
        "label": "iPhone XS",
    },
}

DEFAULT_DEVICE = "iphone-16-pro"


# ── Shared helpers ───────────────────────────────────────────────────────────

def _rrect(draw, bbox, r, **kw):
    """Draw a rounded rectangle."""
    x0, y0, x1, y1 = bbox
    r = min(r, (x1 - x0) // 2, (y1 - y0) // 2)
    if r <= 0:
        draw.rectangle(bbox, **kw)
        return
    draw.rectangle([x0 + r, y0, x1 - r, y1], **kw)
    draw.rectangle([x0, y0 + r, x1, y1 - r], **kw)
    for c in [([x0, y0, x0+2*r, y0+2*r], 180, 270),
              ([x1-2*r, y0, x1, y0+2*r], 270, 360),
              ([x0, y1-2*r, x0+2*r, y1], 90, 180),
              ([x1-2*r, y1-2*r, x1, y1], 0, 90)]:
        draw.pieslice(c[0], c[1], c[2], **kw)


def hex_to_rgba(hex_color):
    """Convert hex color string to RGBA tuple."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r, g, b, 255)


def resolve_frame(device_name, color=None):
    """Resolve the frame PNG path and device info."""
    dev = DEVICES[device_name]
    colors = dev.get("colors", {})
    if color and color in colors:
        filename = colors[color]
    else:
        filename = dev["filename"]
    frame_path = os.path.join(FRAMES_DIR, filename)
    if not os.path.exists(frame_path):
        raise FileNotFoundError(f"Frame not found: {frame_path}")
    return frame_path, dev


def is_video(path):
    return os.path.splitext(path)[1].lower() in VIDEO_EXTS


def is_image(path):
    return os.path.splitext(path)[1].lower() in IMAGE_EXTS


def scale_device(dev, frame_path, scale):
    """Scale a device frame and return updated paths/dims. Returns (new_frame_path, dev_copy, is_temp)."""
    if scale is None or scale == 1.0:
        return frame_path, dev, False
    img = Image.open(frame_path)
    fw, fh = dev["frame_size"]
    nw, nh = int(fw * scale), int(fh * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(tmp.name, "PNG")
    sx, sy, sw, sh = dev["screen_box"]
    new_dev = dict(dev)
    new_dev["frame_size"] = (nw, nh)
    new_dev["screen_box"] = (int(sx*scale), int(sy*scale), int(sw*scale), int(sh*scale))
    new_dev["cr"] = int(dev["cr"] * scale)
    return tmp.name, new_dev, True


def make_shadow(frame_w, frame_h, cr, blur=50, opacity=80, offset_y=8):
    """Generate a soft gaussian drop shadow as a PIL Image."""
    pad = int(blur * 3)
    tw, th = frame_w + pad * 2, frame_h + pad * 2
    s = 2
    shadow = Image.new("RGBA", (tw * s, th * s), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    x0, y0 = pad * s, (pad + offset_y) * s
    x1, y1 = (pad + frame_w) * s - 1, (pad + frame_h + offset_y) * s - 1
    _rrect(sd, [x0, y0, x1, y1], cr * s, fill=(0, 0, 0, opacity))
    shadow = shadow.resize((tw, th), Image.LANCZOS)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur))
    return shadow, pad


def extract_screen_mask(frame_path, screen_box, target_w, target_h, corner_radius=95):
    """Create a screen mask with rounded corners matching the device frame.

    Uses the device's known corner radius to draw a precise rounded rectangle.
    This is more reliable than alpha-channel flood-fill, which can leak through
    anti-aliased pixels at the corners.
    """
    sx, sy, sw, sh = screen_box

    # Draw a rounded rectangle mask at the screen dimensions
    mask = Image.new("L", (sw, sh), 0)
    draw = ImageDraw.Draw(mask)
    # Inset by 2px so the frame fully covers edges
    inset = 2
    _rrect(draw, [inset, inset, sw - 1 - inset, sh - 1 - inset], corner_radius, fill=255)

    if mask.size != (target_w, target_h):
        mask = mask.resize((target_w, target_h), Image.LANCZOS)

    return mask


def fit_image(img, target_w, target_h):
    """Scale image to fit within target size, preserving aspect ratio, centered on black."""
    img.thumbnail((target_w, target_h), Image.LANCZOS)
    result = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 255))
    ox = (target_w - img.width) // 2
    oy = (target_h - img.height) // 2
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    result.paste(img, (ox, oy), img)
    return result


# ── Image framing (Pillow) ──────────────────────────────────────────────────

def frame_image(
    input_path, output_path,
    device=DEFAULT_DEVICE, color=None,
    bg_color="#0a0a0a",
    shadow=True, shadow_blur=50, shadow_opacity=80,
    padding=100, scale=None,
):
    """Frame a screenshot/image in a device mockup. Pure Pillow, no ffmpeg."""

    screenshot = Image.open(input_path).convert("RGBA")
    print(f"Input image: {screenshot.width}x{screenshot.height}")

    frame_path, dev = resolve_frame(device, color)
    frame_path, dev, is_temp = scale_device(dev, frame_path, scale)

    fw, fh = dev["frame_size"]
    sx, sy, sw, sh = dev["screen_box"]
    cr = dev["cr"]

    print(f"Frame: {fw}x{fh}, screen: {sw}x{sh} at ({sx},{sy})")

    # Canvas
    cw = fw + padding * 2
    ch = fh + padding * 2
    canvas = Image.new("RGBA", (cw, ch), hex_to_rgba(bg_color))

    fx, fy = padding, padding
    scx, scy = fx + sx, fy + sy

    # Drop shadow
    if shadow:
        shadow_img, shadow_pad = make_shadow(
            fw, fh, cr if cr > 0 else 60,
            shadow_blur, shadow_opacity, int(8 * (scale or 1))
        )
        shx = fx - shadow_pad
        shy = fy - shadow_pad
        canvas.paste(shadow_img, (shx, shy), shadow_img)

    # Scale screenshot to fit screen area
    screen_img = fit_image(screenshot, sw, sh)

    # Apply screen mask with rounded corners matching the device
    mask = extract_screen_mask(frame_path, (sx, sy, sw, sh), sw, sh, cr)
    screen_img.putalpha(ImageChops.multiply(screen_img.split()[3], mask))

    # Paste screenshot onto canvas
    canvas.paste(screen_img, (scx, scy), screen_img)

    # Overlay device frame
    frame_img = Image.open(frame_path).convert("RGBA")
    canvas.paste(frame_img, (fx, fy), frame_img)

    # Save
    canvas.save(output_path, "PNG")

    if is_temp:
        os.unlink(frame_path)

    print(f"Done → {output_path}")
    return output_path


# ── Video framing (ffmpeg) ──────────────────────────────────────────────────

def get_video_info(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_streams", "-show_format", path],
        capture_output=True, text=True,
    )
    d = json.loads(r.stdout)
    vs = next((s for s in d.get("streams", []) if s["codec_type"] == "video"), None)
    if not vs:
        raise ValueError("No video stream found in input")
    w, h = int(vs["width"]), int(vs["height"])
    rot = int(vs.get("tags", {}).get("rotate", 0))
    if rot in (90, 270):
        w, h = h, w
    return {
        "width": w, "height": h,
        "duration": float(d.get("format", {}).get("duration", 0)),
        "fps": eval(vs.get("r_frame_rate", "30/1")),
        "has_audio": any(s["codec_type"] == "audio" for s in d.get("streams", [])),
    }


def frame_video(
    input_path, output_path,
    device=DEFAULT_DEVICE, color=None,
    bg_color="#0a0a0a",
    shadow=True, shadow_blur=50, shadow_opacity=80,
    padding=100, scale=None,
    quality="high", keep_audio=True,
):
    """Frame a screen recording in a device mockup. Uses ffmpeg for video compositing."""

    vi = get_video_info(input_path)
    fps = min(vi["fps"], 60)
    print(f"Input video: {vi['width']}x{vi['height']}, {vi['fps']:.1f}fps, {vi['duration']:.1f}s")

    frame_path, dev = resolve_frame(device, color)
    frame_path, dev, is_temp = scale_device(dev, frame_path, scale)

    fw, fh = dev["frame_size"]
    sx, sy, sw, sh = dev["screen_box"]
    cr = dev["cr"]

    print(f"Frame: {fw}x{fh}, screen: {sw}x{sh} at ({sx},{sy})")

    tmp = tempfile.mkdtemp(prefix="devframe_")

    # Canvas
    cw = fw + padding * 2
    ch = fh + padding * 2
    cw += cw % 2; ch += ch % 2

    fx, fy = padding, padding
    scx, scy = fx + sx, fy + sy

    # Build ffmpeg inputs
    inputs = ["-i", input_path, "-i", frame_path]
    idx = {"video": 0, "frame": 1}
    next_i = 2

    if shadow:
        shadow_img, shadow_pad = make_shadow(
            fw, fh, cr if cr > 0 else 60,
            shadow_blur, shadow_opacity, int(8 * (scale or 1))
        )
        sp = os.path.join(tmp, "shadow.png")
        shadow_img.save(sp, "PNG")
        inputs += ["-i", sp]
        idx["shadow"] = next_i; next_i += 1

    # Screen mask with rounded corners matching the device
    mask = extract_screen_mask(frame_path, (sx, sy, sw, sh), sw, sh, cr)
    mp = os.path.join(tmp, "mask.png")
    mask.save(mp, "PNG")
    inputs += ["-i", mp]
    idx["mask"] = next_i; next_i += 1

    # Build filter_complex
    fc = []
    fc.append(f"color=c={bg_color}:s={cw}x{ch}:r={fps},format=rgba[bg]")
    fc.append(
        f"[0:v]scale={sw}:{sh}:force_original_aspect_ratio=decrease,"
        f"pad={sw}:{sh}:(ow-iw)/2:(oh-ih)/2:color=black,format=rgba[vid]"
    )

    fc.append(f"[{idx['mask']}:v]format=gray,format=rgba,alphaextract[mask]")
    fc.append("[vid][mask]alphamerge[vr]")
    vl = "vr"

    if shadow:
        shx = fx - shadow_pad
        shy = fy - shadow_pad
        fc.append(f"[bg][{idx['shadow']}:v]overlay={shx}:{shy}:format=auto[bgs]")
        base = "bgs"
    else:
        base = "bg"

    fc.append(f"[{base}][{vl}]overlay={scx}:{scy}:format=auto[bgv]")
    fc.append(f"[bgv][{idx['frame']}:v]overlay={fx}:{fy}:format=auto[out]")

    crf = {"high": "18", "medium": "23", "low": "28"}[quality]
    preset = {"high": "slow", "medium": "medium", "low": "fast"}[quality]

    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", ";".join(fc),
        "-map", "[out]",
    ]
    if keep_audio and vi["has_audio"]:
        cmd += ["-map", "0:a?", "-c:a", "aac", "-b:a", "192k"]
    else:
        cmd += ["-an"]
    cmd += [
        "-c:v", "libx264", "-crf", crf, "-preset", preset,
        "-pix_fmt", "yuv420p", "-r", str(int(fps)),
        "-shortest", output_path,
    ]

    print(f"Encoding ({quality} quality)...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ffmpeg error:\n{result.stderr[-3000:]}")
        raise RuntimeError(f"ffmpeg failed ({result.returncode})")

    # Cleanup
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)
    if is_temp:
        os.unlink(frame_path)

    print(f"Done → {output_path}")
    return output_path


# ── Auto-dispatch ────────────────────────────────────────────────────────────

def frame_content(input_path, output_path=None, **kwargs):
    """Auto-detect input type and frame it accordingly."""
    ext = os.path.splitext(input_path)[1].lower()

    if ext in VIDEO_EXTS:
        if output_path is None:
            base, _ = os.path.splitext(input_path)
            output_path = f"{base}_framed.mp4"
        return frame_video(input_path, output_path, **kwargs)

    elif ext in IMAGE_EXTS:
        if output_path is None:
            base, _ = os.path.splitext(input_path)
            output_path = f"{base}_framed.png"
        # Remove video-only kwargs
        img_kwargs = {k: v for k, v in kwargs.items()
                      if k not in ("quality", "keep_audio")}
        return frame_image(input_path, output_path, **img_kwargs)

    else:
        raise ValueError(
            f"Unsupported file type: {ext}\n"
            f"  Video: {', '.join(sorted(VIDEO_EXTS))}\n"
            f"  Image: {', '.join(sorted(IMAGE_EXTS))}"
        )


def list_devices():
    print("Available devices:\n")
    for name, dev in DEVICES.items():
        colors = ", ".join(sorted(dev.get("colors", set())))
        fw, fh = dev["frame_size"]
        sw, sh = dev["screen_box"][2], dev["screen_box"][3]
        label = dev.get("label", name)
        print(f"  {name:20s}  {label:16s}  frame {fw}x{fh}  screen {sw}x{sh}")
        print(f"  {'':20s}  colors: {colors}")
        print()


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Wrap a screen recording or screenshot in a device frame",
        epilog="Extended from github.com/t9mike/iphone_overlay (Apache 2.0)\n"
               "Supports video (MP4, MOV, etc.) and image (PNG, JPG, etc.) inputs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("input", nargs="?", help="Input video or image file")
    p.add_argument("-o", "--output", default=None,
                   help="Output path (default: <input>_framed.mp4/.png)")
    p.add_argument("-d", "--device", default=DEFAULT_DEVICE,
                   choices=list(DEVICES.keys()), help="Device model")
    p.add_argument("--color", default=None, help="Device color variant")
    p.add_argument("--bg", default="#0a0a0a", help="Background color (hex)")
    p.add_argument("--no-shadow", action="store_true", help="Disable drop shadow")
    p.add_argument("--shadow-blur", type=int, default=50)
    p.add_argument("--shadow-opacity", type=int, default=80, help="0-255")
    p.add_argument("--padding", type=int, default=100, help="Padding around device (px)")
    p.add_argument("--scale", type=float, default=None,
                   help="Scale frame (e.g. 0.5 for half size)")
    p.add_argument("-q", "--quality", default="high",
                   choices=["high", "medium", "low"], help="Video quality preset")
    p.add_argument("--no-audio", action="store_true", help="Strip audio (video only)")
    p.add_argument("--list-devices", action="store_true")

    a = p.parse_args()

    if a.list_devices:
        list_devices()
        sys.exit(0)

    if not a.input:
        p.print_help()
        sys.exit(1)

    frame_content(
        a.input, a.output,
        device=a.device, color=a.color,
        bg_color=a.bg,
        shadow=not a.no_shadow,
        shadow_blur=a.shadow_blur,
        shadow_opacity=a.shadow_opacity,
        padding=a.padding,
        scale=a.scale,
        quality=a.quality,
        keep_audio=not a.no_audio,
    )
