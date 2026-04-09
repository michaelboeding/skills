---
name: walkthrough-script-agent
description: >
  Use this skill to generate walkthrough video scripts for app features.
  Triggers: "walkthrough script", "feature walkthrough", "app walkthrough script",
  "demo script", "video script for app", "feature tour script", "product walkthrough",
  "screen-by-screen script", "app feature scripts", "walkthrough narration",
  "tutorial script", "onboarding script", "feature highlight script"
  Outputs: Timed walkthrough scripts with narration, screen directions, and transitions for each app feature.
---

# Walkthrough Script Agent

Generate professional, screen-by-screen walkthrough video scripts for app features — ready for recording or voiceover production.

**This skill uses 3 specialized agents** that analyze your app, write feature scripts from different angles, then synthesize them into a polished script package.

## What It Produces

| Output | Description |
|--------|-------------|
| **Feature Scripts** | Individual timed scripts for each app feature |
| **Full Walkthrough** | Complete app tour script covering all features |
| **Screen Directions** | What to show on screen at each moment |
| **Narration Text** | Voiceover-ready narration with pacing cues |
| **Shot List** | Ordered list of screens/actions to capture |

## Prerequisites

- No API keys required
- Works best with app screenshots, screen recordings, or a detailed feature list
- Optionally pair with `app-demo-agent` to produce the final video

## Workflow

### Step 1: Gather App Context (REQUIRED)

⚠️ **DO NOT skip this step. Use interactive questioning — ask ONE question at a time.**

#### Question Flow

⚠️ **Use the `AskUserQuestion` tool for each question below.** Do not just print questions in your response — use the tool to create interactive prompts with the options shown.

**Q1: App Overview**
> "I'll write walkthrough scripts for your app! First — **what's the app called and what does it do?**
>
> *(A brief description is fine — e.g., 'Bubba Fishing — a fishing app for logging catches, tracking trips, and competing in tournaments')*"

*Wait for response.*

**Q2: Target Audience**
> "Who's the **target audience** for these walkthrough videos?
>
> - New users (onboarding/tutorial style)
> - Potential customers (marketing/conversion style)
> - Investors / stakeholders (pitch/demo style)
> - Internal team (training/documentation style)
> - Or describe"

*Wait for response. This determines tone, pacing, and emphasis.*

**Q3: Features to Cover**
> "Which **features** should I write scripts for?
>
> - **All major features** — I'll analyze the app and cover everything
> - **Specific features** — list the ones you want
> - **Single feature deep-dive** — one feature, thorough walkthrough"

*Wait for response. If they say "all", use the feature analyzer agent to identify them.*

**Q4: Source Material**
> "What do I have to work with?
>
> - **Screenshots** — provide paths to app screenshots
> - **Screen recording** — provide path to a recording
> - **Codebase** — I'll read the source code to understand features
> - **Description only** — you'll describe the screens to me
> - **Multiple sources** — combination of the above"

*Wait for response. More context = better scripts.*

**Q5: Video Style**
> "What **style** for the walkthrough?
>
> - **Quick tour** — fast-paced, 15-30s per feature, highlight reel
> - **Standard walkthrough** — 30-60s per feature, show key flows
> - **Detailed tutorial** — 60-90s per feature, step-by-step instructions
> - **Marketing showcase** — benefit-focused, emotional, persuasive
> - **Or describe your own style**"

*Wait for response.*

**Q6: Tone**
> "What **tone** should the narration use?
>
> - **Professional** — polished, confident, product demo feel
> - **Friendly / conversational** — casual, like showing a friend
> - **Energetic / excited** — upbeat, enthusiastic
> - **Calm / instructional** — patient, step-by-step
> - **Or describe**"

*Wait for response.*

**Q7: Output Format**
> "How do you want the scripts delivered?
>
> - **Markdown files** — one `.md` per feature + a master script (default)
> - **Single document** — everything in one file
> - **JSON** — structured data for programmatic use
> - **Ready for app-demo-agent** — formatted for direct handoff to video production"

*Wait for response.*

#### Quick Reference

| Question | Determines |
|----------|------------|
| App Overview | Context and domain knowledge |
| Target Audience | Tone, depth, and persuasion strategy |
| Features | Scope of scripts to generate |
| Source Material | How we analyze the app |
| Video Style | Pacing and duration targets |
| Tone | Narration voice and language |
| Output Format | Deliverable structure |

---

### Step 2: Analyze the App

Based on the source material provided, build a complete picture of the app's features and screens.

#### If screenshots provided:
Read each screenshot with the Read tool. Document what you see:
- Screen name / purpose
- Key UI elements and interactions
- Navigation flow between screens
- Feature entry points

#### If codebase provided:
Use the feature-analyzer agent to examine the source code:
- ViewControllers / screens
- Navigation flows (segues, routes)
- Key user-facing features
- Data models that map to features

#### If screen recording provided:
Extract frames for analysis:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/app-demo-agent/scripts/extract_frames.py \
  INPUT_VIDEO \
  -o ~/walkthrough_project/frames/ \
  --scene-detect \
  --timestamps
