---
name: product-engineer-agent
description: >
  Use this skill to design new products, iterate on product ideas, or develop product specifications.
  Triggers: "design product", "new product idea", "product concept", "product development",
  "product spec", "iterate on product", "product design", "invention", "prototype spec",
  "product requirements", "product engineering", "develop product"
  Outputs: Product specification, BOM estimate, feature breakdown, differentiation analysis.
---

# Product Engineer Agent

Design and develop new product concepts with comprehensive specifications.

**This skill uses 5 specialized agents** that analyze product ideas from different engineering perspectives, then synthesizes into a complete product specification.

## What It Produces

| Output | Description |
|--------|-------------|
| **Product Spec** | Complete product specification document |
| **Feature Matrix** | Prioritized feature list with rationale |
| **BOM Estimate** | Bill of materials with rough cost estimates |
| **Differentiation** | How it differs from existing products |
| **Next Steps** | Recommended path to prototype/production |

## Prerequisites

- No API keys required (analysis only)
- Works with any product category

## Workflow

### Step 1: Gather the Product Idea

**Ask the user:**

> "I'll help you design this product! Tell me about your idea:
>
> 1. **What problem does it solve?** (the core user need)
> 2. **Who is it for?** (target user)
> 3. **Any must-have features?** (key requirements)
> 4. **Any constraints?** (budget, size, materials, etc.)
>
> Share as much or as little as you have - I'll help fill in the gaps!"

**Wait for the user to describe their product idea.**

---

### Step 2: Run Specialized Engineering Agents in Parallel

Deploy 5 agents, each analyzing from a different perspective:

#### Agent 1: Industrial Designer
Focus: Form, ergonomics, aesthetics, user interaction
```
Consider:
- Physical form factor and dimensions
- Ergonomics and human factors
- Visual aesthetics and brand expression
- User interaction points (buttons, displays, etc.)
- Packaging and unboxing experience
```

#### Agent 2: Mechanical Engineer
Focus: How it works, materials, mechanisms
```
Consider:
- Core mechanism / how it functions
- Materials selection (strength, weight, cost)
- Manufacturing feasibility
- Durability and lifecycle
- Assembly and serviceability
```

#### Agent 3: User Researcher
Focus: User needs, pain points, usability
```
Consider:
- User journey with the product
- Pain points addressed
- Potential usability issues
- Onboarding and learning curve
- Accessibility considerations
```

#### Agent 4: Manufacturing Advisor
Focus: Feasibility, cost, production
```
Consider:
- Manufacturing methods (injection molding, CNC, etc.)
- Tooling requirements and costs
- Unit cost estimates at various volumes
- Supply chain considerations
- Quality control points
```

#### Agent 5: Innovation Scout
Focus: Existing solutions, patents, differentiation
```
Consider:
- Similar products in market
- Patent landscape (potential conflicts)
- Unique differentiators
- Technology trends to leverage
- Blue ocean opportunities
```

---

### Step 3: Synthesize into Product Specification

Combine all agent outputs into a structured specification:

```json
{
  "product": {
    "name": "Product Name",
    "tagline": "One-line description",
    "problem_solved": "Core problem it addresses",
    "target_user": "Who it's for",
    "category": "Product category"
  },
  "design": {
    "form_factor": "Physical description",
    "dimensions": "L x W x H",
    "weight": "Estimated weight",
    "materials": ["Material 1", "Material 2"],
    "colors": ["Primary options"],
    "key_interactions": ["How users interact with it"]
  },
  "features": {
    "must_have": [
      {"feature": "Feature 1", "rationale": "Why it's essential"}
    ],
    "should_have": [
      {"feature": "Feature 2", "rationale": "High value add"}
    ],
    "could_have": [
      {"feature": "Feature 3", "rationale": "Nice to have"}
    ]
  },
  "technical": {
    "mechanism": "How it works",
    "power_source": "Battery/plug/manual/etc.",
    "electronics": "Any electronic components",
    "software": "Any software/firmware needed"
  },
  "manufacturing": {
    "primary_method": "Main manufacturing process",
    "estimated_bom": [
      {"component": "Part 1", "estimated_cost": "$X"}
    ],
    "unit_cost_estimates": {
      "100_units": "$XX",
      "1000_units": "$XX",
      "10000_units": "$XX"
    },
    "complexity": "Low/Medium/High"
  },
  "market": {
    "similar_products": ["Competitor 1", "Competitor 2"],
    "differentiators": ["What makes this unique"],
    "price_positioning": "Budget/Mid/Premium",
    "target_msrp": "$XX"
  },
  "next_steps": [
    "1. Validate with potential users",
    "2. Create detailed CAD model",
    "3. Build first prototype",
    "4. Patent search (if applicable)"
  ]
}
```

---

### Step 4: Deliver and Iterate

**Delivery message:**

"✅ Product specification complete!

**Product:** [Name]
**Problem:** [What it solves]
**Key Differentiator:** [What makes it unique]

**Estimated unit cost:** $XX at 1,000 units
**Suggested MSRP:** $XX

**Next steps:**
1. [First recommended action]
2. [Second recommended action]

**Want me to:**
- Deep dive on any section?
- Explore alternative approaches?
- Estimate costs for different volumes?
- Compare to specific competitors?"

---

## Integration with Other Agents

This skill works well with:

| Agent | Use Case |
|-------|----------|
| `brand-research-agent` | Ensure product fits brand guidelines |
| `patent-lawyer-agent` | Check patentability of innovations |
| `market-researcher-agent` | Validate market opportunity |
| `pitch-deck-agent` | Create investor presentation |

---

## Agents

| Agent | File | Focus |
|-------|------|-------|
| Industrial Designer | `industrial-designer.md` | Form, aesthetics, UX |
| Mechanical Engineer | `mechanical-engineer.md` | Function, materials |
| User Researcher | `user-researcher.md` | Needs, usability |
| Manufacturing Advisor | `manufacturing-advisor.md` | Cost, feasibility |
| Innovation Scout | `innovation-scout.md` | Competition, patents |

---

## Example Prompts

**Basic:**
> "Design a new portable phone charger that's more convenient"

**With context:**
> "I want to create a kitchen gadget that helps with meal prep. Target audience is busy parents. Budget under $30 retail."

**Iteration:**
> "Take my existing product idea and suggest improvements: [description]"

**Competitive:**
> "Design something better than [competitor product]"
