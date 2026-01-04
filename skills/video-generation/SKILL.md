---
name: video-generation
description: >
  Use this skill for AI video generation. Triggers include:
  "generate video", "create video", "make video", "animate", "text to video", "video from image", "video of",
  "animate image", "bring to life", "make it move", "add motion", "video with audio", "video with dialogue"
  Supports text-to-video, image-to-video, video with dialogue/audio using Google Veo 3.1 (default) or OpenAI Sora.
---

# Video Generation Skill

Generate videos using AI (Google Veo 3.1, OpenAI Sora).

**Capabilities:**
- 🎬 **Text-to-Video**: Create videos from text descriptions
- 🖼️ **Image-to-Video**: Animate images as the first frame
- 🔊 **Audio Generation**: Dialogue, sound effects, ambient sounds (Veo 3+)
- 🎭 **Reference Images**: Guide video content with up to 3 reference images (Veo 3.1)

## Prerequisites

At least one API key is required:

- `GOOGLE_API_KEY` - For Google Veo (same key as image generation) ✅
- `OPENAI_API_KEY` - For OpenAI Sora

## Available Models

### Google Veo Models (Recommended - Default)

| Model | Description | Audio | Best For |
|-------|-------------|-------|----------|
| `veo-3.1` | Latest, highest quality | ✅ Yes | Professional, dialogue, reference images |
| `veo-3.1-fast` | Faster processing | ✅ Yes | Quick iterations |
| `veo-3` | Previous generation | ✅ Yes | Standard quality |
| `veo-3-fast` | Fast previous gen | ✅ Yes | Rapid prototyping |
| `veo-2` | Older, silent | ❌ No | Silent videos only |

**Veo 3.1 Features:**
- 720p/1080p resolution
- 4, 6, or 8 second duration
- Native audio (dialogue, SFX, ambient)
- Image-to-video (animate images)
- Reference images (up to 3)
- Video extension

### OpenAI Sora
- **Best for**: Creative videos, cinematic quality, complex motion
- **Resolutions**: 480p, 720p, 1080p
- **Durations**: 5s, 10s, 15s, 20s
- **Features**: Text-to-video, image-to-video

## Workflow

### Step 1: Ask Clarifying Questions

Before generating, ask the user in a single message:

---

**Example prompt to user:**

"I'll generate that video for you! Quick questions:

1. **Do you have an image to animate?** (I can use it as the first frame)

2. **Audio preference?**
   - With audio (default) - Veo 3.1 generates dialogue, SFX, ambient
   - Silent video - uses `--silent` flag (Veo 2)

3. **Which model would you like?**
   - `veo-3.1` - Latest, highest quality with audio (default)
   - `veo-3.1-fast` - Faster processing with audio
   - `veo-3` / `veo-3-fast` - Previous generation with audio
   - `sora` - OpenAI, up to 20 seconds, no audio

4. **Settings?**
   - Duration: 4s, 6s, or 8s (default: 8s)
   - Aspect ratio: 16:9 (landscape) or 9:16 (portrait)
   - Resolution: 720p or 1080p"

---

### Step 2: Craft the Prompt

Transform the user request into an effective video prompt:

1. **Describe the scene**: Set the visual context
2. **Specify action**: What moves, changes, happens
3. **Include camera work**: "slow pan", "tracking shot", "dolly shot"
4. **Add audio cues** (Veo 3+): Use quotes for dialogue, describe sounds
5. **Set the mood**: Lighting, atmosphere, time of day

**Example with dialogue (Veo 3.1):**
- User: "a person discovering treasure"
- Enhanced: "Close-up of a treasure hunter's face as torchlight flickers. He murmurs 'This must be it...' while brushing dust off an ancient chest. Sound of creaking hinges as he opens it, revealing golden light on his awestruck face. Cinematic, dramatic shadows."

**Example without dialogue:**
- User: "a dog running on a beach"
- Enhanced: "Cinematic slow-motion shot of a golden retriever running joyfully along a beach at sunset, waves lapping, warm golden hour lighting, shallow depth of field"

### Step 3: Select the Model

**Default: Google Veo 3.1** (latest, with audio)

| Use Case | Recommended Model | Reason |
|----------|------------------|--------|
| Default / Best quality | veo-3.1 | Latest, audio, reference images |
| Quick iteration | veo-3.1-fast | Faster with audio |
| Longer videos (>8s) | sora | Supports up to 20s |
| Silent videos | veo-2 | No audio processing |
| Cinematic/artistic | sora | Best creative control |

