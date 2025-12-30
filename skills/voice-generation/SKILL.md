---
name: voice-generation
description: This skill should be used when the user asks to "generate voice", "create audio", "text to speech", "TTS", "read this aloud", "generate narration", "create voiceover", "synthesize speech", or needs AI voice generation using ElevenLabs or OpenAI TTS. Handles voice selection, audio generation, and delivery.
---

# Voice Generation Skill

Generate realistic speech and voice audio using AI text-to-speech APIs (ElevenLabs, OpenAI TTS).

## Prerequisites

Environment variables must be configured for the APIs to work. At least one API key is required:

- `ELEVENLABS_API_KEY` - For ElevenLabs high-quality voice synthesis
- `OPENAI_API_KEY` - For OpenAI TTS voices

See the repository README for setup instructions.

## Available APIs

### ElevenLabs (Recommended for quality)
- **Best for**: Natural-sounding voices, voice cloning, long-form content
- **Voices**: Large library of pre-made voices + custom voice cloning
- **Languages**: 29+ languages
- **Models**: Eleven Multilingual v2, Eleven Turbo v2

### OpenAI TTS (Recommended for simplicity)
- **Best for**: Quick, reliable text-to-speech with consistent quality
- **Voices**: alloy, echo, fable, onyx, nova, shimmer
- **Models**: tts-1 (fast), tts-1-hd (high quality)
- **Output**: MP3, Opus, AAC, FLAC

## Workflow

### Step 1: Understand the Request

Parse the user's voice request for:
- **Text content**: What should be spoken?
- **Voice type**: Male, female, specific character?
- **Tone**: Professional, casual, dramatic, cheerful?
- **Use case**: Narration, voiceover, audiobook, notification?
- **Language**: English, Spanish, other?
- **Speed**: Normal, slow, fast?

### Step 2: Select Voice and API

Choose based on requirements:

| Use Case | Recommended API | Reason |
|----------|----------------|--------|
| Audiobook/podcast | ElevenLabs | Most natural, best for long content |
| Quick narration | OpenAI TTS | Fast, reliable, good quality |
| Specific accent | ElevenLabs | Widest voice selection |
| Voice cloning | ElevenLabs | Only API with cloning |
| Budget-conscious | OpenAI TTS | Lower cost per character |

### Step 3: Prepare the Text

Optimize text for speech:

1. **Add pauses**: Use commas, periods for natural rhythm
2. **Spell out numbers**: "1,234" → "one thousand two hundred thirty-four" (if needed)
3. **Handle acronyms**: "NASA" vs "N.A.S.A." depending on pronunciation
4. **Mark emphasis**: Some APIs support emphasis markers

**Example transformation:**
- Original: "The Q4 2024 results show a 15% YoY increase."
- Optimized: "The Q4 2024 results show a fifteen percent year-over-year increase."

### Step 4: Generate the Audio

Execute the appropriate script from `${CLAUDE_PLUGIN_ROOT}/skills/voice-generation/scripts/`:

**For ElevenLabs:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/voice-generation/scripts/elevenlabs.py \
  --text "Your text here" \
  --voice "Rachel" \
  --model "eleven_multilingual_v2"
```

**For OpenAI TTS:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/voice-generation/scripts/openai_tts.py \
  --text "Your text here" \
  --voice "nova" \
  --model "tts-1-hd"
```

### Step 5: Deliver the Result

1. Provide the generated audio file path
2. Mention the voice and settings used
3. Offer to:
   - Try a different voice
   - Adjust speed or tone
   - Use a different API
   - Generate in a different format

## Error Handling

**Missing API key**: Inform the user which key is needed and how to set it up:
- ElevenLabs: https://elevenlabs.io
- OpenAI: https://platform.openai.com/api-keys

**Text too long**: Split into chunks and concatenate, or suggest shorter text.

**Rate limit**: Suggest waiting or trying a different API.

**Unsupported language**: Suggest an alternative API that supports the language.

## Voice Selection Guide

### OpenAI TTS Voices
| Voice | Description | Best For |
|-------|-------------|----------|
| alloy | Neutral, balanced | General purpose |
| echo | Warm, conversational | Podcasts, casual |
| fable | Expressive, British | Storytelling |
| onyx | Deep, authoritative | Narration, professional |
| nova | Friendly, upbeat | Marketing, tutorials |
| shimmer | Soft, gentle | Meditation, ASMR |

### ElevenLabs Popular Voices
| Voice | Description | Best For |
|-------|-------------|----------|
| Rachel | Young female, American | Narration, audiobooks |
| Domi | Young female, energetic | Marketing, ads |
| Bella | Young female, soft | Storytelling |
| Antoni | Young male, well-rounded | Narration |
| Josh | Young male, deep | Audiobooks |
| Arnold | Mature male, authoritative | Documentary |
| Adam | Middle-aged male, deep | Narration |
| Sam | Young male, raspy | Character voices |

## Best Practices

### For Narration
- Use a consistent voice throughout
- Add natural pauses between paragraphs
- Consider pacing for the content type

### For Dialogue
- Use different voices for different characters
- Match voice characteristics to character descriptions
- Adjust speed for emotional scenes

### For Accessibility
- Use clear, well-paced speech
- Avoid overly stylized voices
- Test with screen readers if applicable

## API Comparison

| Feature | ElevenLabs | OpenAI TTS |
|---------|------------|------------|
| Voice quality | Excellent | Very good |
| Voice variety | 100+ voices | 6 voices |
| Voice cloning | Yes | No |
| Languages | 29+ | 50+ |
| Speed control | Yes | Yes (0.25-4x) |
| Max length | 5,000 chars | 4,096 chars |
| Output formats | MP3, WAV | MP3, Opus, AAC, FLAC |
