---
name: competitive-intel-agent
description: >
  Use this skill to analyze competitors, find competitive gaps, and develop competitive strategy.
  Triggers: "competitor analysis", "competitive analysis", "analyze competitor", "competitive intel",
  "competitive intelligence", "competitive landscape", "competitor comparison", "beat competitor",
  "competitor weakness", "competitive advantage", "competitor research"
  Outputs: Competitive matrix, gap analysis, differentiation strategy, battlecards.
---

# Competitive Intel Agent

Analyze competitors and develop strategies to win against them.

**This skill uses 4 specialized agents** that analyze competitors from different angles, then synthesizes into actionable intelligence.

## What It Produces

| Output | Description |
|--------|-------------|
| **Competitive Matrix** | Feature-by-feature comparison |
| **SWOT Analysis** | Strengths, weaknesses, opportunities, threats |
| **Gap Analysis** | Where you can differentiate |
| **Battlecard** | Quick reference for sales/marketing |
| **Strategy Recommendations** | How to position against each competitor |

## Prerequisites

- Web access for research
- No API keys required

## Workflow

### Step 1: Identify Competitors to Analyze

**Ask the user:**

> "I'll analyze your competitive landscape!
>
> Tell me:
> 1. **What's your product/service?** (what you offer)
> 2. **Who are your main competitors?** (company names/URLs)
> 3. **What aspects to compare?** (features, pricing, market position)
> 4. **What's your goal?** (differentiate, enter market, win deals)
>
> If you don't know competitors, I can help identify them."

**Wait for the user to provide competitor list.**

---

### Step 2: Run Specialized Analysis Agents in Parallel

Deploy 4 agents, each analyzing from a different perspective:

#### Agent 1: Feature Analyst
Focus: Product features and capabilities
```
Compare:
- Core features and functionality
- Feature depth vs breadth
- Unique capabilities
- Missing features
- Roadmap/recent launches
- Integrations and ecosystem
```

#### Agent 2: Pricing Analyst
Focus: Pricing and value proposition
```
Compare:
- Pricing models (subscription, usage, one-time)
- Price points and tiers
- Feature packaging
- Free tier/trial offerings
- Enterprise pricing
- Total cost of ownership
```

#### Agent 3: Positioning Analyst
Focus: Brand positioning and messaging
```
Compare:
- Target audience claims
- Key messaging themes
- Brand personality
- Thought leadership
- Customer testimonials
- Marketing channels
```

#### Agent 4: Market Position Analyst
Focus: Market share and business health
```
Compare:
- Estimated market share
- Company size/funding
- Growth trajectory
- Customer base
- Partnerships
- Public perception
```

---

### Step 3: Synthesize into Competitive Intelligence

Combine all agent outputs into structured intelligence:

```json
{
  "analysis_scope": {
    "your_product": "Your product/service",
    "competitors_analyzed": ["Competitor 1", "Competitor 2", "Competitor 3"],
    "analysis_date": "2026-01-04"
  },
  "competitive_matrix": {
    "features": {
      "Feature Category 1": {
        "your_product": "✅ Full",
        "competitor_1": "✅ Full",
        "competitor_2": "⚠️ Partial",
        "competitor_3": "❌ None"
      }
    },
    "pricing": {
      "your_product": "$XX/mo",
      "competitor_1": "$XX/mo",
      "competitor_2": "$XX/mo"
    }
  },
  "competitor_profiles": [
    {
      "name": "Competitor 1",
      "website": "https://competitor1.com",
      "positioning": "How they position themselves",
      "target_audience": "Who they target",
      "strengths": ["Strength 1", "Strength 2"],
      "weaknesses": ["Weakness 1", "Weakness 2"],
      "pricing": "$XX/mo for Pro tier",
      "differentiator": "What makes them unique",
      "threat_level": "High/Medium/Low"
    }
  ],
  "swot": {
    "strengths": ["Your strength vs competitors"],
    "weaknesses": ["Your weakness vs competitors"],
    "opportunities": ["Gaps to exploit"],
    "threats": ["Competitive threats to address"]
  },
  "gap_analysis": {
    "underserved_segments": ["Segment competitors ignore"],
    "missing_features": ["Features no one offers"],
    "pricing_gaps": ["Price point opportunities"],
    "positioning_gaps": ["Messaging white space"]
  },
  "battlecard": {
    "competitor_1": {
      "when_we_win": ["Scenario 1", "Scenario 2"],
      "when_they_win": ["Scenario 1", "Scenario 2"],
      "key_differentiators": ["What to emphasize"],
      "objection_handling": {
        "They're cheaper": "Response...",
        "They have feature X": "Response..."
      },
      "landmines": ["Questions to ask that expose their weakness"]
    }
  },
  "recommendations": {
    "positioning": "How to position against the field",
    "messaging": "Key messages to emphasize",
    "features_to_build": ["Feature gaps to close"],
    "segments_to_target": ["Where you can win"],
    "pricing_strategy": "How to price competitively"
  }
}
```

