---
name: video-generation
description: This skill should be used when the user asks to "generate a video", "create a video", "make a video", "animate", "text to video", "video from image", "video of", or needs AI video generation using OpenAI Sora or Google Veo. Handles prompt crafting, API selection, and video delivery.
---

# Video Generation Skill

Generate videos using AI video generation APIs (OpenAI Sora, Google Veo 3).

## Prerequisites

Environment variables must be configured. At least one API key is required:

- `OPENAI_API_KEY` - For OpenAI Sora video generation
- `GOOGLE_API_KEY` - For Google Veo 3 video generation

See the repository README for setup instructions.

## Available APIs

### Google Veo 3 (Recommended - Default)
- **Best for**: Realistic videos, natural motion, high fidelity
- **Resolutions**: Up to 1080p
- **Durations**: Up to 8 seconds per generation
- **Aspect ratios**: 16:9, 9:16, 1:1
- **Features**: Text-to-video, high fidelity, natural physics, same API key as image generation

### OpenAI Sora
- **Best for**: Creative videos, cinematic quality, complex motion
- **Resolutions**: 480p, 720p, 1080p
- **Durations**: 5s, 10s, 15s, 20s
- **Aspect ratios**: 16:9, 9:16, 1:1
- **Features**: Text-to-video, image-to-video, video extensions

## Workflow

### Step 1: Understand the Request

Parse the user's video request for:
- **Subject/action**: What should happen in the video?
- **Style**: Cinematic, documentary, animation, abstract?
- **Duration**: How long should it be?
- **Aspect ratio**: Landscape (16:9), portrait (9:16), square (1:1)?
- **Camera motion**: Static, pan, zoom, tracking shot?

### Step 2: Craft the Prompt

Transform the user request into an effective video generation prompt:

1. **Describe the scene**: Set the visual context
2. **Specify action**: What moves, changes, happens
3. **Include camera work**: "slow pan", "tracking shot", "static wide shot"
4. **Add style descriptors**: "cinematic", "documentary", "film grain"
5. **Set the mood**: Lighting, atmosphere, time of day

**Example transformation:**
- User: "a dog running on a beach"
- Enhanced: "Cinematic slow-motion shot of a golden retriever running joyfully along a pristine beach at sunset, waves gently lapping in the background, warm golden hour lighting, shallow depth of field, 4K quality, natural documentary style"

### Step 3: Select the API

**Default: Google Veo 3** (uses same API key as image generation)

1. **If only one API is available**: Use it automatically.

2. **If both APIs are available**: Default to **Veo 3** unless user specifically requests Sora.
   - Veo 3 uses the same `GOOGLE_API_KEY` as image generation
   - Only use Sora if user asks for it or needs features Veo lacks

| Use Case | Recommended API | Reason |
|----------|----------------|--------|
| Default / Quick | Veo 3 | Same API key, faster |
| Realistic scenes | Veo 3 | Natural physics |
| Cinematic/artistic | Sora | Best creative control |
| Complex motion | Sora | Better motion understanding |
| Longer videos (>8s) | Sora | Supports up to 20s |

### Step 4: Generate the Video

Execute the appropriate script from `${CLAUDE_PLUGIN_ROOT}/skills/video-generation/scripts/`:

**For OpenAI Sora:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/video-generation/scripts/sora.py \
  --prompt "your enhanced prompt" \
  --duration 10 \
  --resolution "1080p" \
  --aspect-ratio "16:9"
```

**For Google Veo 3:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/video-generation/scripts/veo.py \
  --prompt "your enhanced prompt" \
  --duration 8 \
  --aspect-ratio "16:9"
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

### For Cinematic Quality
- Include camera directions: "slow dolly", "tracking shot", "crane shot"
- Specify lighting: "golden hour", "dramatic shadows", "soft diffused light"
- Add film references: "Blade Runner style", "Wes Anderson aesthetic"

### For Realistic Motion
- Describe physics: "natural movement", "realistic physics"
- Include environmental details: "wind in hair", "leaves rustling"
- Specify speed: "slow motion", "real-time", "time-lapse"

### For Consistency
- Use detailed descriptions for subjects
- Maintain consistent style language
- Reference previous successful prompts

## API Comparison

| Feature | Veo 3 (Default) | Sora |
|---------|-----------------|------|
| Provider | Google | OpenAI |
| API Key | `GOOGLE_API_KEY` | `OPENAI_API_KEY` |
| Max duration | 8 seconds | 20 seconds |
| Resolution | Up to 1080p | Up to 1080p |
| Aspect ratios | 16:9, 9:16, 1:1 | 16:9, 9:16, 1:1 |
| Image-to-video | Yes | Yes |
| Best for | Realistic, fast | Creative, cinematic |
| Speed | Faster | Slower |
| Same key as images | ✅ Yes | ❌ No |
