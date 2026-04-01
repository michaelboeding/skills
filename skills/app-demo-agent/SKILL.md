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

**Q3b: Device Color** *(if device frame selected)*
> "What color for the [device name]?
>
> *(list the available colors for the selected device)*"

*Wait for response. Show the actual color options from the device registry.*

**Q3c: Background Color** *(if device frame selected)*
> "What background color for the video?
>
> - **Dark** (`#0a0a0a`) — cinematic, great for social media
> - **White** (`#ffffff`) — clean, good for presentations/websites
> - **Transparent** — for compositing *(note: output will be WebM, not MP4)*
> - **Custom** — specify a hex color"

*Wait for response. If transparent, set output format to WebM with alpha. If custom, validate the hex color.*

**Q4: Voiceover**
> "How should we handle the voiceover?
>
> - **Generate** — I'll analyze the recording and write a script that narrates what's on screen
> - **You provide** — Give me the script text
> - **None** — No voiceover"

*Wait for response.*

**Q5: Voice Style** *(if voiceover enabled)*
> "What kind of voice?
>
> **Tone:**
> - Professional / polished
> - Friendly / conversational
> - Energetic / excited
> - Calm / reassuring
> - Or describe your own tone
>
> **Gender preference:**
> - Male
> - Female
> - No preference"

*Wait for response.*

**Q6: Voice Selection** *(if voiceover enabled)*

Based on the user's tone and gender preference, recommend a specific voice and let them confirm or pick another:

> "Based on your preferences, I'd recommend **[voice name]** ([provider]). Here are some options:
>
> | Voice | Provider | Tone |
> |-------|----------|------|
> | Kore | Gemini | Friendly, clear, female |
> | Charon | Gemini | Professional, authoritative, male |
> | Puck | Gemini | Upbeat, energetic, male |
> | Aoede | Gemini | Breezy, warm, female |
> | nova | OpenAI | Friendly, natural, female |
> | onyx | OpenAI | Deep, professional, male |
>
> Want to go with **[recommendation]**, or pick a different one?"

*Wait for response.*

**Q7: Background Music**
> "Want background music? If so, what vibe?
>
> - **Modern / minimal** — clean, tech-forward
> - **Upbeat / positive** — energetic, fun
> - **Corporate / professional** — polished, confident
> - **Ambient / calm** — soft, relaxed
> - **Custom** — describe the vibe you want
> - **No music** — voiceover only (or silent)"

*Wait for response.*

**Q8: Output**
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
| Device Color | Color variant for the selected device |
| Background Color | Background behind the device frame |
| Voiceover | Generate script vs user-provided vs none |
| Voice Style | Tone and gender preference |
| Voice Selection | Specific TTS voice and provider |
| Background Music | Whether to generate music and what style |
| Output | Where to save final video |

---

### Step 2: Analyze the Screen Recording

Extract keyframes from the recording. **Use scene detection** to capture frames at actual screen transitions rather than fixed intervals — this gives you frames at the moments that matter.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/app-demo-agent/scripts/extract_frames.py \
  INPUT_VIDEO \
  -o ~/demo_project/frames/ \
  --scene-detect \
  --timestamps
```

If scene detection doesn't find enough transitions (e.g., scrolling content), fall back to fixed intervals:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/app-demo-agent/scripts/extract_frames.py \
  INPUT_VIDEO \
  -o ~/demo_project/frames/ \
  --interval 2 \
  --max-frames 20 \
  --timestamps
```

**Options:**
| Option | Default | Description |
|--------|---------|-------------|
| `--scene-detect` | off | Detect actual screen transitions instead of fixed intervals |
| `--scene-threshold` | `0.3` | Scene sensitivity 0.0-1.0, lower = more sensitive |
| `--interval` | `2` | Seconds between frame captures (fixed interval mode) |
| `--max-frames` | `20` | Maximum number of frames to extract |
| `-o, --output` | `./frames/` | Output directory for frames |
| `--timestamps` | off | Also output a `timestamps.json` mapping |

This creates numbered PNG screenshots: `frame_001.png`, `frame_002.png`, etc. The `timestamps.json` maps each frame to its exact timestamp in the video.

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

⚠️ **This is the most important step.** The voiceover must match what's happening on screen at every moment. A generic script that doesn't align with the visuals will feel disconnected and unprofessional.

**First, get the exact video duration:**
```bash
ffprobe -v quiet -show_entries format=duration -of csv=p=0 INPUT_VIDEO
```

**Then write a timed script** that maps narration to the frame timeline you built in Step 2. Every line of the script should correspond to what's visible on screen at that moment.

#### Script Rules

1. **Content must match the screen** — if the user is tapping a button at 4s, the narration at 4s should describe that action. Never narrate something that isn't visible.
2. **Fill the full video duration** — the voiceover should naturally span the entire recording. Not too short (dead silence at the end), not too long (audio gets cut off). Aim for the TTS output to be within 2-3 seconds of the video length.
3. **Flow with transitions** — when the screen transitions between views, use that moment for a brief pause or transitional phrase. Don't talk over a screen change.
4. **Be natural and conversational** — not robotic marketing speak.
5. **Highlight key features** — call out what makes the app special as those features appear on screen.