---

### Step 4: Deliver Actionable Intelligence

**Delivery message:**

"✅ Competitive analysis complete!

**You vs [# competitors analyzed]**

**Your Biggest Advantage:** [Key differentiator]

**Biggest Threat:** [Competitor] because [reason]

**Best Opportunity:** [Gap or segment to exploit]

**Quick Battlecard:**
- Against [Competitor 1]: Lead with [differentiator]
- Against [Competitor 2]: Emphasize [strength]

**Want me to:**
- Deep dive on any competitor?
- Create detailed battlecards for sales?
- Analyze additional competitors?
- Research specific features?
- Monitor for changes?"

---

## Output Formats

### Competitive Matrix (Visual)
```
Feature          | You  | Comp A | Comp B | Comp C
-----------------|------|--------|--------|-------
Feature 1        | ✅   | ✅     | ⚠️     | ❌
Feature 2        | ✅   | ❌     | ✅     | ✅
Feature 3        | ✅   | ✅     | ✅     | ❌
Pricing (Pro)    | $29  | $49    | $39    | $19
Free Tier        | ✅   | ❌     | ✅     | ✅
```

### Sales Battlecard (Quick Reference)
```
## vs [Competitor Name]

WHEN WE WIN:
- Customer values X
- They need Y integration
- Budget is limited

WHEN THEY WIN:
- They're already using their ecosystem
- Need feature Z (we don't have)

OUR LANDMINES:
- "How do they handle [problem we solve better]?"
- "What's their uptime SLA?"

OBJECTION HANDLING:
- "They're the market leader" → "Size doesn't mean best fit..."
- "They have more features" → "More features = more complexity..."
```

---

## Integration with Other Agents

| Agent | Use Case |
|-------|----------|
| `brand-research-agent` | Deep dive on competitor's brand |
| `market-researcher-agent` | Market size and dynamics |
| `product-engineer-agent` | Design features to differentiate |
| `copywriter-agent` | Write competitive messaging |

---

## Agents

| Agent | File | Focus |
|-------|------|-------|
| Feature Analyst | `feature-analyst.md` | Product features |
| Pricing Analyst | `pricing-analyst.md` | Pricing models |
| Positioning Analyst | `positioning-analyst.md` | Brand/messaging |
| Market Position Analyst | `market-position-analyst.md` | Market share |

---

## Example Prompts

**Full analysis:**
> "Analyze our CRM competitors: Salesforce, HubSpot, and Pipedrive"

**Specific competitor:**
> "Deep dive on Notion - find their weaknesses"

**Find competitors:**
> "Who are the main competitors to our AI writing tool?"

**Battlecard:**
> "Create a sales battlecard for when we compete against Slack"

**Gap analysis:**
> "What features do our competitors have that we're missing?"
