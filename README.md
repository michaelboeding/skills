# Skills

> **Version 3.4.0** - Gemini Nano Banana Pro image generation, ~/.config/skills/.env support

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
| [style-guide](skills/style-guide/) | Analyze codebase conventions with specialized agents (structure, naming, patterns, testing, frontend). Generates `.claude/codebase-style.md` style guide. | None |
| [ios-to-android](skills/ios-to-android/) | Use iOS/Swift as source of truth, implement equivalent feature in Android/Kotlin/Compose. Feature parity, not literal translation. | None |
| [android-to-ios](skills/android-to-ios/) | Use Android/Kotlin as source of truth, implement equivalent feature in iOS/Swift/SwiftUI. Feature parity, not literal translation. | None |
| [debug-council](skills/debug-council/) | Research-aligned self-consistency (Wang et al., 2022). Each agent debugs independently, majority voting. For bugs & algorithms. | None |
| [feature-council](skills/feature-council/) | Multi-agent feature implementation. Each agent builds the feature independently, then synthesizes best parts from each. | None |
| [parallel-builder](skills/parallel-builder/) | Divide-and-conquer from specs/plans. Decomposes a plan into independent tasks, assigns each to an agent, executes in parallel waves, then integrates. | None |
| [model-council](skills/model-council/) | Multi-model consensus - run problems through Claude, GPT, Gemini, Grok in parallel and compare (analysis only). | Optional: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `XAI_API_KEY` |
| [image-generation](skills/image-generation/) | Generate images using AI models (OpenAI DALL-E 3, Google Imagen 3). | `OPENAI_API_KEY` or `GOOGLE_API_KEY` |
| [video-generation](skills/video-generation/) | Generate videos using AI models (OpenAI Sora, Google Veo 3). | `OPENAI_API_KEY` or `GOOGLE_API_KEY` |
| [voice-generation](skills/voice-generation/) | Generate realistic speech using AI text-to-speech (ElevenLabs, OpenAI TTS). | `ELEVENLABS_API_KEY` or `OPENAI_API_KEY` |
| [music-generation](skills/music-generation/) | Generate music and songs using AI (Suno, Udio). | `SUNO_API_KEY` or `UDIO_API_KEY` |

---

## Agents

### Debug Solvers (for debug-council)

10 debug solver agents focused on finding bugs:

| Agents | Purpose |
|--------|---------|
| `debug-solver-1` through `debug-solver-10` | Independent bug finding and fixing |

Focus: Root cause analysis, finding the ONE correct fix, chain-of-thought debugging.

### Feature Solvers (for feature-council)

10 feature solver agents focused on building features:

| Agents | Purpose |
|--------|---------|
| `feature-solver-1` through `feature-solver-10` | Independent feature implementation |

Focus: Codebase pattern matching, edge case coverage, comprehensive implementation.

### Builder Solvers (for parallel-builder)

10 builder solver agents focused on implementing assigned pieces:

| Agents | Purpose |
|--------|---------|
| `builder-solver-1` through `builder-solver-10` | Implement assigned piece of decomposed plan |

Focus: File ownership, shared contracts, parallel execution, integration.

### Style Analyzers (for style-guide)

5 specialized analyzer agents, each focused on one aspect:

| Agent | Focus |
|-------|-------|
| `style-structure` | Folder organization, file layout, module patterns |
| `style-naming` | Naming conventions for files, variables, functions, classes |
| `style-patterns` | Error handling, data access, logging, configuration |
| `style-testing` | Test location, naming, structure, assertions |
| `style-frontend` | Component patterns, styling, state (if applicable) |

Focus: Language-agnostic detection, real examples from codebase, structured output.

---

Both debug and feature agent types:
- Same temperature (0.7) for sampling diversity
- Same tools (Read, Grep, Glob, LS)
- Use ultrathink (extended thinking)
- Explore the codebase independently

Builder agents are different:
- Lower temperature (0.4) for consistency
- Full tools including Write and Shell
- Implement assigned pieces only
- Follow shared contracts exactly

Council skills will ask you how many agents to use (3-10), or specify directly:

| Mode | Agents | Use Case |
|------|--------|----------|
| `debug council of 3` | 3 | Fast, simple bugs |
| `debug council of 5` | 5 | Standard debugging |
| `debug council of 10` | 10 | Critical bugs |
| `feature council of 3` | 3 | Simple features |
| `feature council of 5` | 5 | Standard features |
| `feature council of 10` | 10 | Complex features |

**Minimum 3 agents** for councils - needed for meaningful voting/synthesis.

Parallel-builder uses as many agents as needed based on task decomposition (up to 10).

These agents are invoked automatically by their skills and should not be called directly.

---

## Usage Examples

