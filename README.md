# Skills

> **Version 5.17.0** - New add-to-xcode skill for automatic Xcode project file registration

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

## Python Dependencies

Many skills require Python packages. Run the install script:

```bash
# From the skills directory
./scripts/install.sh
```

Or install manually:

```bash
pip install -r requirements.txt
```

**Requirements:**
- Python 3.10+ (for `google-genai` package)
- pip

**What gets installed:**

| Package | Version | Used By |
|---------|---------|---------|
| `google-genai` | ≥1.0.0 | image-generation, video-generation, voice-generation, music-generation |
| `matplotlib` | ≥3.7.0 | chart-generation |
| `numpy` | ≥1.24.0 | chart-generation |
| `python-pptx` | ≥0.6.21 | slide-generation |
| `Pillow` | ≥10.0.0 | slide-generation, image processing |

**Optional tools:**

| Tool | Install | Used By |
|------|---------|---------|
| `ffmpeg` | `brew install ffmpeg` | media-utils, audio/video processing |

---

## Setup

### API Keys (Required for some skills)

Some skills require API keys to function. Copy the example environment file and add your keys:

```bash
# Copy to your config directory (recommended - keeps keys safe from git)
mkdir -p ~/.config/skills
cp env.example ~/.config/skills/.env
# Edit ~/.config/skills/.env with your keys
```

Then export the variables in your shell profile (`~/.bashrc`, `~/.zshrc`, or `~/.bash_profile`):

```bash
# Core APIs (used by multiple skills)
export OPENAI_API_KEY="sk-..."          # DALL-E, Sora, TTS
export GOOGLE_API_KEY="..."             # Imagen, Gemini (AI Studio)
export ELEVENLABS_API_KEY="..."         # ElevenLabs TTS

# Music Generation
export SUNO_API_KEY="..."               # Suno music
export UDIO_API_KEY="..."               # Udio music

# Model Council (optional)
export ANTHROPIC_API_KEY="sk-ant-..."   # Claude API
export XAI_API_KEY="..."                # Grok API
```

Restart your terminal or run `source ~/.bashrc` (or equivalent) for changes to take effect.

### Google Cloud / Vertex AI (Default for All Google Skills) ⭐

Vertex AI is the **default backend** for all Google-powered skills with higher rate limits:

| Skill | AI Studio | Vertex AI |
|-------|-----------|-----------|
| Video (Veo) | 10/day | 10/min |
| Voice (Gemini TTS) | Limited | Higher |
| Music (Lyria) | Limited | Higher |
| Image (Imagen) | Limited | Higher |

**Setup Vertex AI (one-time):**

```bash
# 1. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install

# 2. Login and set project
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID

# 3. Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# 4. Export project (add to .env or shell profile)
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"  # or us-east4
```

The video generation scripts auto-detect and use Vertex AI when `GOOGLE_CLOUD_PROJECT` is set.

**Where to get API keys:**
- OpenAI: https://platform.openai.com/api-keys
- Google AI Studio: https://aistudio.google.com/apikey
- Google Cloud: https://console.cloud.google.com/
- ElevenLabs: https://elevenlabs.io
- Suno: https://suno.com
- Udio: https://udio.com
- Anthropic: https://console.anthropic.com/
- xAI: https://console.x.ai/

### ⚠️ Credential Security

| ✅ Do | ❌ Don't |
|-------|---------|
| Store keys in `~/.config/skills/.env` | Commit `.env` files to git |
| Use `gcloud auth` for local dev | Hardcode keys in scripts |
| Use service accounts for CI/CD | Share API keys publicly |
| Rotate keys if exposed | Store keys in repo, even private |

**For CI/CD / Production:**

```bash
# Option 1: Service Account (recommended)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"

# Option 2: Workload Identity (GKE/Cloud Run)
# Automatically authenticated, no keys needed
```

---

## Skills vs Agents

