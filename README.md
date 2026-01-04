# Skills

> **Version 5.1.0** - Added slide-generation and review-analyst-agent

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
| [image-generation](skills/image-generation/) | Generate images using AI (Gemini 3 Pro Image, DALL-E 3). Reference images, editing, style transfer. | `GOOGLE_API_KEY` or `OPENAI_API_KEY` |
| [video-generation](skills/video-generation/) | Generate videos using AI (Veo 3.1 with audio, Sora). Text-to-video, image-to-video. | `GOOGLE_API_KEY` or `OPENAI_API_KEY` |
| [voice-generation](skills/voice-generation/) | Generate speech using AI TTS (Gemini TTS, ElevenLabs, OpenAI). Multi-speaker support. | `GOOGLE_API_KEY`, `ELEVENLABS_API_KEY`, or `OPENAI_API_KEY` |
| [music-generation](skills/music-generation/) | Generate music using AI (Lyria instrumental, Suno, Udio). | `GOOGLE_API_KEY`, `SUNO_API_KEY`, or `UDIO_API_KEY` |
| [slide-generation](skills/slide-generation/) | Create presentation slides (PPTX, Markdown). Used by pitch-deck-agent and others. | None (`pip install python-pptx`) |

---

## Professional Agent Skills

**Professional agents handle business operations** - research, strategy, design, and content creation. They use specialized sub-agents for comprehensive analysis.

| Agent | Purpose | Multi-Agent |
|-------|---------|-------------|
| [brand-research-agent](skills/brand-research-agent/) | Analyze brands from websites. Extract colors, typography, voice, audience. | ✅ 5 agents |
| [product-engineer-agent](skills/product-engineer-agent/) | Design new products. Create specs, BOM estimates, differentiation. | ✅ 5 agents |
| [market-researcher-agent](skills/market-researcher-agent/) | Research markets. TAM/SAM/SOM, trends, opportunities. | ✅ 4 agents |
| [patent-lawyer-agent](skills/patent-lawyer-agent/) | IP guidance. Prior art, patentability, claims drafting. | ✅ 4 agents |
| [pitch-deck-agent](skills/pitch-deck-agent/) | Create pitch decks. Investor, partner, customer presentations. | No (workflow) |
| [copywriter-agent](skills/copywriter-agent/) | Write marketing copy. Headlines, ads, landing pages, emails. | ✅ 4 agents |
| [competitive-intel-agent](skills/competitive-intel-agent/) | Analyze competitors. Features, pricing, positioning, battlecards. | ✅ 4 agents |
| [review-analyst-agent](skills/review-analyst-agent/) | Analyze product reviews. Find issues, prioritize improvements. | ✅ 4 agents |

**All professional agents use the `-agent` suffix** to indicate they are top-level autonomous workflows.

---

## Producer Agent Skills (Orchestrators)

**Producer agents combine multiple generation skills to create complete, polished media.** They handle the entire workflow: planning, generating assets, and assembling the final output.

```
┌─────────────────────────────────────────────────────────────┐
│              PRODUCER AGENTS (Orchestrators)                │
│         Plan → Generate → Assemble → Deliver                │
├─────────────────────────────────────────────────────────────┤
│  video-producer-agent    podcast-producer-agent             │
│  audio-producer-agent    social-producer-agent              │
└───────────────────────────┬─────────────────────────────────┘
                            │ uses
┌───────────────────────────▼─────────────────────────────────┐
│              GENERATION SKILLS (Single-purpose)             │
├─────────────────────────────────────────────────────────────┤
│  image-generation   video-generation   music-generation     │
│  voice-generation   slide-generation                        │
└───────────────────────────┬─────────────────────────────────┘
                            │ uses
┌───────────────────────────▼─────────────────────────────────┐
│                    MEDIA UTILS (Assembly)                   │
├─────────────────────────────────────────────────────────────┤
│  audio_concat    audio_mix    video_concat    video_merge   │
└─────────────────────────────────────────────────────────────┘
```

