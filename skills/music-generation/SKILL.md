---
name: music-generation
description: This skill should be used when the user asks to "generate music", "create a song", "make music", "compose", "create a beat", "generate audio", "make a soundtrack", "create a jingle", or needs AI music generation using Suno or Udio. Handles prompt crafting, style selection, and audio delivery.
---

# Music Generation Skill

Generate music, songs, and audio using AI music generation APIs (Suno, Udio).

## Prerequisites

Environment variables must be configured. At least one API key is required:

- `SUNO_API_KEY` - For Suno music generation
- `UDIO_API_KEY` - For Udio music generation

See the repository README for setup instructions.

## Available APIs

### Suno (Recommended)
- **Best for**: Full songs with vocals, catchy melodies, various genres
- **Duration**: Up to 4 minutes
- **Features**: Lyrics generation, instrumental mode, style tags
- **Genres**: Pop, rock, jazz, electronic, classical, hip-hop, and more

### Udio
- **Best for**: High-fidelity audio, experimental styles, remixes
- **Duration**: Up to 2 minutes per generation
- **Features**: Style control, audio quality options
- **Genres**: Wide variety with strong electronic/experimental support

## Workflow

### Step 1: Understand the Request

Parse the user's music request for:
- **Genre/style**: Pop, rock, jazz, electronic, classical, etc.
- **Mood**: Happy, sad, energetic, calm, dramatic
- **Tempo**: Fast, slow, medium, specific BPM
- **Vocals**: With vocals, instrumental only
- **Purpose**: Background music, song, jingle, soundtrack
- **Duration**: How long should it be?

### Step 2: Craft the Prompt

Transform the user request into an effective music generation prompt:

1. **Specify genre**: Be specific about the style
2. **Describe mood**: Emotional tone and energy level
3. **Include instruments**: What should be prominent
4. **Add production style**: Lo-fi, polished, vintage, modern
5. **Set tempo**: BPM or descriptive (upbeat, slow)

**Example transformation:**
- User: "happy summer song"
- Enhanced: "Upbeat indie pop song with bright acoustic guitar, cheerful ukulele, and sunny vibes. Feel-good summer anthem with catchy hooks and positive energy. Male vocals, 120 BPM, radio-friendly production"

### Step 3: Handle Lyrics (If Needed)

For songs with vocals:
- **User provides lyrics**: Use them directly
- **Generate lyrics**: Ask Suno/Udio to generate, or use Claude to write them first
- **Instrumental**: Specify "instrumental" to skip vocals

Lyrics format for Suno:
```
[Verse 1]
Your lyrics here

[Chorus]
Catchy chorus lyrics

[Verse 2]
More lyrics
```

### Step 4: Select the API

Choose based on requirements:

| Use Case | Recommended API | Reason |
|----------|----------------|--------|
| Full songs with vocals | Suno | Best vocal quality |
| Instrumental/soundtrack | Either | Both work well |
| Experimental/electronic | Udio | Strong in these genres |
| Quick generation | Suno | Faster processing |
| Highest audio quality | Udio | Superior fidelity |

### Step 5: Generate the Music

Execute the appropriate script from `${CLAUDE_PLUGIN_ROOT}/skills/music-generation/scripts/`:

**For Suno:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/music-generation/scripts/suno.py \
  --prompt "upbeat indie pop, summer vibes, acoustic guitar" \
  --title "Summer Days" \
  --instrumental false
```

**For Udio:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/music-generation/scripts/udio.py \
  --prompt "cinematic orchestral, epic trailer music" \
  --duration 120
```

### Step 6: Deliver the Result

1. Provide the generated audio file path
2. Share the prompt and settings used
3. Mention the duration and format
4. Offer to:
   - Generate variations
   - Try different style/genre
   - Adjust tempo or mood
   - Extend the track
   - Add or remove vocals

## Error Handling

**Missing API key**: Inform the user which key is needed:
- Suno: https://suno.com/api (or app.suno.ai)
- Udio: https://udio.com/api

**Content policy violation**: Rephrase lyrics or prompt.

**Generation failed**: Retry with simplified prompt.

**Quota exceeded**: Suggest waiting or trying other provider.

## Prompt Engineering Tips

### Genre Tags (Suno Style)
Include specific genre tags for best results:
- `[pop, upbeat, female vocals, 128 BPM]`
- `[jazz, smooth, saxophone, laid-back]`
- `[electronic, synthwave, 80s, driving]`
- `[classical, orchestral, emotional, strings]`

### Mood Descriptors
- **Energetic**: upbeat, driving, powerful, intense
- **Calm**: relaxing, ambient, peaceful, gentle
- **Happy**: cheerful, bright, sunny, joyful
- **Sad**: melancholic, emotional, heartfelt, somber
- **Epic**: cinematic, dramatic, sweeping, grand

### Production Style
- **Lo-fi**: warm, vintage, tape hiss, nostalgic
- **Polished**: crisp, modern, radio-ready, professional
- **Raw**: garage, live, organic, unpolished
- **Electronic**: synthesizers, digital, processed

## API Comparison

| Feature | Suno | Udio |
|---------|------|------|
| Max duration | 4 minutes | 2 minutes |
| Vocals | Excellent | Good |
| Instrumentals | Great | Excellent |
| Genre variety | Wide | Wide |
| Audio quality | Very good | Excellent |
| Speed | Fast | Medium |
| Lyrics input | Yes | Yes |
| Extensions | Yes | Yes |

## Example Prompts

### Pop Song
```
Catchy pop song with female vocals, bright synths, and an anthemic chorus. 
Feel-good energy, summer vibes, 120 BPM, radio-friendly production.
```

### Cinematic Score
```
Epic orchestral trailer music with building tension. Powerful brass, 
sweeping strings, thundering percussion. Dramatic and emotional.
```

### Lo-fi Beat
```
Chill lo-fi hip hop beat, jazzy piano samples, vinyl crackle, 
relaxed drums, perfect for studying. 85 BPM, nostalgic mood.
```

### Electronic Dance
```
High-energy EDM track with massive drops, pulsing synths, 
four-on-the-floor beat. Festival-ready, 128 BPM.
```