**Everything is a skill** (has a SKILL.md file), but there are two types:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AGENT SKILLS (Higher-Level)                              │
│         Skills that orchestrate other skills + have sub-agents              │
│                                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐ │
│  │ patent-lawyer-agent │  │ product-engineer-   │  │ video-producer-     │ │
│  │   5 sub-agents      │  │     agent           │  │     agent           │ │
│  │   uses: image-gen   │  │   5 sub-agents      │  │   uses: video-gen   │ │
│  │         chart-gen   │  │   uses: image-gen   │  │         voice-gen   │ │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘ │
│                                      │ calls                                │
├──────────────────────────────────────▼──────────────────────────────────────┤
│                    BASE SKILLS (Single-Purpose)                             │
│               Do ONE thing well - can be used directly or by agents         │
│                                                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ image-gen    │ │ video-gen    │ │ voice-gen    │ │ music-gen    │       │
│  │ Generate     │ │ Generate     │ │ Generate     │ │ Generate     │       │
│  │ images       │ │ videos       │ │ speech       │ │ music        │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                        │
│  │ chart-gen    │ │ slide-gen    │ │ media-utils  │                        │
│  │ Data charts  │ │ PPTX slides  │ │ Concat/mix   │                        │
│  └──────────────┘ └──────────────┘ └──────────────┘                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Difference:**
- **Skills** = Single-purpose tools. Do ONE thing (generate an image, create a chart, make a video).
- **Agents** = Higher-level skills that orchestrate multiple other skills + have specialized sub-agents.

**Note:** Agents are still skills (they have SKILL.md files), but they're a higher-level type that combines other skills in their execution. Think of it as: agents are skills that use skills.

---

## Base Skills (Single-Purpose)

Base skills are focused tools that do one thing well. They can be used directly or called by agent skills.

| Skill | What It Does | API Keys |
|-------|--------------|----------|
| [image-generation](skills/image-generation/) | Generate/edit images (Gemini, DALL-E) | `GOOGLE_API_KEY` or `OPENAI_API_KEY` |
| [video-generation](skills/video-generation/) | Generate videos (Veo, Sora) | `GOOGLE_API_KEY` or `OPENAI_API_KEY` |
| [voice-generation](skills/voice-generation/) | Text-to-speech (Gemini TTS, ElevenLabs, OpenAI) | `GOOGLE_API_KEY`, `ELEVENLABS_API_KEY`, or `OPENAI_API_KEY` |
| [music-generation](skills/music-generation/) | Generate music (Lyria, Suno, Udio) | `GOOGLE_API_KEY`, `SUNO_API_KEY`, or `UDIO_API_KEY` |
| [chart-generation](skills/chart-generation/) | Data-driven charts (matplotlib) | None (`pip install matplotlib`) |
| [slide-generation](skills/slide-generation/) | PowerPoint slides (PPTX) | None (`pip install python-pptx`) |
| [media-utils](skills/media-utils/) | Concat/mix audio/video (FFmpeg) | None (`brew install ffmpeg`) |

---

## Coding Skills

Skills for development workflows (no API keys needed):

| Skill | What It Does |
|-------|--------------|
| [style-guide](skills/style-guide/) | Analyze codebase conventions, generate style guide |
| [ios-to-android](skills/ios-to-android/) | Port iOS/Swift features to Android/Kotlin |
| [android-to-ios](skills/android-to-ios/) | Port Android/Kotlin features to iOS/Swift |
| [debug-council](skills/debug-council/) | Multi-agent debugging with majority voting |
| [feature-council](skills/feature-council/) | Multi-agent feature implementation, synthesize best parts |
| [parallel-builder](skills/parallel-builder/) | Decompose plans into parallel tasks |
| [model-council](skills/model-council/) | Get consensus from multiple AI models |

---

## Agent Skills (Orchestrators)

Agent skills are higher-level skills that:
- **Call other base skills** (image-gen, chart-gen, voice-gen, etc.)
- **Have specialized sub-agents** for different perspectives
- **Handle complete workflows** from start to finish

**All agent skills use the `-agent` suffix** to indicate they orchestrate other skills.

### Professional Agents

Business analysis, research, and strategy:

| Agent | What It Does | Sub-Agents | Skills Used |
|-------|--------------|------------|-------------|
| [brand-research-agent](skills/brand-research-agent/) | Analyze brands from websites | 5 (visual, voice, product, audience, competitive) | None |
| [product-engineer-agent](skills/product-engineer-agent/) | Design products with specs + visuals | 5 (industrial, mechanical, user, manufacturing, innovation) | image-generation |
| [market-researcher-agent](skills/market-researcher-agent/) | Research markets (TAM/SAM/SOM) | 4 (trend, consumer, industry, opportunity) | chart-generation |
| [patent-lawyer-agent](skills/patent-lawyer-agent/) | Patent drafting + IP guidance | 5 (prior-art, patentability, claims, strategy, drafter) | image-generation |
| [competitive-intel-agent](skills/competitive-intel-agent/) | Analyze competitors | 4 (feature, pricing, positioning, market) | chart-generation, image-generation |
| [copywriter-agent](skills/copywriter-agent/) | Marketing copy | 4 (headlines, body, ads, CTA) | None |
| [review-analyst-agent](skills/review-analyst-agent/) | Analyze product reviews | 4 (scraper, sentiment, issues, recommendations) | chart-generation |
| [pitch-deck-agent](skills/pitch-deck-agent/) | Create pitch decks | Workflow | slide-generation, chart-generation, image-generation |

