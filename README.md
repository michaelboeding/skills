# Skills

> **Version 5.30.0** - Added search-trend-product-scout: turn category search trends and customer problems into ranked product ideas and illustrated reports

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
| `rembg` | ≥2.0.50 | background-remove, icon-generation |

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
│  ┌─────────────────────┐                                                    │
│  │ patent-prosecution- │                                                    │
│  │     agent           │                                                    │
│  │   5 sub-agents      │                                                    │
│  │   uses: patent-     │                                                    │
│  │     lawyer-agent    │                                                    │
│  └─────────────────────┘                                                    │
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
| [icon-generation](skills/icon-generation/) | Generate app icons with transparent backgrounds | `GOOGLE_API_KEY` |
| [background-remove](skills/background-remove/) | Remove backgrounds from images (AI-based) | None (`pip install rembg`) |
| [video-generation](skills/video-generation/) | Generate videos (Veo, Sora) | `GOOGLE_API_KEY` or `OPENAI_API_KEY` |
| [voice-generation](skills/voice-generation/) | Text-to-speech (Gemini TTS, ElevenLabs, OpenAI) | `GOOGLE_API_KEY`, `ELEVENLABS_API_KEY`, or `OPENAI_API_KEY` |
| [music-generation](skills/music-generation/) | Generate music (Lyria, Suno, Udio) | `GOOGLE_API_KEY`, `SUNO_API_KEY`, or `UDIO_API_KEY` |
| [chart-generation](skills/chart-generation/) | Data-driven charts (matplotlib) | None (`pip install matplotlib`) |
| [slide-generation](skills/slide-generation/) | PowerPoint slides from JSON | None (`pip install python-pptx`) |
| [device-framer](skills/device-framer/) | Wrap screenshots/recordings in iPhone frames | None (`pip install Pillow`, `brew install ffmpeg`) |
| [media-utils](skills/media-utils/) | Concat/mix audio/video (FFmpeg) | None (`brew install ffmpeg`) |
| [docx](skills/docx/) | Create/edit Word documents (OOXML) | None |
| [pptx](skills/pptx/) | Create/edit PowerPoint (advanced) | None (`npm install pptxgenjs`) |
| [xlsx](skills/xlsx/) | Create/edit Excel spreadsheets | None |
| [pdf](skills/pdf/) | PDF forms, extraction, validation | None |

---

## Research Skills

Focused research workflows with traceable sources:

| Skill | What It Does |
|-------|--------------|
| [search-trend-product-scout](skills/search-trend-product-scout/) | Research category search trends, customer problems, and competing products to rank ideas and create illustrated opportunity reports |
| [expired-patent-scout](skills/expired-patent-scout/) | Ask about brands/products and markets, research recent patent expirations, and produce illustrated product-opportunity reports |

---

## Coding Skills

Skills for development workflows (no API keys needed):

| Skill | What It Does |
|-------|--------------|
| [style-guide](skills/style-guide/) | Analyze codebase conventions, generate style guide |
| [ios-to-android](skills/ios-to-android/) | Port iOS/Swift features to Android/Kotlin |
| [android-to-ios](skills/android-to-ios/) | Port Android/Kotlin features to iOS/Swift |
| [mobile-parity-check](skills/mobile-parity-check/) | Audit iOS/Android UI and UX in simulators with matching fake data and illustrated PDF reports |
| [add-to-xcode](skills/add-to-xcode/) | Auto-register new files with Xcode projects |
| [sidequest](skills/sidequest/) | Spawn parallel Claude sessions in new terminal tabs |
| [debug-council](skills/debug-council/) | Multi-agent debugging with majority voting |
| [feature-council](skills/feature-council/) | Multi-agent feature implementation, synthesize best parts |
| [parallel-builder](skills/parallel-builder/) | Decompose plans into parallel tasks |
| [model-council](skills/model-council/) | Get consensus from multiple AI models |
| [auto-permissions-review](skills/auto-permissions-review-install/) | Per-session AI permission review using Claude Haiku |

### Auto Permissions Review

