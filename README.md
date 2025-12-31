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
# Core APIs (used by multiple skills)
export OPENAI_API_KEY="sk-..."          # DALL-E, Sora, TTS
export GOOGLE_API_KEY="..."             # Imagen, Veo, Gemini
export ELEVENLABS_API_KEY="..."         # ElevenLabs TTS

# Music Generation
export SUNO_API_KEY="..."               # Suno music
export UDIO_API_KEY="..."               # Udio music

# Model Council (optional)
export ANTHROPIC_API_KEY="sk-ant-..."   # Claude API
export XAI_API_KEY="..."                # Grok API
```

Restart your terminal or run `source ~/.bashrc` (or equivalent) for changes to take effect.

**Where to get API keys:**
- OpenAI: https://platform.openai.com/api-keys
- Google: https://aistudio.google.com/apikey
- ElevenLabs: https://elevenlabs.io
- Suno: https://suno.com
- Udio: https://udio.com
- Anthropic: https://console.anthropic.com/
- xAI: https://console.x.ai/

---

## Skills

| Skill | Description | API Keys |
|-------|-------------|----------|
| [code-council](skills/code-council/) | Ensemble problem-solving using 3 independent subagents. Each generates a solution in isolation, then synthesizes the best answer. | None |
| [model-council](skills/model-council/) | Multi-model consensus - run problems through Claude, GPT, Gemini, Grok in parallel and compare (analysis only). | Optional: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `XAI_API_KEY` |
| [image-generation](skills/image-generation/) | Generate images using AI models (OpenAI DALL-E 3, Google Imagen 3). | `OPENAI_API_KEY` or `GOOGLE_API_KEY` |
| [video-generation](skills/video-generation/) | Generate videos using AI models (OpenAI Sora, Google Veo 3). | `OPENAI_API_KEY` or `GOOGLE_API_KEY` |
| [voice-generation](skills/voice-generation/) | Generate realistic speech using AI text-to-speech (ElevenLabs, OpenAI TTS). | `ELEVENLABS_API_KEY` or `OPENAI_API_KEY` |
| [music-generation](skills/music-generation/) | Generate music and songs using AI (Suno, Udio). | `SUNO_API_KEY` or `UDIO_API_KEY` |

---

## Agents

Subagents used by the code-council skill for independent solution generation:

### Default (3 agents)
| Agent | Role | Purpose |
|-------|------|---------|
| [council-solver-a](agents/council-solver-a.md) | Straightforward | Conventional, direct solutions using established patterns |
| [council-solver-b](agents/council-solver-b.md) | Alternative | Creative, unconventional approaches |
| [council-solver-c](agents/council-solver-c.md) | Optimized | Performance-focused, production-ready solutions |

### Extended (5 agents) - for critical problems
| Agent | Role | Purpose |
|-------|------|---------|
| [council-solver-d](agents/council-solver-d.md) | Security | Edge cases, input validation, defensive coding |
| [council-solver-e](agents/council-solver-e.md) | Minimal | Elegant, simple solutions with fewest lines |

Use `code council of 5` for critical/security-sensitive code.

These agents are invoked automatically by code-council and should not be called directly.

---

## Usage Examples

### code-council

Spawns 3 independent solver subagents, each generating a solution in isolation, then synthesizes the best answer:

```
code council: fix this bug in my function

code council: write a function to find duplicates in an array

code council of 5: critical production bug, need extra confidence
```

How it works:
1. **Solver A** (straightforward) generates a conventional solution
2. **Solver B** (alternative) generates a creative/different approach  
3. **Solver C** (optimized) generates a production-ready solution
4. Claude Code synthesizes the best elements from all three

### model-council

Get consensus from multiple AI models (Claude, GPT, Gemini, Grok):

```
model council: review this architecture decision

model council with claude, gpt-4o: is this code secure?

model council all: critical decision, need all perspectives
```

### image-generation

Generate images with AI:

```
generate an image of a sunset over mountains

create a cyberpunk cityscape at night

make a watercolor painting of a cat
```

### video-generation

Generate videos with AI:

```
generate a video of waves crashing on a beach at sunset

create a cinematic drone shot flying over mountains

make a video of a cat playing with yarn
```

### voice-generation

Generate speech and audio:

```
read this text aloud: "Hello, welcome to my podcast"

generate a voiceover for this script

create narration for my video using a deep male voice
```

### music-generation

Generate music and songs:

```
create an upbeat pop song about summer

generate a cinematic orchestral soundtrack

make a lo-fi hip hop beat for studying
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

### Plugin Not Updating / Missing Skills

If you update the plugin but Claude Code still uses an old version, or skills are missing:

**The cache may be stale.** Clear it:

```bash
# Clear the plugin cache
rm -rf ~/.claude/plugins/cache/michaelboeding-skills
rm -rf ~/.claude/plugins/cache/temp_local_*
```

Then reinstall fresh in Claude Code:

```
/plugin remove skills@michaelboeding-skills
/plugin marketplace remove michaelboeding-skills
/plugin marketplace add michaelboeding/skills
/plugin install skills@michaelboeding-skills
```

Then **restart Claude Code**.

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