### Producer Agents

Create complete media by combining multiple generation skills:

| Agent | What It Creates | Skills Used |
|-------|-----------------|-------------|
| [video-producer-agent](skills/video-producer-agent/) | Complete videos with voiceover + music | video-gen, voice-gen, music-gen, media-utils |
| [podcast-producer-agent](skills/podcast-producer-agent/) | Podcast episodes, dialogues | voice-gen, music-gen, media-utils |
| [audio-producer-agent](skills/audio-producer-agent/) | Audiobooks, ads, jingles | voice-gen, music-gen, media-utils |
| [social-producer-agent](skills/social-producer-agent/) | Multi-asset content packs | image-gen, video-gen, voice-gen |

---

## How Agents Use Skills

Example: **patent-lawyer-agent** workflow:

```
User: "Draft a patent for my self-watering planter"
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│             patent-lawyer-agent                     │
│                                                     │
│  1. prior-art-searcher    → Finds existing patents  │
│  2. patentability-analyst → Assesses novelty        │
│  3. claims-strategist     → Drafts claims           │
│  4. ip-strategy-advisor   → Recommends approach     │
│  5. patent-drafter        → Writes full application │
│                    │                                │
│                    ▼ calls                          │
│         ┌─────────────────────┐                     │
│         │  image-generation   │ → Patent figures    │
│         └─────────────────────┘                     │
│         ┌─────────────────────┐                     │
│         │  chart-generation   │ → Patent landscape  │
│         └─────────────────────┘                     │
└─────────────────────────────────────────────────────┘
                    │
                    ▼
Output: Complete patent document + generated figures
```

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

5 specialized engineering perspectives + visual generation:

| Agent | Focus |
|-------|-------|
| `industrial-designer` | Form, ergonomics, aesthetics + **generates concept renders** |
| `mechanical-engineer` | Mechanism, materials, assembly + **generates exploded views** |
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

5 specialized IP perspectives:

| Agent | Focus |
|-------|-------|
| `prior-art-searcher` | Find existing patents, publications |
| `patentability-analyst` | Assess novelty, non-obviousness |
| `claims-strategist` | Draft claims, claim strategy |
| `ip-strategy-advisor` | Protection strategy, timing, costs |
| `patent-drafter` | Draft complete patent applications with generated figures |

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

### chart-generation

Generate data-driven charts from data:

```
create a bar chart comparing our features to competitors

plot our monthly revenue: [100, 150, 220, 350]

generate a competitive positioning matrix

create a TAM/SAM/SOM chart: TAM $50B, SAM $5B, SOM $500M

make a pie chart showing use of funds
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

Design new products with specs and visuals:

```
design a new portable phone charger

I have an idea for a smart water bottle, help me develop it

create a product spec for a pet feeding device

design a modular desk organizer and show me concept renders

create an exploded view of my product design
```

### market-researcher-agent

Research markets and opportunities:

```
what's the market size for smart home devices?

research the plant-based food market trends

is there an opportunity in sustainable packaging?
```

### patent-lawyer-agent

IP guidance and patent drafting (informational only):

```
is my invention patentable?

search for prior art on foldable drone designs

should I patent this or keep it as trade secret?

draft a full patent application for my invention

create a patent with figures for my self-watering planter
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

### Architecture Mismatch Error (Apple Silicon Macs)

If you see this error:
```
Architecture Mismatch Error
dlopen(...pydantic_core...incompatible architecture (have 'x86_64', need 'arm64'))
```

**Cause:** Pip installed x86_64 packages when running under Rosetta emulation.

**Fix:**
```bash
# Force arm64 architecture for pip installs
/usr/bin/arch -arm64 pip3 install --force-reinstall pydantic pydantic-core google-genai
```

**Prevention:**
1. Run the install script (it auto-detects Apple Silicon):
   ```bash
   ./scripts/install.sh
   ```
2. Or ensure Claude Code isn't running under Rosetta:
   - Right-click Claude Code app → Get Info
   - Uncheck "Open using Rosetta"
   - Restart Claude Code

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
