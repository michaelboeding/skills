---
name: code-council
description: Research-aligned self-consistency for code. Spawns 10 independent solver agents with identical prompts, collects solutions, and uses majority voting to select the best answer. Based on "Self-Consistency Improves Chain of Thought Reasoning" (Wang et al., 2022). Use when the user asks for "code council", wants higher confidence, needs help debugging, or asks to "try multiple ways".
---

# Code Council: Self-Consistency for Code

Research-aligned implementation of self-consistency (Wang et al., 2022). Spawns multiple independent solvers with **identical prompts**, then uses **majority voting** to select the most likely correct answer.

## CRITICAL: Spawn Agents with IDENTICAL Prompts

You MUST spawn solver agents. All agents get the **exact same prompt**.

```
Task(agent: "council-solver-1", prompt: "[problem]")
Task(agent: "council-solver-2", prompt: "[problem]")
Task(agent: "council-solver-3", prompt: "[problem]")
... (continue for all agents)
```

**Default: 5 agents** | **Extended: 10 agents** (for critical problems)

## Research Basis

This implementation follows "Self-Consistency Improves Chain of Thought Reasoning in Language Models" (Wang et al., 2022):

| Principle | Implementation |
|-----------|----------------|
| Multiple independent samples | 5-10 solver agents |
| Identical prompts | Same problem statement to all |
| Same temperature | 0.7 for all agents |
| Chain-of-thought | Required before solution |
| Majority voting | Select answer with most agreement |

### Why This Works

If each agent has probability p of being correct, and agents are independent:
- P(majority wrong with 5 agents) << P(single agent wrong)
- As samples increase, probability of correct answer increases

**Key insight**: When multiple independent reasoners converge on the same answer, it's more likely correct than a single attempt.

## Workflow

### Step 1: Prepare the Problem

Create a clear, self-contained problem statement:

```markdown
## Problem

[Clear description of what needs to be solved]

## Context

[Relevant code - paste the actual code, not just file paths]

## Expected Behavior

[What should happen]

## Current Behavior (for bugs)

[What's actually happening / error messages]
```

**IMPORTANT**: All agents must receive the **exact same prompt**.

### Step 2: Spawn Agents

**Default (5 agents):**
```
Task(agent: "council-solver-1", prompt: "[problem]")
Task(agent: "council-solver-2", prompt: "[problem]")
Task(agent: "council-solver-3", prompt: "[problem]")
Task(agent: "council-solver-4", prompt: "[problem]")
Task(agent: "council-solver-5", prompt: "[problem]")
```

**Extended (10 agents)** - use for critical/complex problems:
```
Task(agent: "council-solver-1", prompt: "[problem]")
... through ...
Task(agent: "council-solver-10", prompt: "[problem]")
```

### Step 3: Collect Solutions

Wait for all agents to complete. Each returns:
- Analysis of the problem
- Chain-of-thought reasoning
- Proposed solution

### Step 4: Majority Voting

**Group solutions by their core approach/answer:**

1. Identify the **key decision** in each solution (e.g., "change `<=` to `<`")
2. Group solutions that make the same key decision
3. Count how many agents chose each approach

**Example:**
```
Approach A (change <= to <):     Agents 1, 2, 4, 5, 7, 9  → 6 votes
Approach B (add bounds check):   Agents 3, 6             → 2 votes  
Approach C (use forEach):        Agents 8, 10            → 2 votes

MAJORITY: Approach A (6/10 = 60%)
```

### Step 5: Select Answer

**If clear majority (≥50%):**
- Select the majority solution
- Confidence: HIGH

**If plurality but no majority (highest < 50%):**
- Select the plurality solution
- Confidence: MEDIUM
- Note the disagreement

**If no clear winner (tie or close):**
- Analyze why agents disagree
- May indicate ambiguous problem or multiple valid approaches
- Confidence: LOW
- Consider running more agents

### Step 6: Implement

Implement the winning solution. Do NOT synthesize or merge - use the majority answer as-is.

### Step 7: Report Results

Present results in this detailed format so the user understands the reasoning:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                     CODE COUNCIL RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📊 Voting Summary

| Approach | Description | Agents | Votes |
|----------|-------------|--------|-------|
| ✅ A | Change `<=` to `<` in loop | 1, 2, 4, 5, 7 | **5/8** |
| B | Add bounds check before loop | 3, 6 | 2/8 |
| C | Use forEach instead | 8 | 1/8 |

**Winner: Approach A** (62.5% consensus)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🧠 Agent Reasoning Highlights

### Why agents chose Approach A (majority):
- Agent 1: "The off-by-one error is clear - loop iterates past array bounds"
- Agent 2: "Standard fix for fence-post error in iteration"
- Agent 4: "Root cause is `<=` should be `<` to stay within bounds"

### Why some agents chose differently:
- Agent 3 (Approach B): "Adding explicit bounds check is more defensive"
- Agent 8 (Approach C): "forEach eliminates index management entirely"

### Key insight from minority:
Agent 3's bounds check idea could be valuable as additional safety.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ✅ Selected Solution (Majority Winner)

[Show the complete winning solution with code]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📈 Confidence Assessment

**Confidence: HIGH** ✅

Why:
- 5 of 8 agents (62.5%) independently chose the same approach
- Core reasoning aligned across majority
- Fix addresses the root cause directly

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🔧 Implementation

[Show the actual diff/change being made]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Key elements to include:**
1. Visual voting table with clear winner marked
2. Percentage consensus
3. Brief reasoning quotes from key agents
4. Why minority chose differently (may have insights)
5. Confidence level with justification
6. The actual implementation

## Configuration

| Mode | Agents | Use Case |
|------|--------|----------|
| `code council` | 5 | Default, most problems |
| `code council of 10` | 10 | Critical, complex, or ambiguous problems |
| `code council of 3` | 3 | Simple problems, faster |

## Why Majority Voting > Synthesis

| Approach | Pros | Cons |
|----------|------|------|
| **Majority voting** | Mathematical guarantee, no bias introduced | Might miss good ideas from minority |
| **Synthesis** | Can combine best ideas | Introduces orchestrator bias, no mathematical guarantee |

Research shows majority voting is more reliable. We use it.

## Agent Configuration

All 10 agents are **identical**:
- Same prompt (the problem)
- Same temperature (0.7)
- Same instructions (chain-of-thought, then solve)
- Same tools (Read, Grep, Glob, LS)

Diversity comes from **sampling randomness**, not from different prompts.

## Agents

Located in `agents/` directory:
- `council-solver-1` through `council-solver-10`

All identical - this is intentional per the research.
