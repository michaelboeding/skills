# Skills

> **Version 2.0.0** - Research-aligned code-council with self-consistency (Wang et al., 2022)

Personal collection of agent skills using the open [SKILL.md standard](https://agentskills.io). Works with Claude Code and other AI assistants.

## Installation

### Claude Code

```bash
# Add the marketplace
/plugin marketplace add michaelboeding/skills

# Install the plugin
/plugin install skills@michaelboeding-skills
```

### Other Tools

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
| [code-council](skills/code-council/) | Research-aligned self-consistency (Wang et al., 2022). Spawns 5-10 identical solvers, uses majority voting to select answer. | None |
| [model-council](skills/model-council/) | Multi-model consensus - run problems through Claude, GPT, Gemini, Grok in parallel and compare (analysis only). | Optional: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `XAI_API_KEY` |
| [image-generation](skills/image-generation/) | Generate images using AI models (OpenAI DALL-E 3, Google Imagen 3). | `OPENAI_API_KEY` or `GOOGLE_API_KEY` |
| [video-generation](skills/video-generation/) | Generate videos using AI models (OpenAI Sora, Google Veo 3). | `OPENAI_API_KEY` or `GOOGLE_API_KEY` |
| [voice-generation](skills/voice-generation/) | Generate realistic speech using AI text-to-speech (ElevenLabs, OpenAI TTS). | `ELEVENLABS_API_KEY` or `OPENAI_API_KEY` |
| [music-generation](skills/music-generation/) | Generate music and songs using AI (Suno, Udio). | `SUNO_API_KEY` or `UDIO_API_KEY` |

---

## Agents

### Code Council Solvers (Research-Aligned)

10 identical solver agents used by code-council for self-consistency:

| Agents | Purpose |
|--------|---------|
| `council-solver-1` through `council-solver-10` | Independent solution generation |

**All agents are identical** - same prompt, same temperature (0.7), same instructions.

This follows the self-consistency research (Wang et al., 2022):
- Diversity comes from sampling randomness, not different prompts
- Majority voting selects the most likely correct answer
- More agents = higher confidence

The skill will ask you how many agents to use (1-10), or specify directly:

| Mode | Agents |
|------|--------|
| `code council` | Asks you to choose |
| `code council of 3` | 3 agents (fast) |
| `code council of 5` | 5 agents (standard) |
| `code council of 7` | 7 agents (important) |
| `code council of 10` | 10 agents (maximum) |

These agents are invoked automatically by code-council and should not be called directly.

---

## Usage Examples

### code-council

Research-aligned self-consistency. Spawns multiple independent solvers with identical prompts, then uses majority voting:

```
code council: fix this bug in my function

code council: write a function to find duplicates in an array

code council of 10: critical production bug, need maximum confidence
```

How it works (based on Wang et al., 2022):
1. Orchestrator gathers context and prepares problem statement
2. **Same prompt** sent to 5-10 identical solver agents
3. Each agent uses **ultrathink** (extended thinking) to reason deeply
4. Solutions are grouped by their core approach
5. **Majority voting** selects the most common answer
6. Confidence based on voting distribution (5/5 agree = HIGH)

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

**Quick fix - run the update script:**

```bash
# From the skills repo directory
./scripts/update-plugin.sh
```

**Or manually clear the cache:**

```bash
rm -rf ~/.claude/plugins/cache/michaelboeding-skills
rm -rf ~/.claude/plugins/cache/temp_local_*
```

Then in Claude Code:

```
/plugin update skills@michaelboeding-skills
```

Then **restart Claude Code** (quit and reopen - required for changes to take effect).

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
