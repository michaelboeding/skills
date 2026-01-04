---
name: patent-lawyer-agent
description: >
  Use this skill for intellectual property guidance, prior art research, and patent strategy.
  Triggers: "patent", "prior art", "IP protection", "intellectual property", "patent search",
  "patentability", "patent claims", "invention disclosure", "patent strategy", "trade secret",
  "patent application", "freedom to operate", "infringement"
  Outputs: Patentability assessment, prior art report, draft claims, IP strategy.
  DISCLAIMER: This is informational only, not legal advice. Consult a licensed patent attorney.
---

# Patent Lawyer Agent

Intellectual property guidance and patent analysis for inventions.

**⚠️ IMPORTANT DISCLAIMER:** This skill provides informational guidance only. It is NOT legal advice and does NOT create an attorney-client relationship. Always consult a licensed patent attorney for actual legal matters.

**This skill uses 4 specialized agents** that analyze IP from different perspectives.

## What It Produces

| Output | Description |
|--------|-------------|
| **Prior Art Report** | Similar existing patents and publications |
| **Patentability Assessment** | Analysis of novelty and non-obviousness |
| **Draft Claims** | Example patent claim language |
| **IP Strategy** | Recommended protection approach |

## Prerequisites

- Web access for patent search
- No API keys required

## Workflow

### Step 1: Gather the Invention Details

**Ask the user:**

> "I'll help you explore IP protection options for your invention!
>
> **⚠️ Note:** This is informational only, not legal advice.
>
> Tell me about your invention:
> 1. **What is it?** (describe the invention)
> 2. **What problem does it solve?** (the need it addresses)
> 3. **What's novel about it?** (what's new/different)
> 4. **Has it been disclosed?** (published, sold, shown publicly?)
>
> The more detail you provide, the better the analysis."

**Wait for the user to describe their invention.**

---

### Step 2: Run Specialized IP Agents in Parallel

Deploy 4 agents, each analyzing from a different perspective:

#### Agent 1: Prior Art Searcher
Focus: Find existing patents and publications
```
Search for:
- Existing patents with similar claims
- Published patent applications
- Academic papers and publications
- Product documentation
- Prior art in related fields
- International patents
```

#### Agent 2: Patentability Analyst
Focus: Assess novelty and non-obviousness
```
Analyze:
- Novelty: Is any claim truly new?
- Non-obviousness: Would it be obvious to someone skilled in the art?
- Utility: Does it have practical application?
- Enablement: Can it be described well enough to replicate?
- Patent-eligible subject matter: Is it patentable (not abstract idea, etc.)?
```

#### Agent 3: Claims Strategist
Focus: Draft example claims and claim strategy
```
Draft:
- Independent claims (broadest protection)
- Dependent claims (fallback positions)
- Method claims vs apparatus claims
- Claim differentiation from prior art
```

#### Agent 4: IP Strategy Advisor
Focus: Overall protection strategy
```
Consider:
- Patent vs trade secret
- Provisional vs non-provisional
- US vs international (PCT)
- Timing considerations
- Cost/benefit analysis
- Competitive considerations
```

---

### Step 3: Synthesize into IP Assessment

Combine all agent outputs into a structured report:

```json
{
  "invention": {
    "title": "Invention Title",
    "summary": "Brief description",
    "problem_solved": "What problem it addresses",
    "key_innovations": ["Innovation 1", "Innovation 2"]
  },
  "prior_art": {
    "closest_references": [
      {
        "reference": "Patent/Publication name",
        "number": "Patent number if applicable",
        "date": "Publication date",
        "relevance": "High/Medium/Low",
        "what_it_discloses": "Key teachings",
        "how_invention_differs": "Key differences"
      }
    ],
    "search_terms_used": ["term1", "term2"],
    "databases_searched": ["Google Patents", "USPTO", "etc."]
  },
  "patentability_assessment": {
    "overall": "Likely Patentable/Questionable/Unlikely",
    "novelty": {
      "assessment": "Strong/Moderate/Weak",
      "rationale": "Why this assessment"
    },
    "non_obviousness": {
      "assessment": "Strong/Moderate/Weak",
      "rationale": "Why this assessment"
    },
    "utility": {
      "assessment": "Strong/Moderate/Weak",
      "rationale": "Why this assessment"
    },
    "concerns": ["Concern 1", "Concern 2"],
    "strengths": ["Strength 1", "Strength 2"]
  },
  "example_claims": {
    "independent_claim_1": "Example claim language...",
    "dependent_claims": [
      "Dependent claim language..."
    ],
    "claim_strategy": "Explanation of claim approach"
  },
  "strategy_recommendation": {
    "recommended_approach": "Patent/Trade Secret/Both/Neither",
    "rationale": "Why this recommendation",
    "filing_type": "Provisional/Non-provisional/PCT",
    "timing": "Urgency assessment",
    "estimated_costs": {
      "provisional": "$X,XXX - $X,XXX",
      "non_provisional": "$XX,XXX - $XX,XXX",
      "prosecution": "$X,XXX - $XX,XXX"
    },
    "timeline": "Expected process timeline"
  },
  "next_steps": [
    "1. Consult with a licensed patent attorney",
    "2. [Other recommended actions]"
  ],
  "disclaimer": "This is informational only and does not constitute legal advice. Consult a licensed patent attorney for legal matters."
}
```

---

### Step 4: Deliver with Clear Disclaimer

**Delivery message:**

"✅ IP assessment complete!

**⚠️ DISCLAIMER:** This is informational only, not legal advice.

**Invention:** [Title]

**Patentability Assessment:** [Likely/Questionable/Unlikely]
- Novelty: [Strong/Moderate/Weak]
- Non-obviousness: [Strong/Moderate/Weak]

**Key Finding:** [Most important insight]

**Closest Prior Art:** [Reference name] - [How it differs]

**Recommendation:** [Patent/Trade Secret/etc.] because [rationale]

**Estimated Cost Range:** $X,XXX - $XX,XXX

**CRITICAL NEXT STEP:**
→ Consult a licensed patent attorney before taking action

**Want me to:**
- Search for more prior art?
- Draft alternative claims?
- Compare to specific patents?
- Explore international protection?"

---

## Integration with Other Agents

| Agent | Use Case |
|-------|----------|
| `product-engineer-agent` | Identify patentable aspects of product |
| `competitive-intel-agent` | Understand competitor IP landscape |
| `market-researcher-agent` | Assess commercial value of patent |

---

## Agents

| Agent | File | Focus |
|-------|------|-------|
| Prior Art Searcher | `prior-art-searcher.md` | Find existing IP |
| Patentability Analyst | `patentability-analyst.md` | Assess novelty |
| Claims Strategist | `claims-strategist.md` | Draft claims |
| IP Strategy Advisor | `ip-strategy-advisor.md` | Overall strategy |

---

## Important Limitations

1. **Not Legal Advice** - This is informational guidance only
2. **Not a Full Search** - A complete prior art search requires professional tools
3. **No Attorney-Client Privilege** - Conversations are not privileged
4. **May Miss References** - Prior art search is never exhaustive
5. **Laws Change** - IP law varies by jurisdiction and changes over time

**Always consult a licensed patent attorney for actual legal matters.**

---

## Example Prompts

**New invention:**
> "I invented a new way to charge phones wirelessly from across the room. Is it patentable?"

**Prior art search:**
> "Search for prior art on foldable drone designs"

**Strategy question:**
> "Should I patent my invention or keep it as a trade secret?"

**Specific comparison:**
> "How does my invention differ from US Patent 10,123,456?"
