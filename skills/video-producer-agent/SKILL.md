---
name: video-producer-agent
description: >
  Use this skill to create complete videos with voiceover and music.
  Triggers: "create video", "product video", "explainer video", "promo video", "demo video",
  "training video", "ad video", "commercial", "marketing video", "video with voiceover",
  "video with music", "brand video", "testimonial video"
  Orchestrates: script, voiceover, background music, video clips/images, and final assembly.
---

# Video Producer

Create complete videos with voiceover, music, and visuals.

**This is an orchestrator skill** that combines:
- Script/storyboard generation (Claude)
- Voiceover synthesis (Gemini TTS)
- Background music (Lyria)
- Video clip generation (Veo 3.1) or image animation
- Final assembly (FFmpeg via media-utils)

## What You Can Create

| Type | Example |
|------|---------|
| Product video | 30s hero video showcasing a product |
| Explainer video | How-to or feature explanation |
| Promo/ad video | Marketing advertisement |
| Demo video | Product demonstration |
| Training video | Internal training content |
| Testimonial | Customer quote style video |
| Brand video | Company/brand story |

## Prerequisites

- `GOOGLE_API_KEY` - For Veo (video), Gemini TTS (voice), Lyria (music), Gemini (images)
- FFmpeg installed: `brew install ffmpeg`

## Workflow

### Step 1: Understand the Request

When user asks for video content, gather:

| What to Ask | Why |
|-------------|-----|
| **Subject** | What is the video about? Product, concept, story? |
| **Duration** | How long? (30s, 1min, 2min) |
| **Style** | Premium, fun, corporate, casual? |
| **Visuals** | User has images? Or generate everything? |
| **Voiceover** | Tone, voice preference? |
| **Music** | Style, energy level? |
| **Format** | Aspect ratio? (16:9, 9:16 for social) |

**Example prompt to user:**

"I'll create that product video! Quick questions:

1. **Do you have product images?** (I can use them or generate visuals)
2. **How long?** (30s, 1min, etc.)
3. **Style?** (Premium/luxury, fun/playful, corporate/professional)
4. **Voiceover tone?** (Professional, friendly, energetic)
5. **Music vibe?** (Modern electronic, cinematic, upbeat pop)
6. **Aspect ratio?** (16:9 landscape, 9:16 vertical for social)"

---

### Step 2: Create the Storyboard

Break down the video into scenes:

```
VIDEO: Premium Wireless Earbuds - 30 seconds

SCENE 1 (0-5s): Hero Reveal
- Visual: Slow zoom on earbuds emerging from shadow, premium lighting
- Audio: Subtle bass hit, then ambient electronic builds
- Voiceover: None (music only)

SCENE 2 (5-12s): Feature Highlight - Sound
- Visual: Sound waves visualization, person enjoying music
- Audio: Music continues, ducks under voice
- Voiceover: "Crystal clear sound. Immersive bass."

SCENE 3 (12-20s): Feature Highlight - Comfort
- Visual: Close-up of earbud in ear, person moving/exercising
- Audio: Music builds energy
- Voiceover: "All-day comfort. Secure fit."

SCENE 4 (20-27s): Lifestyle
- Visual: Person in various settings using earbuds
- Audio: Music peaks
- Voiceover: "Your music. Everywhere."

SCENE 5 (27-30s): Logo/CTA
- Visual: Product + logo on clean background
- Audio: Music resolves, subtle end sting
- Voiceover: "Experience the difference."

---
ASSETS NEEDED:
- Background music: Modern electronic, premium, 35 seconds
- Voiceover: Professional, confident voice (Charon)
- Video clips: 5 scenes via Veo 3.1
```

---

### Step 3: Generate Assets

**Generate background music (Lyria):**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/music-generation/scripts/lyria.py \
  --prompt "modern electronic, premium, sleek, product showcase, subtle bass" \
  --duration 35 \
  --bpm 100 \
  --brightness 0.6
```

**Generate voiceover (Gemini TTS):**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/voice-generation/scripts/gemini_tts.py \
  --text "Crystal clear sound. Immersive bass. All-day comfort. Secure fit. Your music. Everywhere. Experience the difference." \
  --voice Charon \
  --style "Speak with confident, premium brand voice. Measured pace, slight pauses between phrases."
```

**Generate video clips (Veo 3.1):**

Scene 1:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/video-generation/scripts/veo.py \
  --prompt "Cinematic slow zoom on premium wireless earbuds emerging from shadow, dramatic lighting, product photography style, high-end commercial look" \
  --model veo-3.1 \
  --duration 6 \
  --aspect-ratio 16:9 \
  --silent
