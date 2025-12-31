---
name: code-council
description: Ensemble problem-solving using independent subagents. Spawns 3 isolated solver agents that generate truly independent solutions, then synthesizes the best answer. Use when the user asks for "code council", wants multiple coding approaches compared, requests higher-quality/verified code, needs help debugging, or asks to "try multiple ways" on coding problems, algorithms, bug fixes, or technical implementations.
---

# Code Council: Multi-Agent Ensemble Problem Solving

## CRITICAL: You MUST Spawn Subagents

**DO NOT solve this yourself in a single context.** You MUST spawn the 3 solver agents to get truly independent solutions.

After understanding the problem, use Task to spawn each agent:

```
Task(agent: "council-solver-a", prompt: "[problem statement]")
Task(agent: "council-solver-b", prompt: "[problem statement]")  
Task(agent: "council-solver-c", prompt: "[problem statement]")
```

Wait for all 3 agents to complete, then synthesize their solutions.

---

Spawn 3 independent solver subagents, each generating a solution in isolation, then synthesize the best answer using consensus analysis.

## Architecture

```
User Request: "code council: fix this bug"
                    │
                    ▼
    ┌───────────────────────────────┐
    │   Code Council Orchestrator   │
    │      (Claude Code Main)       │
    │                               │
    │  1. Parse problem             │
    │  2. Prepare context           │
    │  3. Spawn subagents           │
    └───────────────────────────────┘
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Solver A   │ │  Solver B   │ │  Solver C   │
│ Straight-   │ │ Alternative │ │ Optimized   │
│ forward     │ │ Creative    │ │ Production  │
│             │ │             │ │             │
│ (isolated)  │ │ (isolated)  │ │ (isolated)  │
└─────────────┘ └─────────────┘ └─────────────┘
       │            │            │
       └────────────┼────────────┘
                    ▼
    ┌───────────────────────────────┐
    │         Synthesis             │
    │    (Claude Code Main)         │
    │                               │
    │  1. Compare all solutions     │
    │  2. Check consensus           │
    │  3. Merge best elements       │
    │  4. Implement final solution  │
    └───────────────────────────────┘
```

## Why Subagents?

**The research problem**: Self-consistency requires *truly independent* reasoning paths. When one model generates all solutions sequentially, later solutions are influenced by earlier ones.

**The solution**: Spawn separate subagent instances with isolated contexts:
- Each agent sees ONLY the problem (not other solutions)
- Different temperature settings encourage diversity
- True independence = true ensemble diversity
- Matches the original self-consistency research methodology

## Subagent Definitions

Three solver agents are defined in the `agents/` directory:

| Agent | Role | Style | Temperature |
|-------|------|-------|-------------|
| `council-solver-a` | Straightforward | Conventional, direct, established patterns | 0.7 |
| `council-solver-b` | Alternative | Creative, unconventional, different paradigms | 0.9 |
| `council-solver-c` | Optimized | Performance-focused, production-ready, robust | 0.7 |

Each agent:
- Has READ-ONLY access to the codebase (can explore, not modify)
- Returns analysis + proposed solution (does NOT implement)
- Works in complete isolation from other agents

## Workflow

### Step 1: Orchestrator Receives Request

Claude Code (main session) receives the code council request.

**Detect mode:**
- **Bug Fix Mode**: User provides broken code + error/unexpected behavior
- **New Code Mode**: User requests new functionality

### Step 2: Prepare the Problem Statement

Create a clear, self-contained problem statement for the agents:

```markdown
## Problem Statement

[Clear description of what needs to be solved]

## Context

[Relevant code snippets, file paths, error messages]

## Requirements

[What the solution must do]

## Constraints

[Any constraints: performance, compatibility, style]

---

Generate your solution following your designated approach style.
Provide analysis and proposed code, but DO NOT implement changes.
```

### Step 3: Spawn Subagents in Parallel

Invoke all three solver agents simultaneously:

```
@council-solver-a [problem statement]
@council-solver-b [problem statement]  
@council-solver-c [problem statement]
```

Each agent works in isolation and returns:
- Analysis of the problem
- Reasoning/chain-of-thought
- Proposed solution (code)
- Edge cases considered
- Trade-offs identified
- Confidence level

### Step 4: Collect Solutions

Wait for all three agents to complete. Collect their outputs.

### Step 5: Analyze Consensus (Orchestrator)

Claude Code analyzes the three solutions:

**High Consensus** (2+ agents agree on core approach):
- Strong signal of correctness
- Merge best elements from agreeing solutions
- Note any unique insights from the dissenting solution

**Partial Consensus** (agents agree on some aspects):
- Identify what they agree on (likely correct)
- Investigate disagreements (may reveal edge cases)

**No Consensus** (all different):
- Indicates complex problem with multiple valid approaches
- Evaluate each on merits
- Consider spawning additional agents if critical

### Step 6: Synthesize Best Solution

Using ultrathink (maximum extended thinking), synthesize:

1. **Evaluate correctness** of each proposed solution
2. **Identify strongest elements** from each approach
3. **Merge complementary ideas** (e.g., A's algorithm + C's error handling)
4. **Resolve conflicts** where approaches disagree
5. **Create final solution** that represents the best of all approaches

### Step 7: Test the Synthesized Solution

Actually execute the solution in the environment:
- Run against test cases
- Verify edge cases
- Confirm the original problem is solved

### Step 8: Implement

Only Claude Code (orchestrator) makes actual code changes:
- Apply the synthesized solution
- No conflicting changes from multiple agents
- Single source of truth

### Step 9: Deliver Results

Provide:

1. **Final implemented solution** (the actual code change)
2. **Consensus report**:
   - What did agents agree on?
   - What unique insights did each provide?
3. **For bug fixes**: Diff showing what changed + why it was broken
4. **Test results** confirming it works
5. **Confidence level**:
   - High: Strong consensus (2+ agreed)
   - Medium: Partial consensus or close decision
   - Low: No consensus (investigate further)
6. **Trade-offs** to be aware of

## Example Output

```
## Code Council Results

### Consensus: HIGH (2/3 agents agreed on core approach)

### Solution Summary
All agents identified the off-by-one error in the loop condition.
Solver A and C both recommended `i < len` (consensus).
Solver B suggested using `forEach` to avoid index entirely (alternative insight).

### Synthesized Solution
Implementing Solver A's fix with Solver C's added null check:

[code diff here]

### Agent Contributions
- **Solver A**: Identified the bug, proposed clean fix
- **Solver B**: Suggested iterator approach (valid alternative for future)
- **Solver C**: Added defensive null check, noted edge case with empty array

### Tests: 5/5 passing
### Confidence: HIGH
```

## Configuration

**Default**: 3 agents (A, B, C)

**Variations:**
- `code council of 2`: Simpler problems (Solver A + C only)
- `code council of 5`: Critical code (add Solver D: Security, Solver E: Edge Cases)
- `quick code council`: Skip subagents, use single-context multi-approach (faster but less independent)

## Why This Works

Research shows:
- **Independent samples** that converge = higher accuracy than single attempt
- **Diverse reasoning paths** catch different edge cases
- **Consensus** is a strong correctness signal
- **Meta-evaluation** (synthesizing best answer) matches human expert judgment

The subagent architecture ensures TRUE independence - each solver has no knowledge of what others are doing, eliminating cross-contamination of ideas.