Reduces permission prompt fatigue by auto-approving safe operations and sending ambiguous commands to Haiku for review. Per-session — each terminal enables independently.

| Tool | Default mode | Accept-edits mode (Shift+Tab) |
|------|-------------|-------------------------------|
| `Read`, `Glob`, `Grep`, `LS`, `Agent` | instant allow | instant allow |
| Simple Bash (`ls`, `cat`, `find`, `git status`) | instant allow | instant allow |
| Complex Bash (pipes, substitution) | Haiku reviews | Haiku reviews |
| `Edit`, `Write` | normal prompt (you decide) | Haiku reviews |

```
/auto-permissions-review-install   # one-time setup
/auto-permissions-review-enable    # turn on (this session)
/auto-permissions-review-disable   # turn off (this session)
```

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
| [cmo-agent](skills/cmo-agent/) | AI CMO: SEO audit, content, Reddit, HN, X growth | 6 (seo, geo, content-writer, reddit, hackernews, x) | site_audit.py, chart-generation |
| [brand-research-agent](skills/brand-research-agent/) | Analyze brands from websites | 5 (visual, voice, product, audience, competitive) | None |
| [product-engineer-agent](skills/product-engineer-agent/) | Design products with specs + visuals | 5 (industrial, mechanical, user, manufacturing, innovation) | image-generation |
| [market-researcher-agent](skills/market-researcher-agent/) | Research markets (TAM/SAM/SOM) | 4 (trend, consumer, industry, opportunity) | chart-generation |
| [patent-lawyer-agent](skills/patent-lawyer-agent/) | Patent drafting + IP guidance | 5 (prior-art, patentability, claims, strategy, drafter) | image-generation |
| [patent-prosecution-agent](skills/patent-prosecution-agent/) | Office action responses + prosecution | 5 (analyzer, strategist, amendment-drafter, argument-writer, distinguisher) | patent-lawyer-agent |
| [competitive-intel-agent](skills/competitive-intel-agent/) | Analyze competitors | 4 (feature, pricing, positioning, market) | chart-generation, image-generation |
| [copywriter-agent](skills/copywriter-agent/) | Marketing copy | 4 (headlines, body, ads, CTA) | None |
| [review-analyst-agent](skills/review-analyst-agent/) | Analyze product reviews | 4 (scraper, sentiment, issues, recommendations) | chart-generation |
| [pitch-deck-agent](skills/pitch-deck-agent/) | Create pitch decks | Workflow | slide-generation, chart-generation, image-generation |

### Producer Agents

Create complete media by combining multiple generation skills:

| Agent | What It Creates | Skills Used |
|-------|-----------------|-------------|
| [walkthrough-script-agent](skills/walkthrough-script-agent/) | Walkthrough video scripts for app features | app-demo-agent, voice-gen |
| [video-producer-agent](skills/video-producer-agent/) | Complete videos with voiceover + music | video-gen, voice-gen, music-gen, media-utils |
| [podcast-producer-agent](skills/podcast-producer-agent/) | Podcast episodes, dialogues | voice-gen, music-gen, media-utils |
| [audio-producer-agent](skills/audio-producer-agent/) | Audiobooks, ads, jingles | voice-gen, music-gen, media-utils |
| [social-producer-agent](skills/social-producer-agent/) | Multi-asset content packs | image-gen, video-gen, voice-gen |
| [app-demo-agent](skills/app-demo-agent/) | Polished demos from screen recordings | device-framer, voice-gen, music-gen, media-utils |

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

Example: **patent-prosecution-agent** workflow (after office action received):

