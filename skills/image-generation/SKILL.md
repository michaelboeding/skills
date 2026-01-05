---
name: image-generation
description: >
  Use this skill for any image-related AI generation or editing task. Triggers include:
  GENERATE: "generate image", "create image", "make picture", "draw", "visualize", "image of", "create art", "generate art"
  EDIT: "edit image", "modify image", "change image", "update image", "fix image", "enhance image"
  ADD/REMOVE: "add to image", "put in image", "remove from image", "delete from image", "add element"
  STYLE: "style transfer", "make it look like", "convert style", "apply style", "in the style of"
  PRODUCT: "product photo", "product placement", "place product", "mockup", "put product on"
  COMPOSITE: "combine images", "merge images", "blend images", "create composite"
  Supports text-to-image generation, image editing with references, product placement, style transfer, and multi-image composition using Google Gemini (Nano Banana Pro) or OpenAI DALL-E.
---

# Image Generation & Editing Skill

Generate and edit images using AI (Google Gemini Nano Banana Pro, OpenAI DALL-E 3).

**Capabilities:**
- 🎨 **Generate**: Create new images from text descriptions
- ✏️ **Edit**: Modify existing images (add/remove elements, change colors)
- 🛍️ **Product Placement**: Put products into scenes
- 🎭 **Style Transfer**: Apply artistic styles to photos
- 🖼️ **Composite**: Combine multiple images into one

## Quick Examples

Users can specify what they want:

| User Says | Mode | What Happens |
|-----------|------|--------------|
| "Generate an image of a sunset" | Generate | Text-to-image, no reference needed |
| "Create a logo for my coffee shop" | Generate | Text-to-image with text rendering |
| "Edit this image: add a hat to the cat" | Edit | User provides image, AI modifies it |
| "Remove the background from this photo" | Edit | User provides image, AI edits it |
| "Put this product on a kitchen counter" | Product | User provides product + optional scene |
| "Make this photo look like Van Gogh painted it" | Style | User provides photo, AI applies style |
| "Combine these photos into a group shot" | Composite | User provides multiple images |

## Prerequisites

Environment variables must be configured for the APIs to work. At least one API key is required:

- `OPENAI_API_KEY` - For OpenAI DALL-E 3 image generation
- `GOOGLE_API_KEY` - For Google Gemini (Nano Banana / Nano Banana Pro)

See the repository README for setup instructions.

## Available APIs

### OpenAI DALL-E 3
- **Best for**: High-quality, creative images with excellent prompt understanding
- **Sizes**: 1024x1024, 1024x1792, 1792x1024
- **Styles**: vivid (dramatic, hyper-real) or natural (realistic)
- **Quality**: standard or hd

### Google Gemini Native Image Generation (Recommended)
- **Nano Banana** (`gemini-2.5-flash-image`): Fast, efficient, 1K resolution, up to 3 reference images
- **Nano Banana Pro** (`gemini-3-pro-image-preview`): Professional quality, up to 4K, thinking mode, up to 14 reference images (default)
- **Aspect ratios**: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9
- **Resolutions** (Pro only): 1K, 2K, 4K
- **Features**: 
  - Image editing (add/remove elements, color changes)
  - Product placement and composition
  - Style transfer
  - Advanced text rendering
  - Google Search grounding (Pro only)
  - Thinking mode for complex prompts (Pro only)

## Workflow

### Step 1: Gather Requirements (REQUIRED)

⚠️ **Use interactive questioning — ask ONE question at a time.**

#### Question Flow

⚠️ **Use the `AskUserQuestion` tool for each question below.** Do not just print questions in your response — use the tool to create interactive prompts with the options shown.

**Q1: Reference**
> "I'll generate that image for you! First — **do you have any reference images?**
> 
> - Product photos to include
> - Style references
> - Images to edit
> - No, generate from scratch"

*Wait for response.*

**Q2: Aspect Ratio**
> "What **aspect ratio**?
> 
> - 1:1 (square)
> - 16:9 (landscape/widescreen)
> - 9:16 (portrait/vertical)
> - 4:3 / 3:4 (classic)
> - Other (2:3, 3:2, 4:5, 5:4, 21:9)
> - Or specify"

*Wait for response.*

**Q3: Resolution**
> "What **resolution**?
> 
> - 1K (fast)
> - 2K (balanced)
> - 4K (highest quality)"

