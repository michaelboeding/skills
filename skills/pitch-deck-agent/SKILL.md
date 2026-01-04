---
name: pitch-deck-agent
description: >
  Use this skill to create investor pitch decks, partnership presentations, or business proposals.
  Triggers: "pitch deck", "investor deck", "fundraising presentation", "startup pitch",
  "investor presentation", "VC pitch", "seed deck", "series A deck", "business proposal",
  "partnership pitch", "sales deck", "demo day"
  Outputs: Structured slide content, talking points, and optional generated visuals.
---

# Pitch Deck Agent

Create compelling pitch decks for investors, partners, or customers.

**This is a structured workflow skill** that guides you through building a complete pitch deck, then generates content and visuals for each slide.

## What It Produces

| Output | Description |
|--------|-------------|
| **Slide Content** | Text, bullet points, key messages for each slide |
| **Talking Points** | What to say for each slide |
| **Visual Concepts** | Image prompts or generated visuals |
| **Appendix Slides** | Backup slides for Q&A |

## Prerequisites

- For generated images: `GOOGLE_API_KEY` (uses image-generation skill)
- Works without API keys (text content only)

## Standard Pitch Deck Structure

```
1. Title / Hook
2. Problem
3. Solution
4. Market Opportunity
5. Product / Demo
6. Business Model
7. Traction
8. Competition
9. Team
10. Financials / Ask
11. Closing / Contact
---
Appendix: Detailed metrics, references, backup slides
```

## Workflow

### Step 1: Gather Business Information

**Ask the user:**

> "I'll help you create a compelling pitch deck!
>
> Tell me about your business:
> 1. **What do you do?** (one sentence)
> 2. **What problem do you solve?** (the pain point)
> 3. **Who is your customer?** (target market)
> 4. **What's your traction?** (users, revenue, growth)
> 5. **What's the ask?** (investment amount, partnership goal)
>
> Also helpful:
> - Any existing materials? (website, one-pager, etc.)
> - What's the audience? (VC, angel, corporate partner)
> - Presentation length? (5 min, 10 min, demo day)"

**Wait for the user to provide business details.**

---

### Step 2: Research and Validate (Optional)

If the user provides a website or limited info, use:
- `brand-research-agent` - Extract brand elements
- `market-researcher-agent` - Get market size data
- `competitive-intel-agent` - Understand competitive landscape

---

### Step 3: Build Slide-by-Slide Content

Generate content for each slide:

#### Slide 1: Title / Hook
```
Content:
- Company name and logo
- Tagline / one-liner
- Presenter name and contact
- Optional: Compelling statistic or hook

Visual: Logo, clean design, brand colors
```

#### Slide 2: Problem
```
Content:
- Clear statement of the problem
- Who has this problem (and how many)
- Current solutions and why they fail
- Emotional hook / story

Visual: Icon or illustration of pain point
```

#### Slide 3: Solution
```
Content:
- Your solution in one sentence
- How it works (simple explanation)
- Key benefits (3 max)
- "Magic moment" - what makes it special

Visual: Product screenshot or demo
```

#### Slide 4: Market Opportunity
```
Content:
- TAM, SAM, SOM with clear definitions
- Market growth rate
- Why now (timing/trends)
- Your wedge into the market

Visual: Market size chart, growth graph
```

#### Slide 5: Product / Demo
```
Content:
- Product screenshots or demo
- Key features (3-5 max)
- User workflow
- Technology/IP if relevant

Visual: Product screenshots, demo video thumbnail
```

#### Slide 6: Business Model
```
Content:
- How you make money
- Pricing model
- Unit economics (LTV, CAC, etc.)
- Revenue streams

Visual: Simple pricing table or revenue model diagram
```

#### Slide 7: Traction
```
Content:
- Key metrics (users, revenue, growth)
- Growth chart (up and to the right)
- Notable customers/logos
- Key milestones achieved

Visual: Growth chart, customer logos
```

#### Slide 8: Competition
```
Content:
- Competitive landscape (2x2 matrix preferred)
- Your differentiation
- Moat / defensibility
- Why you win

Visual: Competitive matrix, positioning chart
```

#### Slide 9: Team
```
Content:
- Founders with relevant experience
- Key hires and why they joined
- Advisors (if notable)
- Why this team wins

Visual: Team photos, company logos of past experience
```

#### Slide 10: Financials / Ask
```
Content:
- What you're raising
- Use of funds (3-4 categories)
- Key milestones this funding enables
- Current investors (if any)

Visual: Pie chart of use of funds, milestone timeline
```

#### Slide 11: Closing
```
Content:
- Restate the opportunity
- Call to action
- Contact information
- Thank you

Visual: Brand imagery, contact details
```

---

### Step 4: Generate Output

**For each slide, provide:**

```json
{
  "slide_number": 1,
  "title": "Slide Title",
  "content": {
    "headline": "Main message",
    "bullets": ["Point 1", "Point 2", "Point 3"],
    "key_stat": "XX% growth" 
  },
  "talking_points": [
    "What to say when presenting this slide",
    "Key points to emphasize",
    "Anticipated questions"
  ],
  "visual_concept": {
    "type": "chart/screenshot/icon/photo",
    "description": "What the visual should show",
    "image_prompt": "Prompt for image generation if applicable"
  }
}
```

---

### Step 5: Offer Enhancements

**Delivery message:**

"✅ Pitch deck content complete!

**Deck:** [Company Name] - [Type] Pitch
**Slides:** 11 core + appendix recommendations

**Ready for:**
- Copy to Google Slides/PowerPoint
- Generate visuals for each slide
- Create appendix slides for Q&A

**Want me to:**
- Generate images for each slide? (uses image-generation)
- Create appendix slides? (detailed metrics, etc.)
- Adjust tone for different audience?
- Add more slides for specific sections?"

---

## Output Formats

### Option A: Markdown (Copy/Paste)
```markdown
# Slide 1: [Company Name]
**Tagline:** [One-liner]

---

# Slide 2: The Problem
[Problem statement]

---
...
```

### Option B: JSON (Structured)
Full structured output for programmatic use.

### Option C: With Generated Images
Use `image-generation` skill to create visuals for each slide.

---

## Integration with Other Agents

| Agent | Use Case |
|-------|----------|
| `brand-research-agent` | Align deck with brand guidelines |
| `market-researcher-agent` | Get market size data |
| `competitive-intel-agent` | Build competition slide |
| `image-generation` | Generate slide visuals |

---

## Best Practices Applied

1. **One message per slide** - No cluttered slides
2. **10-20-30 rule** - 10 slides, 20 minutes, 30pt font
3. **Story arc** - Problem → Solution → Opportunity → Ask
4. **Show, don't tell** - Data and demos over claims
5. **Anticipate questions** - Appendix for deep dives

---

## Example Prompts

**Full deck:**
> "Create a pitch deck for my AI startup that automates customer support"

**Specific stage:**
> "Create a seed round pitch deck for a B2B SaaS company"

**With context:**
> "I'm pitching to Sequoia next week. Here's my one-pager: [paste content]"

**Update existing:**
> "Update my Series A deck with new traction numbers: [new data]"