```
User: "Help me respond to this 103 rejection"
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│          patent-prosecution-agent                    │
│                                                     │
│  1. office-action-analyzer  → Parse rejections      │
│  2. prior-art-distinguisher → Analyze cited art     │
│  3. prosecution-strategist  → Pick strategy         │
│  4. claim-amendment-drafter → Rewrite claims        │
│  5. argument-writer         → Draft remarks         │
└─────────────────────────────────────────────────────┘
                    │
                    ▼
Output: Complete office action response + PDF
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

### CMO Specialists (for cmo-agent)

6 specialized marketing agents that work in parallel:

| Agent | Focus |
|-------|-------|
| `seo-analyst` | Technical SEO audit with exact HTML fix snippets |
| `geo-analyst` | AI search visibility (ChatGPT, Perplexity, Google AI Overview) |
| `content-writer` | Full SEO articles (1500-3000 words) + 4-week content calendar |
| `reddit-scout` | Active thread discovery + copy-paste-ready comments with risk assessment |
| `hackernews-scout` | Show HN submission + founder comment + objection responses |
| `x-scout` | Tweet threads + standalone tweets + 7-day calendar + influencer mapping |

Also includes `site_audit.py`: stdlib-only technical SEO crawler with 3-tier scoring (static analysis, PageSpeed Insights API, Lighthouse CLI).

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

### Prosecution Specialists (for patent-prosecution-agent)

5 specialized patent prosecution perspectives:

| Agent | Focus |
|-------|-------|
| `office-action-analyzer` | Parse rejections, map claims to references |
| `prosecution-strategist` | Response strategy, amend vs argue decisions |
| `claim-amendment-drafter` | Rewrite claims with proper amendment markup |
| `argument-writer` | Draft legal arguments and remarks |
| `prior-art-distinguisher` | Analyze cited art, find meaningful differences |

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

### search-trend-product-scout

Find product ideas from category search trends and evidence of unmet customer needs:

```text
Use search-trend-product-scout and ask me about the category, market, and product constraints.

Research hunting accessories for U.S. customers in the $25-$150 range.
Compare the same seasons across years, investigate recurring customer problems,
and rank differentiated product ideas I could prototype.
Create a PDF with trend charts, competing products, evidence, and next tests.
```

The skill asks about category/subcategory, customer, region/language, product type, price, manufacturing capabilities, budget, and research period, reusing information already provided. It uses multiple years for seasonal context and complete comparable periods for momentum when available. Hunting examples are query seeds, not claims about current trends.

It combines Google Trends data with optional keyword-volume estimates, reviews, customer discussions, and current products. Rankings consider the search signal, problem strength, differentiation, build feasibility, and commercial fit, with confidence and unknowns shown explicitly. Ideas include a smallest useful validation experiment and a reason to reject or revisit the concept.

The default deliverables are an illustrated PDF, editable Markdown, ranked opportunity CSV, source log, raw trend exports, and analysis JSON. Charts use measured data; the report identifies assumptions, sparse signals, access gaps, and proposed concepts. Optional follow-up can pass a chosen mechanism and target markets to expired-patent-scout.

Google Trends Explore and CSV exports provide a path when official API access is unavailable; verify access at run time. The API currently requires alpha access. Trends indices measure relative search interest rather than exact search counts or sales, and independently normalized exports cannot be compared as though they share one scale. Without trend data, the result is labeled a preliminary qualitative scan.

The Python 3.9+ standard-library CSV helper handles regular monthly, weekly, and daily Explore exports. It excludes partial intervals, preserves missing/censored values, compares prior-year periods, reports descriptive seasonality, and suppresses growth from very small baselines. It does not retrieve data or rank products. Run its synthetic tests with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 skills/search-trend-product-scout/scripts/test_analyze_trends.py
```

A quick live pilot on October 1, 2026 researched U.S. trail-camera power accessories: it retrieved Google Trends data, analyzed 260 complete weeks, withheld a sparse growth metric, screened existing products, and produced three ranked records with nine sources and a five-page PDF whose pages were visually inspected. The run also led to explicit guidance for exported weeks that overlap the selected date boundaries. This narrow pilot verifies the workflow for that case; specific product demand, economics, and reliability remain unvalidated. See [the skill](skills/search-trend-product-scout/SKILL.md) for intake and [the data guide](skills/search-trend-product-scout/references/trend-research.md) for formats, methods, and official sources.

---

### expired-patent-scout

Find engineering ideas and product opportunities in recently expired patents:

