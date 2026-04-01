---
name: app-demo-agent
description: >
  Use this skill to turn screen recordings into polished app demo videos with AI voiceover and music.
  Triggers: "app demo", "demo video from recording", "screen recording demo", "narrate this recording",
  "add voiceover to screen recording", "make a demo from this recording", "polish this screen recording",
  "app walkthrough video", "product demo video", "turn this recording into a demo",
  "screen recording with voiceover", "app showcase video", "demo with narration"
  Orchestrates: screen analysis, voiceover script, device framing, TTS, background music, and final assembly.
  NOTE: This skill requires an existing screen recording as input. It does NOT generate screen recordings.
---

# App Demo Producer

Turn raw screen recordings into polished app demo videos with AI-generated voiceover, device frames, and background music.

**This is an orchestrator skill** that combines:
- Screen recording analysis (FFmpeg frame extraction + Claude vision)
- Voiceover script generation (Claude)
- Device framing (device-framer)
- Voice synthesis (Gemini TTS / OpenAI TTS / ElevenLabs)
- Background music (Lyria / Suno / Udio)
- Final assembly (FFmpeg via media-utils)

## Workflow

### Step 1: Gather Requirements (REQUIRED)

⚠️ **DO NOT skip this step. DO NOT start processing until you have ALL answers.**

**Use interactive questioning** — ask ONE question at a time, wait for the response, then ask the next.

#### Question Flow

⚠️ **Use the `AskUserQuestion` tool for each question below.**

**Q1: Screen Recording**
> "I'll turn that into a polished demo! First — **where's the screen recording?**
>
> *(provide the file path, e.g., ~/Desktop/recording.mp4)*"

*Wait for response. Verify the file exists.*