```

Scene 2:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/video-generation/scripts/veo.py \
  --prompt "Abstract sound wave visualization transitioning to person with eyes closed enjoying music through earbuds, blissful expression, cinematic" \
  --model veo-3.1 \
  --duration 8 \
  --silent
```

*(Continue for each scene...)*

**Or generate from user's product image:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/video-generation/scripts/veo.py \
  --prompt "Camera slowly orbits around the product, premium lighting" \
  --image "/path/to/product.jpg" \
  --model veo-3.1 \
  --duration 6
```

---

### Step 4: Assemble the Video

**Concatenate video clips:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/media-utils/scripts/video_concat.py \
  -i scene1.mp4 scene2.mp4 scene3.mp4 scene4.mp4 scene5.mp4 \
  --transition fade \
  --duration 0.5 \
  -o video_no_audio.mp4
```

**Mix voiceover with music:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/media-utils/scripts/audio_mix.py \
  --voice voiceover.wav \
  --music background_music.wav \
  --music-volume 0.3 \
  --fade-in 2 \
  --fade-out 2 \
  -o final_audio.mp3
```

**Merge audio with video:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/media-utils/scripts/video_audio_merge.py \
  --video video_no_audio.mp4 \
  --audio final_audio.mp3 \
  -o final_product_video.mp4
```

---

### Step 5: Deliver the Result

**Example delivery:**

"✅ Your product video is ready!

**File:** `earbuds_product_video.mp4` (30s, 1080p, 16:9)

**What I created:**
- 5 video scenes with fade transitions
- Professional voiceover (Charon voice)
- Modern electronic background music
- Music ducks under voiceover

**Preview the sections:**
- 0-5s: Hero reveal (music only)
- 5-20s: Feature highlights with voiceover
- 20-27s: Lifestyle montage
- 27-30s: Logo/CTA

**Want me to:**
- Change the voiceover tone?
- Try different music?
- Adjust scene timing?
- Create a vertical (9:16) version for social?"

---

## Input Files You Can Provide

| File Type | How It's Used |
|-----------|---------------|
| Product images | Animate with Veo as first frame |
| Logo (PNG) | Overlay on final scene |
| Existing voiceover | Skip TTS generation |
| Brand music | Use instead of Lyria |
| Video clips | Include in assembly |
| Script/copy | Use for voiceover text |

---

## Video Styles & Music Pairings

| Style | Music Prompt | Voice |
|-------|--------------|-------|
| Premium/Luxury | "elegant, minimal, ambient, sophisticated" | Charon (informative) |
| Tech/Modern | "electronic, futuristic, clean, innovative" | Kore (firm) |
| Fun/Playful | "upbeat, cheerful, acoustic, positive" | Puck (upbeat) |
| Corporate | "professional, inspiring, orchestral lite" | Orus (firm) |
| Lifestyle | "chill, aspirational, indie, warm" | Aoede (breezy) |
| Dramatic/Cinematic | "epic, orchestral, emotional, building" | Gacrux (mature) |

---

## Common Video Structures

### Product Video (30s)
```
0-5s:   Hero shot (music only)
5-15s:  Features (voiceover + music)
15-25s: Lifestyle/use case (voiceover + music)
25-30s: Logo + CTA (music fade)
```

### Explainer Video (60s)
```
0-5s:   Hook/problem statement
5-20s:  Solution introduction
20-45s: How it works (3 steps)
45-55s: Benefits summary
55-60s: CTA
```

### Testimonial Video (45s)
```
0-5s:   Intro/name card
5-35s:  Testimonial quote (multiple scenes)
35-45s: Product shot + logo
```

---

## Limitations

- **Veo video duration**: Max 8 seconds per clip (concatenate for longer)
- **Veo 3.1 always has audio**: Use `--silent` flag to get Veo 2 for silent clips, or strip audio in assembly
- **Processing time**: Video generation takes 1-3 minutes per clip
- **Resolution**: Currently 720p or 1080p (1080p for 8s only)

## Error Handling

| Error | Solution |
|-------|----------|
| "GOOGLE_API_KEY not set" | Set up API key per README |
| "FFmpeg not found" | Install: `brew install ffmpeg` |
| Video generation timeout | Retry, or use shorter duration |
| Audio/video sync issues | Use `--offset` in video_audio_merge |

## Example Prompts

**Simple:**
> "Create a 30-second product video for my new coffee maker"

**Detailed:**
> "Create a 45-second product video for our new wireless earbuds. Premium, luxury feel. I have product photos attached. Professional male voiceover. Modern electronic music. 16:9 for YouTube, also make a 9:16 cut for Instagram."

**With assets:**
> "Create a video using these product images. Add a voiceover reading this script: '...' Use upbeat music."