```text
Use expired-patent-scout and ask me which brands, products, or technology areas to research.

Find recently expired patents related to portable outdoor cooking products.
Focus on U.S. manufacturing and sales, and expirations in the last 24 months.
Create a PDF with patent figures, useful mechanisms, product concepts, and remaining risks.
```

The skill asks for target brands/products/problems, countries of manufacture/import/sale/use, and the desired expiration window. It uses a stated 24-month lookback when that preference is omitted and can add a separate upcoming-expiration list when requested. Constraints such as price point, manufacturing capability, and utility versus design interests refine the ranking.

It expands brand and assignee names, searches mechanisms and classifications, verifies territory-specific status against official records, and reviews granted claims and related active/pending rights. Natural term expirations, fee lapses with restoration uncertainty, upcoming expirations, and unverified/background records stay separate. A source label or old filing date alone cannot qualify a lead.

The default deliverable is an illustrated PDF with sourced patent figures, full opportunity analysis, status/date evidence, family and related-right notes, product concepts, and technical/legal follow-up questions. Editable Markdown, a candidate ledger, search log, and source evidence accompany it. The output is a research shortlist, not freedom-to-operate clearance or permission to copy an entire branded product.

The agent uses live patent research and available PDF tools. Some official records may require an account; access gaps are disclosed. The standard-library Python validator checks record consistency, dates, references, and shortlist prerequisites; it does not determine legal status or calculate patent terms. Run its synthetic tests with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 skills/expired-patent-scout/scripts/test_validate_candidates.py
```

No live portfolio research or PDF export is performed by the validator. A real target-specific run is needed to validate the complete research workflow. See [the skill](skills/expired-patent-scout/SKILL.md) for intake and evidence requirements.

---

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

### mobile-parity-check

Compare the UI and UX of both apps using isolated audit branches, an iOS Simulator and Android Emulator, and matching synthetic data:

```text
Use mobile-parity-check to compare /path/to/ios-app and /path/to/android-app.
iOS origin/main is the design reference; compare Android origin/develop.
Audit all screens, navigation, interaction states, and accessibility.
Generate a PDF with paired screenshots and full UI/UX analysis for the developers.
```

Also supports Android as the reference or a bidirectional comparison when design authority is unresolved. It pins both revisions, creates worktrees, uses repeatable fixtures, and compares layout, typography, copy, navigation, forms, loading/error states, responsive behavior, and accessibility. Native platform conventions are assessed by usability and intent.

Outputs a self-contained PDF with embedded paired screenshots, full UI/UX analysis, reproducible findings, severity, code locations, suggested fixes, retest criteria, and complete coverage. Markdown source and structured JSON accompany the PDF. Every PDF page is rendered and visually checked before delivery; blocked or untested states remain visible. Fixture/build checks support the UI/UX audit; broader backend audits and feature implementation are separate work. Reports are prepared for handoff and are not sent automatically.

The setup helper uses Python 3.9+ and Git. Simulator runs require macOS/Xcode, an Android SDK/emulator, and an available UI driver or the projects' UI test frameworks. See [the skill](skills/mobile-parity-check/SKILL.md) for the workflow.

**Report package:**

| File | Purpose |
|------|---------|
| `report.pdf` | Primary deliverable: embedded screen pairs, full analysis, prioritized findings, coverage, and developer handoff |
| `report.md` | Editable source with the same analysis and evidence captions |
| `findings.json`, `coverage.json` | Stable issue/checkpoint IDs, execution outcomes, and evidence references |
| `run.json`, fixtures, patches, raw evidence | Exact versions, setup, and artifacts needed to reproduce the audit |

This is an agent-driven workflow. The bundled `prepare_run.py` helper creates the isolated Git worktrees and run manifest; fixture integration, simulator interaction, and PDF generation are adapted to each app pair using available tools. Verify those stages with a real app pair before relying on a complete audit. Missing tooling or unexecuted checks must be reported as blocked or untested.

The helper's integration tests use disposable repositories and cover dry runs, pinned revisions, preservation of staged/unstaged/untracked changes and SSH remotes, invalid refs, branch/output collisions, and partial setup failures. Run them from the skills repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 skills/mobile-parity-check/scripts/test_prepare_run.py
```