### Step 4: Generate the Video

Execute the appropriate script from `${CLAUDE_PLUGIN_ROOT}/skills/video-generation/scripts/`:

**For Google Veo 3.1 (default, with audio):**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/video-generation/scripts/veo.py \
  --prompt "your enhanced prompt with 'dialogue in quotes'" \
  --model "veo-3.1" \
  --duration 8 \
  --aspect-ratio "16:9" \
  --resolution "720p"
```

**For Google Veo 3.1 with image input:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/video-generation/scripts/veo.py \
  --prompt "The cat slowly opens its eyes and yawns" \
  --image "/path/to/cat.jpg" \
  --model "veo-3.1" \
  --duration 8
```

**For faster generation:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/video-generation/scripts/veo.py \
  --prompt "your prompt" \
  --model "veo-3.1-fast"
```

**For OpenAI Sora (longer videos):**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/video-generation/scripts/sora.py \
  --prompt "your enhanced prompt" \
  --duration 20 \
  --resolution "1080p"
```

**Silent video (no audio):**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/video-generation/scripts/veo.py \
  --prompt "your prompt" \
  --silent
```

**List available models:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/video-generation/scripts/veo.py --list-models
```

### Step 5: Deliver the Result

1. Provide the generated video file/URL
2. Share the enhanced prompt used
3. Mention generation settings (duration, resolution)
4. Offer to:
   - Generate variations
   - Try different style/duration
   - Use a different API
   - Extend the video

## Error Handling

**Missing API key**: Inform the user which key is needed:
- OpenAI: https://platform.openai.com/api-keys
- Google: https://aistudio.google.com/apikey

**Content policy violation**: Rephrase the prompt appropriately.

**Generation failed**: Retry with simplified prompt or different API.

**Quota exceeded**: Suggest waiting or trying the other provider.

## Prompt Engineering Tips

### For Audio (Veo 3.1)
- **Dialogue**: Use quotes for speech: `"Hello!" she said excitedly`
- **Sound effects**: Describe explicitly: `tires screeching, engine roaring`
- **Ambient**: Describe the soundscape: `birds chirping, distant traffic`
- **Example**: `A man whispers "Did you hear that?" as footsteps echo in the dark hallway`

### For Cinematic Quality
- Include camera directions: "slow dolly", "tracking shot", "crane shot"
- Specify lighting: "golden hour", "dramatic shadows", "soft diffused light"
- Add film references: "Blade Runner style", "Wes Anderson aesthetic"

### For Realistic Motion
- Describe physics: "natural movement", "realistic physics"
- Include environmental details: "wind in hair", "leaves rustling"
- Specify speed: "slow motion", "real-time", "time-lapse"

### For Image-to-Video
- Describe what should change/move from the starting image
- Be specific about the action: "the cat slowly opens its eyes"
- Include environmental motion: "leaves blow past"

### Negative Prompts
- Describe what NOT to include: `--negative-prompt "cartoon, low quality, blurry"`
- Don't use "no" or "don't" - just describe the unwanted elements

## API Comparison

| Feature | Veo 3.1 (Default) | Veo 3.1 Fast | Sora |
|---------|-------------------|--------------|------|
| Provider | Google | Google | OpenAI |
| API Key | `GOOGLE_API_KEY` | `GOOGLE_API_KEY` | `OPENAI_API_KEY` |
| Max duration | 8 seconds | 8 seconds | 20 seconds |
| Resolution | 720p, 1080p | 720p, 1080p | Up to 1080p |
| Aspect ratios | 16:9, 9:16 | 16:9, 9:16 | 16:9, 9:16, 1:1 |
| Audio (dialogue, SFX) | ✅ Yes | ✅ Yes | ❌ No |
| Image-to-video | ✅ Yes | ✅ Yes | ✅ Yes |
| Reference images | ✅ Up to 3 | ✅ Up to 3 | ❌ No |
| Video extension | ✅ Yes | ✅ Yes | ❌ No |
| Same key as images | ✅ Yes | ✅ Yes | ❌ No |
| Speed | Standard | Faster | Slower |
| Best for | Professional, dialogue | Quick iterations | Longer videos |