*Wait for response.*

**Q4: Style**
> "Any **style preferences**?
> 
> - Photorealistic
> - Artistic/painterly
> - Cartoon/illustration
> - 3D render
> - Or describe your own"

*Wait for response.*

#### Quick Reference

| Question | Determines |
|----------|------------|
| Reference | Generation vs editing mode |
| Aspect Ratio | Image dimensions |
| Resolution | Quality level |
| Style | Prompt enhancement direction |

**Parsing:**
- If user provides reference images → use image editing mode
- If user doesn't answer all questions → use sensible defaults and note assumptions
- Parse: subject, style, mood, special requirements (colors, text, composition)

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

Check which API keys are available and let the user choose:

1. **Check which API keys are configured** in environment:
   - `OPENAI_API_KEY` → DALL-E 3 available
   - `GOOGLE_API_KEY` → Gemini (Nano Banana Pro) available

2. **If only one API is available**: Use it automatically, no need to ask.

3. **If both APIs are available**: Default to **Google Gemini (Nano Banana Pro)** unless the user specifically requests DALL-E.
   - Gemini is preferred because: up to 4K resolution, reference image support, advanced text rendering
   - Only use DALL-E if user asks for it or if Gemini fails

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

**For Google Gemini (Nano Banana Pro) - Text to Image:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/image-generation/scripts/gemini.py \
  --prompt "your enhanced prompt" \
  --model "gemini-3-pro-image-preview" \
  --aspect-ratio "1:1" \
  --resolution "2K"
```

**For Google Gemini - With Reference Images (editing, product placement, etc.):**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/image-generation/scripts/gemini.py \
  --prompt "Add a wizard hat to this cat" \
  --image "/path/to/cat.jpg" \
  --aspect-ratio "1:1" \
  --resolution "2K"
```

**For Google Gemini - Multiple Reference Images (composition, style transfer):**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/image-generation/scripts/gemini.py \
  --prompt "Place this product on the kitchen counter in this scene" \
  --image "/path/to/product.png" \
  --image "/path/to/kitchen.jpg" \
  --aspect-ratio "16:9" \
  --resolution "2K"
```

**For Google Gemini (Nano Banana - faster, fewer features):**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/image-generation/scripts/gemini.py \
  --prompt "your enhanced prompt" \
  --model "gemini-2.5-flash-image" \
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

## Reference Image Use Cases (Gemini Only)

Nano Banana and Nano Banana Pro support reference images for advanced editing:

### Image Editing
- "Add a santa hat to this person" + person.jpg
- "Remove the background and replace with a beach scene" + product.jpg
- "Change the sofa color to blue" + living_room.jpg

### Product Placement
- "Place this product on a marble kitchen counter" + product.png + kitchen.jpg
- "Show this watch on a person's wrist" + watch.png + arm.jpg

### Style Transfer
- "Transform this photo into Van Gogh's Starry Night style" + photo.jpg
- "Make this look like a watercolor painting" + landscape.jpg

### Multi-Image Composition
- "Create a group photo of these people in an office" + person1.jpg + person2.jpg + person3.jpg
- "Combine these elements into a cohesive scene" + element1.png + element2.png + background.jpg

### Character Consistency
- "Show this character from a different angle" + character.jpg
- "Put this person in a superhero costume" + person.jpg

**Tip**: For best results with reference images, be specific about what you want to preserve vs. change.

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

| Feature | DALL-E 3 | Nano Banana | Nano Banana Pro |
|---------|----------|-------------|-----------------|
| Provider | OpenAI | Google | Google |
| Model | dall-e-3 | gemini-2.5-flash-image | gemini-3-pro-image-preview |
| Best for | Creative, artistic | Fast generation | Professional assets |
| Max Resolution | 1792x1024 | 1K | 4K |
| Aspect ratios | 3 options | 10 options | 10 options |
| Reference images | No | Up to 3 | Up to 14 |
| Image editing | No | Yes | Yes |
| Product placement | No | Yes | Yes |
| Style transfer | No | Yes | Yes |
| Styles | vivid, natural | N/A | N/A |
| Text rendering | Good | Good | Excellent |
| Thinking mode | No | No | Yes |
| Google Search grounding | No | No | Yes |
| Speed | ~15-30s | ~10-20s | ~30-60s |