```

Read the extracted frames to map the flow.

#### If description only:
Work from the user's description, asking follow-up questions if any feature is unclear.

**Output a feature map** before proceeding:

```
Feature Map:
1. [Feature Name] — [Brief description] — [Key screens involved]
2. [Feature Name] — [Brief description] — [Key screens involved]
3. ...
```

Present this to the user for confirmation before writing scripts.

---

### Step 3: Generate Walkthrough Scripts

Deploy the specialized agents in parallel to write scripts for each feature:

#### Agent 1: Feature Analyzer
Examines the app and produces a structured breakdown of each feature including:
- User flow (step-by-step actions)
- Key screens and transitions
- Value proposition of the feature
- Common user goals within the feature

#### Agent 2: Script Writer
Takes each feature breakdown and writes the walkthrough script with:
- Timed narration synced to screen actions
- Screen direction notes (what to show/tap/scroll)
- Transition cues between screens
- Pacing matched to the chosen video style

#### Agent 3: Hook Writer
Creates compelling openings and closings:
- Feature intro hooks (why this feature matters)
- Transition lines between features
- Closing CTAs
- Full walkthrough intro and outro

---

### Step 4: Assemble the Script Package

Combine agent outputs into the final deliverable.

#### Per-Feature Script Format

Each feature script should follow this structure:

```markdown
# [Feature Name] Walkthrough

**Duration:** ~[X]s | **Style:** [chosen style] | **Tone:** [chosen tone]

## Shot List
1. [Screen/action to capture]
2. [Screen/action to capture]
3. ...

## Timed Script

| Time | Screen Direction | Narration |
|------|-----------------|-----------|
| 0-3s | [App opens to home screen] | "Opening hook line..." |
| 3-6s | [User taps feature button] | "Narration for this moment..." |
| 6-10s | [Feature screen loads] | "Narration continues..." |
| ... | ... | ... |

## Narration (Full Text)

> [Complete narration as a single flowing block — ready for TTS or voiceover recording]

## Notes
- [Any special recording instructions]
- [Suggested transitions or effects]
```

#### Master Walkthrough Script

If multiple features, also produce a master script that chains them together:

```markdown
# [App Name] — Complete Walkthrough

**Total Duration:** ~[X]min | **Features Covered:** [N]

## Script Order
1. App Intro (10-15s)
2. [Feature 1] (Xs)
3. [Transition] (3-5s)
4. [Feature 2] (Xs)
5. ...
6. Closing CTA (10-15s)

## Full Timed Script
[Combined timed table for the entire walkthrough]

## Full Narration
[Complete narration text — ready for a single recording session]
```

---

### Step 5: Deliver and Iterate

Save the scripts to the requested location (default: `~/walkthrough_scripts/[app-name]/`).

**Delivery message:**

"Your walkthrough scripts are ready!

**App:** [App Name]
**Features Scripted:** [N]
**Total Narration:** ~[X] words (~[Y] minutes at natural pace)

**Files:**
- `[feature-name].md` — per-feature scripts
- `master-walkthrough.md` — full app tour script
- `shot-list.md` — consolidated recording checklist

**Want me to:**
- Adjust tone or pacing for any feature?
- Add/remove features from the walkthrough?
- Generate a version optimized for a specific platform (TikTok, YouTube, etc.)?
- Hand off to `app-demo-agent` to produce the actual video?"

---

## Pacing Guide

| Style | Duration/Feature | Words/Feature | Pace |
|-------|-----------------|---------------|------|
| Quick tour | 15-30s | 30-60 words | Punchy, highlight key value |
| Standard | 30-60s | 60-120 words | Show key flow, explain benefits |
| Detailed tutorial | 60-90s | 120-180 words | Step-by-step, thorough |
| Marketing showcase | 20-45s | 40-90 words | Benefit-led, emotional hooks |

## Script Writing Rules

1. **Show, don't tell** — every narration line must match what's on screen
2. **Lead with value** — open each feature with WHY it matters, not what it is
3. **Use active voice** — "Tap the plus button" not "The plus button can be tapped"
4. **One idea per line** — keep narration lines to one action or concept
5. **Pause on transitions** — use `...` or `—` for natural breathing room
6. **End with a hook** — each feature should leave the viewer wanting to try it
7. **Name UI elements** — reference actual button names, labels, and screen titles
8. **Include timing cues** — mark where pauses, emphasis, or speed changes should occur

## Platform-Specific Adjustments

| Platform | Duration | Aspect | Script Notes |
|----------|----------|--------|-------------|
| **App Store preview** | 15-30s | 9:16 or 19.5:9 | Hook in first 3s, no audio assumed |
| **TikTok / Reels** | 15-60s | 9:16 | Fast cuts, text overlays, trending hooks |
| **YouTube** | 60s-5min | 16:9 | Can be thorough, SEO-friendly intro |
| **Product Hunt** | 30-60s | 16:9 | Focus on unique value, show key differentiator |
| **Investor demo** | 2-5min | 16:9 | Problem-solution framing, market context |
| **Onboarding** | 30-90s/feature | Device native | Patient, instructional, sequential |

---

## Integration with Other Skills

| Skill | Use Case |
|-------|----------|
| `app-demo-agent` | Produce the actual video from these scripts |
| `brand-research-agent` | Match brand voice and tone |
| `copywriter-agent` | Write marketing copy to accompany the videos |
| `voice-generation` | Generate voiceover audio from the narration text |
| `video-producer-agent` | Full video production with music and effects |
| `social-producer-agent` | Create social media cuts from the walkthrough |

---

## Agents

| Agent | File | Focus |
|-------|------|-------|
| Feature Analyzer | `feature-analyzer.md` | Breaks down app features and user flows |
| Script Writer | `script-writer.md` | Writes timed narration with screen directions |
| Hook Writer | `hook-writer.md` | Creates intros, transitions, and CTAs |

---

## Example Prompts

**Full app walkthrough:**
> "Write walkthrough scripts for all the features in my fishing app"

**Specific features:**
> "Generate walkthrough scripts for the tournament and logbook features"

**From screenshots:**
> "Here are screenshots of each screen — write a walkthrough video script for this flow"

**Marketing style:**
> "Write a marketing-style walkthrough script for our App Store preview video"

**With handoff:**
> "Write walkthrough scripts for my app, then use app-demo-agent to produce the videos"
