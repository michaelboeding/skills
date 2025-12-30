---
name: image-generation
description: This skill should be used when the user asks to "generate an image", "create an image", "make a picture", "draw", "visualize", "image of", "generate art", "create artwork", or needs AI image generation using OpenAI DALL-E or Google Imagen. Handles prompt crafting, API selection, and image delivery.
---

# Image Generation Skill

Generate images using AI image generation APIs (OpenAI DALL-E 3, Google Imagen 3).

## Prerequisites

Environment variables must be configured for the APIs to work. At least one API key is required:

- `OPENAI_API_KEY` - For OpenAI DALL-E 3 image generation
- `GOOGLE_API_KEY` - For Google Imagen 3 (via Gemini API)

See the repository README for setup instructions.

## Available APIs

### OpenAI DALL-E 3 (Recommended)
- **Best for**: High-quality, creative images with excellent prompt understanding
- **Sizes**: 1024x1024, 1024x1792, 1792x1024
- **Styles**: vivid (dramatic, hyper-real) or natural (realistic)
- **Quality**: standard or hd

### Google Imagen 3
- **Best for**: Photorealistic images, detailed scenes
- **Aspect ratios**: 1:1, 16:9, 9:16, 4:3, 3:4
- **Features**: Built-in safety filters, fast generation

## Workflow

### Step 1: Understand the Request

Parse the user's image request for:
- **Subject**: What should be in the image?
- **Style**: Photorealistic, artistic, cartoon, abstract, etc.
- **Mood**: Dark, bright, cheerful, dramatic, etc.
- **Aspect ratio**: Square, portrait, landscape?
- **Special requirements**: Specific colors, composition, references

### Step 2: Craft the Prompt

Transform the user request into an effective image generation prompt:

1. **Be specific**: Add details the user might not have mentioned
2. **Describe style**: "digital art", "oil painting", "photograph", "3D render"
3. **Include lighting**: "soft lighting", "dramatic shadows", "golden hour"
4. **Specify quality**: "highly detailed", "8k", "professional"

**Example transformation:**
- User: "a cat in space"
- Enhanced: "A majestic orange tabby cat floating in outer space, surrounded by colorful nebulae and distant stars, wearing a small astronaut helmet, digital art style, highly detailed, vibrant colors, cinematic lighting"

### Step 3: Select the API

Choose based on availability and use case:

1. **Check which API keys are available** in environment
2. **Match to use case**:
   - Creative/artistic → DALL-E 3 (vivid style)
   - Photorealistic → DALL-E 3 (natural style) or Imagen 3
   - Fast generation → Imagen 3

### Step 4: Generate the Image

Execute the appropriate script from `${CLAUDE_PLUGIN_ROOT}/skills/image-generation/scripts/`:

**For OpenAI DALL-E 3:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/image-generation/scripts/dalle.py \
  --prompt "your enhanced prompt" \
  --size "1024x1024" \
  --style "vivid" \
  --quality "hd"
```

**For Google Imagen 3:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/image-generation/scripts/gemini.py \
  --prompt "your enhanced prompt" \
  --aspect-ratio "1:1"
```

### Step 5: Deliver the Result

1. Show the generated image to the user
2. Provide the enhanced prompt used (so they can iterate)
3. Offer to:
   - Generate variations
   - Try a different style
   - Use a different API/model
   - Refine the prompt

## Error Handling

**Missing API key**: Inform the user which key is needed and how to set it up:
- OpenAI: https://platform.openai.com/api-keys
- Google: https://aistudio.google.com/apikey

**API rate limit**: Suggest waiting or trying the other API.

**Content policy violation**: Rephrase the prompt to be more appropriate.

**Generation failed**: Retry with simplified prompt or different API.

## Prompt Engineering Tips

### For Photorealism
- Include "photograph", "DSLR", "35mm film"
- Specify camera settings: "shallow depth of field", "bokeh"
- Add lighting: "natural light", "studio lighting"

### For Artistic Styles
- Reference art movements: "impressionist", "art nouveau", "cyberpunk"
- Name artist styles: "in the style of Studio Ghibli", "Moebius style"
- Specify medium: "watercolor", "oil painting", "pencil sketch"

### For Consistency
- Use seed values when available
- Save successful prompts for reference
- Note which API produced best results for similar requests

## API Comparison

| Feature | DALL-E 3 | Imagen 3 |
|---------|----------|----------|
| Provider | OpenAI | Google |
| Best for | Creative, artistic | Photorealistic |
| Sizes | 1024², 1024x1792, 1792x1024 | Various aspect ratios |
| Styles | vivid, natural | N/A |
| Quality options | standard, hd | N/A |
| Speed | ~15-30 seconds | ~10-20 seconds |