#### Write the script as a timed outline first

Map each line to the timestamp where it should be spoken:

```
[0-3s]   "Meet TaskFlow — the simplest way to stay on top of your day."
[3-6s]   "Tap the plus button to create a new task."
[6-10s]  "Give it a name... set a due date... and you're done."
[10-14s] "Your tasks show up right on your home screen, organized by priority."
[14-17s] "One tap to mark it complete."
[17-20s] "That's it — no clutter, no complexity. TaskFlow."
```

#### Then convert to a single block for TTS

Remove the timestamps and join into flowing text. Use punctuation to control pacing:

```
Meet TaskFlow — the simplest way to stay on top of your day.
Tap the plus button to create a new task.
Give it a name... set a due date... and you're done.
Your tasks show up right on your home screen, organized by priority.
One tap to mark it complete.
That's it — no clutter, no complexity. TaskFlow.
```

#### Pacing guide

| Video Duration | Target Word Count | Pace |
|----------------|-------------------|------|
| 15s | 30-40 words | Fast, punchy |
| 30s | 60-80 words | Standard |
| 45s | 90-120 words | Comfortable |
| 60s | 120-150 words | Relaxed |
| 90s+ | ~150 words/min | Natural conversational |

**Tips:**
- Short sentences work better for TTS pacing
- Periods create natural pauses (~0.5s)
- Ellipsis (...) creates longer pauses (~1s)
- Em dashes (—) create brief pauses (~0.3s)
- Front-load the hook — first sentence matters most
- End with the app name or a clear CTA

**Present the timed script to the user for approval before generating audio.** Show both the timed outline and the final text block. Ask if they want changes to wording, pacing, or emphasis.

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
  --voice Orus \
  --style "Clear, confident, app demo narration" \
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

⚠️ **You can also use `--text-file` instead of `--text`** to read the script from a file:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/voice-generation/scripts/gemini_tts.py \
  --text-file ~/demo_project/script.md \
  --voice Kore \
  --style "Friendly, clear, app demo narration" \
  -o ~/demo_project/voiceover.wav
```

#### Duration Check (CRITICAL)

After generating the voiceover, **immediately check if it matches the video duration**:

```bash
# Get voiceover duration
VO_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 ~/demo_project/voiceover.wav)

# Get video duration
VID_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 INPUT_VIDEO)

echo "Voiceover: ${VO_DUR}s, Video: ${VID_DUR}s"
```

**If there's a mismatch greater than 3 seconds, fix it before proceeding:**

| Situation | Fix |
|-----------|-----|
| **Voiceover too long** | Shorten the script — remove filler words, tighten phrasing, cut a line. Regenerate. |
| **Voiceover slightly long** (< 5s over) | Extend the video with a freeze frame at the end: `ffmpeg -i video.mp4 -vf "tpad=stop_mode=clone:stop_duration=5" -c:a copy extended.mp4` |
| **Voiceover too short** | Add more descriptive lines, slow the pace with pauses (ellipsis), or add a closing line. Regenerate. |
| **Voiceover slightly short** (< 3s under) | Acceptable — the video will have a brief silent outro which can feel natural. |

**Always prefer adjusting the script** over stretching the video. The script should be written to fit the video, not the other way around.

#### Voice Recommendations for Demos

| Tone | Gemini Voice | OpenAI Voice | ElevenLabs Voice |
|------|-------------|--------------|-----------------|
| **Default / Professional** | **Orus** (recommended) | onyx | josh |
| Friendly | Kore | nova | rachel |
| Energetic | Puck | echo | domi |
| Calm | Aoede | shimmer | bella |
| Authoritative | Charon | alloy | adam |

**Default voice: Orus (Gemini TTS)** — firm, clear, professional. Works well for most app demos.

---

### Step 6: Generate Background Music (Optional)

If the user wants music:

⚠️ **Always match the video duration exactly.** Get the video duration first, then pass it to the music generator:

```bash
# Get exact video duration
DURATION=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 INPUT_VIDEO | cut -d. -f1)

python3 ${CLAUDE_PLUGIN_ROOT}/skills/music-generation/scripts/lyria.py \
  --prompt "modern, minimal, tech product demo, clean, upbeat, positive" \
  --duration $DURATION \
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
  --text-file $PROJECT/script.md --voice Orus \
  --style "Clear, confident, app demo narration" -o $PROJECT/voiceover.wav

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
| **General / default** | **Orus (firm)** | "modern, clean, minimal, professional" |
| SaaS product tour | Orus (firm) | "modern, clean, minimal, professional" |
| Mobile app showcase | Puck (upbeat) | "upbeat, positive, mobile, fresh" |
| Enterprise demo | Charon (authoritative) | "corporate, confident, ambient, subtle" |
| Creative tool | Aoede (breezy) | "inspiring, creative, flowing, warm" |
| Developer tool | Orus (firm) | "tech, minimal, electronic, focused" |
| Consumer app | Kore (friendly) | "playful, modern, light, accessible" |

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