| Producer Agent | Creates | Example |
|----------------|---------|---------|
| [video-producer-agent](skills/video-producer-agent/) | Complete videos with voiceover + music | "Create a 30s product video for my headphones" |
| [podcast-producer-agent](skills/podcast-producer-agent/) | Podcast episodes, interviews, dialogues | "Create a 5min podcast about AI with two hosts" |
| [audio-producer-agent](skills/audio-producer-agent/) | Audiobooks, voiceovers, jingles, ads | "Create a 30s radio ad for our coffee brand" |
| [social-producer-agent](skills/social-producer-agent/) | Multi-asset content packs | "Create a launch kit: 1 reel, 5 carousel images" |

**All producer agents use `GOOGLE_API_KEY`** (same key for video, images, voice, music) and require **FFmpeg** for assembly.

### How Producers Work

1. **Understand** - Parse your request (duration, style, assets)
2. **Plan** - Create storyboard/manifest of what to generate
3. **Generate** - Call generation skills (Veo, Gemini TTS, Lyria, etc.)
4. **Assemble** - Stitch everything together with FFmpeg
5. **Deliver** - Provide final file + offer adjustments

### Example: Creating a Product Video

```
USER: "Create a 30-second product video for my new wireless earbuds"

PRODUCER WORKFLOW:
1. Asks: Duration? Style? Have product images?
2. Plans: 5 scenes (reveal, features, lifestyle, CTA)
3. Generates:
   - 5 video clips (Veo 3.1)
   - Voiceover script (Gemini TTS)
   - Background music (Lyria)
4. Assembles:
   - Concat clips with transitions
   - Mix voice + music (music ducks under voice)
   - Merge audio with video
5. Delivers: final_product_video.mp4

OUTPUT: Professional video with VO, music, transitions
```

### Prerequisites for Producers

```bash
# FFmpeg for media assembly
brew install ffmpeg      # macOS
apt install ffmpeg        # Linux

# Python package for Google APIs
pip install google-genai
```

### Using Professional Agents with Producers

Combine professional agents with producer agents for complete workflows:

```
USER: "Analyze Nike's brand, then create a product video for my sneakers"

WORKFLOW:
1. brand-research-agent analyzes nike.com
   → Extracts colors, typography, voice, audience
   → Saves brand_profile.json

2. video-producer-agent uses brand_profile.json
   → Matches Nike's visual style
   → Uses appropriate music mood
   → Follows voice guidelines

RESULT: Video that feels "Nike-like"
```

```
USER: "Research the smart home market, design a new product, then create a pitch deck"

WORKFLOW:
1. market-researcher-agent → Market report with TAM/SAM/SOM
2. product-engineer-agent → Product spec with BOM
3. patent-lawyer-agent → IP assessment
4. pitch-deck-agent → Investor presentation

RESULT: Complete product launch package
```

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

### Brand Analysts (for brand-research-agent)

5 specialized brand analysts that work in parallel:

| Agent | Focus |
|-------|-------|
| `visual-analyst` | Colors, typography, logo, imagery style |
| `voice-analyst` | Tone, messaging, taglines, copy patterns |
| `product-analyst` | Offerings, features, USPs, pricing |
| `audience-analyst` | Demographics, psychographics, pain points |
| `competitive-analyst` | Market position, competitors, differentiation |

Focus: Web scraping, pattern extraction, structured brand profile output.

### Product Engineers (for product-engineer-agent)

5 specialized engineering perspectives:

| Agent | Focus |
|-------|-------|
| `industrial-designer` | Form, ergonomics, aesthetics, user interaction |
| `mechanical-engineer` | Mechanism, materials, durability, assembly |
| `user-researcher` | User needs, pain points, usability |
| `manufacturing-advisor` | Feasibility, costs, production |
| `innovation-scout` | Existing solutions, patents, differentiation |

### Market Researchers (for market-researcher-agent)

4 specialized market analysis perspectives:

| Agent | Focus |
|-------|-------|
| `trend-analyst` | Market size, growth, trends, future outlook |
| `consumer-researcher` | Customer segments, behavior, needs |
| `industry-analyst` | Market structure, players, dynamics |
| `opportunity-finder` | Gaps, opportunities, entry points |

### Patent Analysts (for patent-lawyer-agent)

4 specialized IP perspectives:

| Agent | Focus |
|-------|-------|
| `prior-art-searcher` | Find existing patents, publications |
| `patentability-analyst` | Assess novelty, non-obviousness |
| `claims-strategist` | Draft claims, claim strategy |
| `ip-strategy-advisor` | Protection strategy, timing, costs |

### Copywriters (for copywriter-agent)

4 specialized copywriting perspectives:

| Agent | Focus |
|-------|-------|
| `headlines-writer` | Headlines, hooks, taglines |
| `body-copy-writer` | Long-form persuasive copy |
| `ad-copy-writer` | Platform-specific ad copy |
| `cta-specialist` | Calls to action, conversion copy |

### Competitive Analysts (for competitive-intel-agent)

4 specialized competitive analysis perspectives:

| Agent | Focus |
|-------|-------|
| `feature-analyst` | Product features, capabilities |
| `pricing-analyst` | Pricing models, value comparison |
| `positioning-analyst` | Brand positioning, messaging |
| `market-position-analyst` | Market share, company health |

### Review Analysts (for review-analyst-agent)

4 specialized review analysis perspectives:

| Agent | Focus |
|-------|-------|
| `review-scraper` | Find and collect reviews from platforms |
| `sentiment-analyzer` | Analyze sentiment, emotions, trends |
| `issue-identifier` | Categorize complaints, find patterns |
| `improvement-recommender` | Prioritize fixes, create action plans |

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

### slide-generation

Create presentation slides:

```
create slides from this content: [paste JSON]

generate a PowerPoint presentation for my pitch

make slides for my market research report
```

---

## Professional Agent Examples

### brand-research-agent

Analyze a brand from their website:

```
analyze the Nike brand from their website

research Apple's brand guidelines

what's the brand voice for Stripe?
```

### product-engineer-agent

Design new products:

```
design a new portable phone charger

I have an idea for a smart water bottle, help me develop it

create a product spec for a pet feeding device
```

### market-researcher-agent

Research markets and opportunities:

```
what's the market size for smart home devices?

research the plant-based food market trends

is there an opportunity in sustainable packaging?
```

### patent-lawyer-agent

IP guidance (informational only):

```
is my invention patentable?

search for prior art on foldable drone designs

should I patent this or keep it as trade secret?
```

### pitch-deck-agent

Create investor presentations:

```
create a pitch deck for my AI startup

build a seed round presentation

make investor slides for my SaaS company
```

### copywriter-agent

Write marketing copy:

```
write headlines for our product launch

create ad copy for our Black Friday sale

write landing page copy for our new app
```

### competitive-intel-agent

Analyze competitors:

```
analyze our competitors: Salesforce, HubSpot, Pipedrive

what are Notion's weaknesses?

create a competitive battlecard for sales
```

### review-analyst-agent

Analyze customer reviews:

```
analyze reviews for our product on Amazon

what are people complaining about with [competitor]?

find the top issues we should fix from customer feedback
```

---

## Producer Agent Examples

### video-producer-agent

Create complete videos with voiceover and music:

```
create a 30-second product video for my headphones

make a demo video for my SaaS app

create an explainer video about how our service works
```

### podcast-producer-agent

Create podcast episodes and dialogues:

```
create a 5-minute podcast about AI with two hosts

make a fake interview between Einstein and Elon Musk

create an educational podcast episode about climate change
```

### audio-producer-agent

Create voiceovers, audiobooks, and audio ads:

```
create a 30-second radio ad for our coffee brand

generate an audiobook narration for this chapter

make a meditation audio with calming background music
```

### social-producer-agent

Create social media content packs:

```
create a launch kit: 1 reel, 5 carousel images

make a week of social content for our product

create TikTok content for our new feature
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