### style-guide

Analyze a codebase to extract its conventions and patterns. Generates a reusable style guide:

```
style guide

generate style guide for this project

analyze codebase conventions
```

How it works:
1. **Quick language detection** - Identifies project type
2. **5 specialized analyzers spawn in parallel**:
   - Structure: folder layout, modules
   - Naming: files, variables, functions, classes
   - Patterns: error handling, data access, logging
   - Testing: test location, naming, structure
   - Frontend: components, styling (if applicable)
3. **Synthesize findings** into comprehensive guide
4. **Save to `.claude/codebase-style.md`**

**Output:**
- Structured style guide with real examples
- Can be referenced by other skills (feature-council, debug-council)
- Run once per codebase, update when patterns change

---

### ios-to-android

Use iOS/Swift code as reference to implement the equivalent Android feature:

```
ios to android: implement this feature for Android

convert this Swift code to Kotlin

port UserProfile from iOS to Android
```

How it works:
1. **Analyze iOS code** - Understand feature behavior, data structures, logic
2. **Check Android context** - Look for existing patterns, style-guide
3. **Create implementation plan** - Map iOS components to Android equivalents
4. **Implement idiomatically** - Kotlin/Compose, not literal translation

**Key principle:** Same behavior, same data shapes, but idiomatic for each platform.

---

### android-to-ios

Use Android/Kotlin code as reference to implement the equivalent iOS feature:

```
android to ios: implement this feature for iOS

convert this Kotlin code to Swift

port UserProfile from Android to iOS
```

Works the same as ios-to-android but in reverse direction.

---

### debug-council

Research-aligned self-consistency for **debugging**. Each agent explores and debugs independently - no shared context:

```
debug council: fix this bug in my function

debug council of 5: important production issue

debug council of 10: critical bug, need maximum confidence
```

How it works (pure Wang et al., 2022):
1. **Raw user prompt** sent to all debug agents (no pre-processing)
2. Each agent **independently explores** the codebase
3. Each agent uses **ultrathink** to find the root cause
4. Solutions are grouped by their core fix
5. **Majority voting** selects the most common answer
6. Confidence based on voting distribution (5/7 agree = HIGH)

**Note:** This is slower than shared-context approaches because each agent explores independently. Use for critical bugs where accuracy matters more than speed.

### feature-council

Multi-agent feature implementation. Each agent builds the feature independently, then **synthesizes** the best parts:

```
feature council: implement user authentication with OAuth

feature council of 5: add caching layer to the API

feature council of 10: complex payment integration
```

How it works:
1. **Raw user prompt** sent to all agents (no pre-processing)
2. Each agent **independently explores** the codebase
3. Each agent implements the **complete feature**
4. Implementations are **compared** across multiple dimensions
5. **Synthesis** combines the best elements from each
6. **Implementation Plan** created with exact files and order
7. **Execute** plan step-by-step

**Output shows:**
- What each agent contributed
- Implementation plan with file order
- Synthesis breakdown (which agent provided what)

### parallel-builder

Divide-and-conquer implementation from specs, PRDs, or plans. Decomposes into parallel tasks:

```
parallel-builder from docs/auth-prd.md

parallel-builder: full CRUD API for blog with posts, comments, users

parallel-builder something like src/features/users but for products
```

How it works:
1. **Analyze the plan** - identify independent work units and dependencies
2. **Define shared contracts** - types/interfaces all agents must use
3. **Show execution plan** - user confirms task breakdown and waves
4. **Execute in waves** - parallel agents build their pieces simultaneously
5. **Integrate** - merge all pieces, resolve conflicts, verify

**Key differences from feature-council:**
- Each agent builds a **different piece** (not the same feature)
- Focus on **speed** via parallelization (not diversity of approaches)
- Agents respect **file ownership** (no overlaps)
- Results are **integrated** (not synthesized)

**Where it shines (maximum speedup):**
- Multi-file specs (types + services + routes + UI)
- CRUD APIs (each resource in separate files)
- Microservices (independent service files)
- Plugin/module systems

**Falls back to sequential when:**
- Multiple tasks modify the same file (to avoid conflicts)
- Still useful for organized task breakdown

**Output shows:**
- Wave execution progress
- Files created per agent
- Integration results
- Verification status
- Estimated vs actual speedup

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

### Agents Hitting Token Limits

If you see errors like:
```
API Error: Claude's response exceeded the 32000 output token maximum
```

**Solution:** Increase the max output tokens (only uses more when needed):

```bash
# Add to ~/.bashrc or ~/.zshrc
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=64000
```

Then restart Claude Code.

This commonly happens with `feature-council` on complex features where agents generate complete implementations. The 64K limit allows full outputs without truncation.

---

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
