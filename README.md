# Skills

Personal collection of agent skills using the open [SKILL.md standard](https://agentskills.io). Works with Claude (claude.ai, Claude Code, API), Cursor, and other AI assistants.

## Installation

### Claude Code

```bash
# Add the marketplace
/plugin marketplace add michaelboeding/skills

# Install the plugin
/plugin install skills@michaelboeding-skills
```

### Claude.ai

1. Download the `.skill` file from [Releases](../../releases)
2. Go to Settings → Skills
3. Upload the file

### Cursor / Other Tools

Copy the `skills/` folder to your project or follow your tool's skill installation docs.

---

## Setup

### API Keys (Required for some skills)

Some skills require API keys to function. Copy the example environment file and add your keys:

```bash
cp env.example .env
```

Then export the variables in your shell profile (`~/.bashrc`, `~/.zshrc`, or `~/.bash_profile`):

```bash
# Image Generation APIs
export OPENAI_API_KEY="sk-..."          # For DALL-E 3 + OpenAI TTS
export GOOGLE_API_KEY="..."             # For Google Imagen 3

# Voice Generation APIs
export ELEVENLABS_API_KEY="..."         # For ElevenLabs TTS
```

Restart your terminal or run `source ~/.bashrc` (or equivalent) for changes to take effect.

**Where to get API keys:**
- OpenAI: https://platform.openai.com/api-keys
- Google: https://aistudio.google.com/apikey
- ElevenLabs: https://elevenlabs.io

---

## Skills

| Skill | Description | API Keys |
|-------|-------------|----------|
| [code-council](skills/code-council/) | Ensemble problem-solving that generates multiple independent code solutions, tests them, and synthesizes the best answer. Based on [self-consistency research](https://arxiv.org/abs/2311.17311). | None |
| [image-generation](skills/image-generation/) | Generate images using AI models (OpenAI DALL-E 3, Google Imagen 3). Handles prompt crafting, API selection, and delivery. | `OPENAI_API_KEY` or `GOOGLE_API_KEY` |
| [voice-generation](skills/voice-generation/) | Generate realistic speech using AI text-to-speech (ElevenLabs, OpenAI TTS). Handles voice selection, text optimization, and audio delivery. | `ELEVENLABS_API_KEY` or `OPENAI_API_KEY` |

---

## Usage Examples

### code-council

Generate multiple code solutions and pick the best one:

```
code council: fix this bug in my function

code council: write a function to find duplicates in an array

code council of 5: critical production bug, need extra confidence
```

### image-generation

Generate images with AI:

```
generate an image of a sunset over mountains

create a cyberpunk cityscape at night

make a watercolor painting of a cat
```

### voice-generation

Generate speech and audio:

```
read this text aloud: "Hello, welcome to my podcast"

generate a voiceover for this script

create narration for my video using a deep male voice
```

---

## Troubleshooting

### Missing API Key Error

If you see an error like:
```
OPENAI_API_KEY environment variable not set
```

**Solution:**

1. Get your API key from the provider (links above)
2. Export it in your terminal:
   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   ```
3. For persistence, add the export to your shell profile (`~/.bashrc`, `~/.zshrc`, or `~/.bash_profile`)
4. Restart your terminal or run `source ~/.bashrc`

### API Rate Limit / Quota Exceeded

If you hit rate limits:
- Wait a few minutes and try again
- Check your API usage dashboard
- Upgrade your plan if needed
- Try a different API (e.g., Google instead of OpenAI)

### Generation Failed

Common causes:
- **Content policy violation**: Rephrase your prompt to be more appropriate
- **Network error**: Check your internet connection
- **Invalid parameters**: Check the error message for specifics

### Skill Not Triggering

If Claude doesn't use a skill when you expect it to:
- Use explicit trigger phrases (e.g., "generate an image of...")
- Check that the plugin is installed: `/plugin list`
- Update the plugin: `/plugin update skills@michaelboeding-skills`

### Script Errors

If a script fails to run:
1. Ensure Python 3 is installed: `python3 --version`
2. Check the API key is exported: `echo $OPENAI_API_KEY`
3. Run the script directly to see detailed errors:
   ```bash
   python3 ~/.claude/plugins/marketplaces/michaelboeding-skills/skills/image-generation/scripts/dalle.py --prompt "test" 
   ```

---

## Error Messages

All skills provide clear error messages when something goes wrong:

| Error | Meaning | Solution |
|-------|---------|----------|
| `API_KEY environment variable not set` | Missing API key | Export the required key (see Setup section) |
| `API error (401)` | Invalid API key | Check your key is correct and active |
| `API error (429)` | Rate limit exceeded | Wait and retry, or use different API |
| `API error (400)` | Bad request | Check your prompt/parameters |
| `Content policy violation` | Prompt rejected | Rephrase to be appropriate |
| `Text too long` | Exceeded character limit | Shorten your text or split into parts |

---

## License

MIT