**Q2: What does the app do?**
> "Give me a quick overview of what this app does and what the recording shows.
>
> *(e.g., 'It's a task management app. The recording shows creating a task, setting a due date, and marking it complete.')*"

*Wait for response. This context dramatically improves the voiceover script.*

**Q3: Device Frame**
> "Should I wrap it in a device frame?
>
> - **Yes** — iPhone 16 Pro (default)
> - **Yes, specific device** — *(I'll show you options)*
> - **No** — Keep as-is"

*Wait for response. If they want a specific device, run `--list-devices` and let them pick.*

**Q4: Voiceover**
> "How should we handle the voiceover?
>
> - **Generate** — I'll analyze the recording and write a script
> - **You provide** — Give me the script text
> - **None** — No voiceover"

*Wait for response.*

**Q5: Voice Style** *(if voiceover enabled)*
> "What voice tone?
>
> - Professional / polished
> - Friendly / conversational
> - Energetic / excited
> - Calm / reassuring
> - Or describe your own tone"

*Wait for response.*

**Q6: Background Music**
> "Want background music?
>
> - **Yes** — *(describe the vibe, or I'll pick something fitting)*
> - **No** — Voiceover only (or silent)"

*Wait for response.*

**Q7: Output**
> "Where should I save the final video?
>
> *(default: same directory as the input, with `_demo` suffix)*"

*Wait for response.*

#### Quick Reference

| Question | Determines |
|----------|------------|
| Screen Recording | Input file |
| App Overview | Context for voiceover script |
| Device Frame | Whether to use device-framer and which device |
| Voiceover | Generate script vs user-provided vs none |
| Voice Style | TTS voice selection and style |
| Background Music | Whether to generate music and what style |
| Output | Where to save final video |

---

### Step 2: Analyze the Screen Recording

Extract keyframes from the recording so you can understand what's happening on screen.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/app-demo-agent/scripts/extract_frames.py \
  INPUT_VIDEO \
  -o ~/demo_project/frames/ \
  --interval 2 \
  --max-frames 20
```

**Options:**
| Option | Default | Description |
|--------|---------|-------------|
| `--interval` | `2` | Seconds between frame captures |
| `--max-frames` | `20` | Maximum number of frames to extract |
| `-o, --output` | `./frames/` | Output directory for frames |
| `--timestamps` | off | Also output a `timestamps.json` mapping |

This creates numbered PNG screenshots: `frame_001.png`, `frame_002.png`, etc.

**Now read each frame image** using the Read tool to understand the screen flow. Build a mental timeline:

```
0s  - App opens, home screen visible
2s  - User taps "New Task" button
4s  - Task creation form appears
6s  - User types task name
8s  - User sets due date
10s - User taps "Save"
12s - Task appears in list with checkmark
```

Use the user's app description (Q2) combined with what you see in the frames to understand the full flow.

---

### Step 3: Write the Voiceover Script

Based on your analysis, write a voiceover script that narrates the screen flow. The script should:

1. **Match the recording duration** — get the video duration first:
   ```bash
   ffprobe -v quiet -show_entries format=duration -of csv=p=0 INPUT_VIDEO
   ```

2. **Be natural and conversational** — not robotic marketing speak
3. **Describe what the user sees** — guide viewers through the flow
4. **Highlight key features** — call out what makes the app special
5. **Match the pacing** — leave pauses where the screen is transitioning

**Script format — write as a single block of text** (TTS handles pacing from punctuation):

```
Meet TaskFlow — the simplest way to stay on top of your day.
Tap the plus button to create a new task.
Give it a name, set a due date, and you're done.
Your tasks show up right on your home screen, organized by priority.
One tap to mark it complete. That's it — no clutter, no complexity.
TaskFlow. Get more done with less.
```

**Tips:**
- Use short sentences (TTS pacing works better)
- Add periods for natural pauses
- Use ellipsis (...) for longer pauses
- Keep it under 150 words for a 30-60s video
- Front-load the hook — first sentence matters most

**Present the script to the user for approval before generating audio.** Ask if they want changes.

---

### Step 4: Frame the Video (Optional)

If the user wants a device frame, wrap the recording:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/device-framer/scripts/frame_video.py \
  INPUT_VIDEO \
  -o ~/demo_project/framed.mp4 \
  -d iphone-16-pro --color natural-titanium \
  --bg '#0a0a0a' --scale 0.5 --padding 100
```

**Recommended combos for demos:**
| Vibe | Device | Color | Background |
|------|--------|-------|------------|
| Premium dark | iphone-16-pro | natural-titanium | `#0a0a0a` |
| Modern vibrant | iphone-17-pro | cosmic-orange | `#1a1a2e` |
| Clean light | iphone-air | cloud-white | `#f0f4f8` |
| Bold | iphone-16 | ultramarine | `#0a0a0a` |
| Classic | iphone-16-pro-max | black-titanium | `#111111` |

⚠️ **Use `--scale 0.5`** for most demos — native resolution is very large.

The framed video becomes the input for the rest of the pipeline.

---

### Step 5: Generate Voiceover Audio

Use one of the voice generation scripts:

**Gemini TTS (recommended — free, high quality):**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/voice-generation/scripts/gemini_tts.py \
  --text "Your voiceover script here..." \
  --voice Kore \
  --style "Friendly, clear, app demo narration" \
  -o ~/demo_project/voiceover.wav
```

**OpenAI TTS:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/voice-generation/scripts/openai_tts.py \
  --text "Your voiceover script here..." \
  --voice nova \
  -o ~/demo_project/voiceover.mp3
```

**ElevenLabs:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/voice-generation/scripts/elevenlabs.py \
  --text "Your voiceover script here..." \
  --voice rachel \
  -o ~/demo_project/voiceover.mp3
```

#### Voice Recommendations for Demos

| Tone | Gemini Voice | OpenAI Voice | ElevenLabs Voice |
|------|-------------|--------------|-----------------|
| Professional | Charon | onyx | josh |
| Friendly | Kore | nova | rachel |
| Energetic | Puck | echo | domi |
| Calm | Aoede | shimmer | bella |
| Authoritative | Orus | alloy | adam |

---

### Step 6: Generate Background Music (Optional)

If the user wants music:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/music-generation/scripts/lyria.py \
  --prompt "modern, minimal, tech product demo, clean, upbeat, positive" \
  --duration MATCH_VIDEO_DURATION \
  -o ~/demo_project/music.wav
```

**Music prompts for demos:**
| App Type | Music Prompt |
|----------|-------------|
| Productivity | "minimal, modern, clean, focused, light electronic" |
| Social/Fun | "upbeat, playful, positive, acoustic, indie" |
| Finance/Business | "professional, confident, modern, ambient, corporate" |
| Health/Wellness | "calm, organic, warm, gentle, ambient" |
| Gaming | "energetic, electronic, dynamic, exciting, bass" |
| Creative tool | "inspiring, flowing, ambient, creative, modern" |

---

### Step 7: Mix Audio

If you have both voiceover and music, mix them:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/media-utils/scripts/audio_mix.py \
  --voice ~/demo_project/voiceover.wav \
  --music ~/demo_project/music.wav \
  -o ~/demo_project/final_audio.mp3 \
  --music-volume 0.2 \
  --fade-in 1.0 \
  --fade-out 2.0
```

**Recommended settings for demos:**
- `--music-volume 0.15` to `0.25` — music should be subtle under narration
- `--fade-in 1.0` — gentle music intro
- `--fade-out 2.0` — clean ending

If voiceover only (no music), skip this step and use the voiceover file directly.

---

### Step 8: Merge Audio with Video

Strip existing audio from the video (if any) and merge the new audio:

```bash
# Strip existing audio first
python3 ${CLAUDE_PLUGIN_ROOT}/skills/media-utils/scripts/video_strip_audio.py \
  -i ~/demo_project/framed.mp4 \
  -o ~/demo_project/silent_video.mp4

# Merge new audio
python3 ${CLAUDE_PLUGIN_ROOT}/skills/media-utils/scripts/video_audio_merge.py \
  --video ~/demo_project/silent_video.mp4 \
  --audio ~/demo_project/final_audio.mp3 \
  -o ~/demo_project/output/app_demo_final.mp4
```

If the video has no audio to strip, merge directly:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/media-utils/scripts/video_audio_merge.py \
  --video ~/demo_project/framed.mp4 \
  --audio ~/demo_project/final_audio.mp3 \
  -o ~/demo_project/output/app_demo_final.mp4
```

---

### Step 9: Deliver

Present the final video to the user:
1. Tell them where the output file is
2. Mention the duration and file size
3. Offer adjustments:
   - "Want me to change the voiceover script?"
   - "Different voice or music style?"
   - "Different device frame or background color?"
   - "Adjust the music volume?"

---

## Project Structure

```
demo_project/
├── frames/                   # Extracted keyframes for analysis
│   ├── frame_001.png
│   ├── frame_002.png
│   └── timestamps.json       # Frame timestamp mapping
├── framed.mp4                # Device-framed video (if applicable)
├── voiceover.wav             # Generated voiceover
├── music.wav                 # Generated background music
├── final_audio.mp3           # Mixed voiceover + music
├── silent_video.mp4          # Video with audio stripped
├── script.md                 # Voiceover script (for reference)
└── output/
    └── app_demo_final.mp4    # Final deliverable
```

---

## Full Pipeline (Quick Reference)

For quick reference, here's the full pipeline in order:

```bash
SKILL="${CLAUDE_PLUGIN_ROOT}/skills"
PROJECT=~/demo_project
INPUT=recording.mp4

# 1. Extract frames for analysis
python3 $SKILL/app-demo-agent/scripts/extract_frames.py $INPUT -o $PROJECT/frames/ --timestamps

# 2. [Claude analyzes frames + writes voiceover script]

# 3. Frame the video (optional)
python3 $SKILL/device-framer/scripts/frame_video.py $INPUT -o $PROJECT/framed.mp4 \
  -d iphone-16-pro --color natural-titanium --bg '#0a0a0a' --scale 0.5

# 4. Generate voiceover
python3 $SKILL/voice-generation/scripts/gemini_tts.py \
  --text-file $PROJECT/script.md --voice Kore \
  --style "Friendly app demo narration" -o $PROJECT/voiceover.wav

# 5. Generate music (optional)
python3 $SKILL/music-generation/scripts/lyria.py \
  --prompt "minimal, modern, tech demo" --duration 30 -o $PROJECT/music.wav

# 6. Mix audio
python3 $SKILL/media-utils/scripts/audio_mix.py \
  --voice $PROJECT/voiceover.wav --music $PROJECT/music.wav \
  -o $PROJECT/final_audio.mp3 --music-volume 0.2

# 7. Strip + merge
python3 $SKILL/media-utils/scripts/video_strip_audio.py -i $PROJECT/framed.mp4 -o $PROJECT/silent.mp4
python3 $SKILL/media-utils/scripts/video_audio_merge.py \
  --video $PROJECT/silent.mp4 --audio $PROJECT/final_audio.mp3 \
  -o $PROJECT/output/app_demo_final.mp4
```

---

## What You Can Create

| Input | Output |
|-------|--------|
| Raw screen recording | Polished demo with voiceover |
| App walkthrough capture | Narrated product tour |
| Feature demo recording | Marketing-ready feature highlight |
| Tutorial screen capture | Professional tutorial with narration |
| Bug reproduction video | Annotated bug report video |
| Prototype recording | Investor demo with voiceover |

---

## Prerequisites

- **FFmpeg** — `brew install ffmpeg` (required for all media processing)
- **Pillow** — `pip install Pillow` (required if using device framing)
- **Voice generation** — at least one of:
  - `GOOGLE_API_KEY` or `GOOGLE_CLOUD_PROJECT` (Gemini TTS — recommended)
  - `OPENAI_API_KEY` (OpenAI TTS)
  - `ELEVENLABS_API_KEY` (ElevenLabs)
- **Music generation** (optional) — `GOOGLE_API_KEY` or `GOOGLE_CLOUD_PROJECT` for Lyria

---

## Voice & Music Pairing Guide

| Demo Style | Voice (Gemini) | Music Prompt |
|------------|----------------|-------------|
| SaaS product tour | Kore (friendly) | "modern, clean, minimal, professional" |
| Mobile app showcase | Puck (upbeat) | "upbeat, positive, mobile, fresh" |
| Enterprise demo | Charon (professional) | "corporate, confident, ambient, subtle" |
| Creative tool | Aoede (breezy) | "inspiring, creative, flowing, warm" |
| Developer tool | Orus (firm) | "tech, minimal, electronic, focused" |
| Consumer app | Zephyr (bright) | "playful, modern, light, accessible" |

---

## Limitations

- **Requires existing screen recording** — this skill does not capture screens
- **Frame analysis depends on image clarity** — blurry recordings produce weaker scripts
- **Video duration limits TTS** — very long recordings (5+ min) may need the script split into segments
- **Device framer adds processing time** — especially for long videos
- **Music generation** — Lyria clips max at ~30s, may need to loop for longer videos

---

## Error Handling

| Error | Solution |
|-------|----------|
| "FFmpeg not found" | Install: `brew install ffmpeg` |
| "No frames extracted" | Check input video is valid, try lower `--interval` |
| "GOOGLE_API_KEY not set" | Set up API key per main README |
| "Pillow not installed" | Run: `pip install Pillow` |
| Audio/video duration mismatch | Voiceover script may be too long/short — adjust and regenerate |
| Device framer fails | Check frame PNG files exist in device-framer/frames/ |

---

## Example Prompts

**Simple:**
> "Here's a screen recording of my app — turn it into a polished demo video"

**With details:**
> "I have a screen recording at ~/Desktop/myapp.mov. It's a fitness app showing the workout tracking feature. Put it in an iPhone 16 Pro frame, add a friendly voiceover, and some upbeat background music."

**Minimal:**
> "Add voiceover narration to this screen recording: ~/recordings/demo.mp4"

**Full control:**
> "Take ~/Desktop/recording.mp4, frame it in iPhone 17 Pro cosmic orange on dark background, generate a professional voiceover script, use Gemini TTS with Charon voice, add minimal electronic background music, save to ~/Desktop/final_demo.mp4"