---

### add-to-xcode

Automatically register newly created source files with Xcode projects:

```
Create a new ProfileViewModel.swift in the ViewModels folder
```

**What happens:**
1. Agent creates the Swift file
2. Agent runs `add_to_xcode.rb` to register it with the `.xcodeproj`
3. File appears in Xcode navigator and compiles with the target

**Manual usage:**
```bash
# After creating any source file in an Xcode project
ruby ${CLAUDE_PLUGIN_ROOT}/skills/add-to-xcode/scripts/add_to_xcode.rb Sources/MyNewFile.swift
```

**Supported files:** `.swift`, `.m`, `.mm`, `.c`, `.cpp`, `.h`

**Requires:** `gem install xcodeproj`

---

### sidequest

Spawn a new Claude Code session in a separate terminal to work on a different task:

```
/sidequest "Add a settings page with dark mode toggle"

/sidequest "Set up the database schema" --no-context

/sidequest  # Interactive prompt for task description
```

**What happens:**
1. Claude asks if you want to include a summary of the current chat
2. Opens a new Terminal/iTerm tab
3. Starts Claude with the sidequest task (and optional context)
4. You continue working in your original session

**Use when:** You're deep in a task but need to branch off for something else without losing your place.

**macOS only** (uses osascript for terminal control)

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

### icon-generation

Generate app icons with transparent backgrounds:

```
generate an icon for a music app

create a flat style settings gear icon

make a 3D shopping cart icon for my e-commerce app
```

### background-remove

Remove backgrounds from images:

```
remove the background from this photo

make this image transparent

cut out the product from this image
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

### device-framer

Wrap screenshots and screen recordings in photorealistic iPhone frames:

```
frame this screenshot in an iPhone 16 Pro

wrap this screen recording in a device mockup

put this in an iPhone 17 Pro in cosmic orange on a dark background
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

### cmo-agent

AI Chief Marketing Officer — enter a URL and get a full marketing team deployed:

```
be my AI CMO for https://mysite.com

run a full SEO audit on https://myapp.io and give me exact fixes

find Reddit and Hacker News opportunities for my product

write SEO articles for my site and create a content calendar
```

How it works:
1. **Onboarding** - Just provide a URL (+ optional context)
2. **Site Audit** - `site_audit.py` crawls the site, scores SEO/Accessibility/Performance/Best Practices
3. **6 agents deploy in parallel** - SEO, GEO, Content Writer, Reddit, HN, X/Twitter
4. **Cross-channel synthesis** - Narrative spines + content cascades across channels
5. **Dashboard** - Terminal-formatted overview with scores, opportunities, and prioritized actions

**Output includes:**
- SEO audit with exact HTML fix snippets (copy-paste ready)
- GEO recommendations with JSON-LD schema code
- Full 1500-3000 word SEO articles ready to publish
- Reddit comments for specific active threads (with risk levels)
- Show HN submission + founder comment + objection responses
- Tweet threads + 7-day content calendar + influencer targets
- Prioritized "Do This Now" action list

**Optional API keys:** `GOOGLE_PSI_API_KEY` for PageSpeed Insights scores, `lighthouse` CLI for full browser audit.

---

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

### patent-prosecution-agent

Respond to patent office actions and examiner rejections (companion to patent-lawyer-agent):

```
I received an office action rejecting my claims under 103, help me respond

analyze this office action and tell me what the examiner is saying

amend my claims to overcome this 102 rejection

write arguments distinguishing my invention over the cited prior art

I got a final rejection, should I file an RCE or appeal?

prepare an appeal brief for the PTAB
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

### app-demo-agent

Turn screen recordings into polished demo videos:

```
here's a screen recording of my app — turn it into a polished demo video

add voiceover to this screen recording: ~/Desktop/demo.mp4

take ~/Desktop/recording.mov, frame it in iPhone 17 Pro, add narration and music
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
