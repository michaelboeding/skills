---
name: feature-council
description: Multi-agent feature implementation. Spawns independent solver agents that each implement the feature from scratch, then synthesizes the best elements from each. Use when building complex features where you want diverse approaches and comprehensive edge case coverage.
---

# Feature Council: Multi-Agent Feature Implementation

Two-phase approach:
1. **Scout phase** - Explore codebase, gather context
2. **Implementation phase** - Multiple agents implement with shared context

**Use this for complex features where you want diverse implementations and comprehensive coverage.**

## Step 0: Ask User How Many Agents

Before doing anything else, **ask the user how many solver agents to use**:

```
How many solver agents would you like me to use? (3-10)

Recommendations:
- 3 agents: Faster, good for straightforward features
- 5 agents: Good balance of diversity and speed
- 7 agents: Comprehensive coverage
- 10 agents: Maximum diversity (complex features)

Note: A scout agent will first explore the codebase, then all
solver agents receive that context to focus on implementation.
```

Wait for the user's response. If they specified a number (e.g., "feature council of 5"), use that.

**Minimum: 3 agents** | **Maximum: 10 agents**

---

## Phase 1: Scout

### Step 1: Capture the Raw User Prompt

Take the user's request **exactly as stated**.

### Step 2: Deploy Scout Agent

Spawn the scout to explore the codebase:

```
Task(agent: "feature-scout", prompt: "[USER'S EXACT WORDS]")
```

The scout will:
- Explore project structure
- Find relevant files
- Identify codebase patterns
- Locate integration points
- Return a comprehensive context summary

### Step 3: Collect Scout Report

Wait for the scout to complete. The scout returns a structured report with:
- Relevant files (to modify, reference, create)
- Codebase patterns (naming, error handling, architecture)
- Integration points
- Key dependencies
- Example code snippets
- Edge cases discovered

---

## Phase 2: Implementation

### Step 4: Spawn Implementers with Context

Spawn ALL implementer agents simultaneously with the scout's context:

```
Task(agent: "feature-solver-1", prompt: "
FEATURE REQUEST:
[USER'S EXACT WORDS]

SCOUT CONTEXT:
[SCOUT'S FULL REPORT]
")

Task(agent: "feature-solver-2", prompt: "
FEATURE REQUEST:
[USER'S EXACT WORDS]

SCOUT CONTEXT:
[SCOUT'S FULL REPORT]
")

... (all in the SAME batch - parallel execution)
```

Each implementer receives:
- The original user request
- The scout's context report
- Full tool access (can still explore further if needed)

### Step 5: Track Progress

As agents complete, **show progress to the user**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                     AGENT PROGRESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☑ Scout    - Complete (context gathered)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☑ Solver 1 - Complete
☑ Solver 2 - Complete  
☑ Solver 3 - Complete
☐ Solver 4 - Working...
☐ Solver 5 - Working...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 6: Collect Implementations

Wait for all agents to complete. Collect their outputs.

---

## Phase 3: Synthesis

### Step 7: Analyze & Compare Implementations

Analyze each implementation for:

| Category | What to Look For |
|----------|------------------|
| **Architecture** | Design patterns, code organization, modularity |
| **Edge Cases** | What edge cases did each agent handle? |
| **Error Handling** | How robust is the error handling? |
| **Type Safety** | Type definitions, null checks, validation |
| **Performance** | Efficiency, caching, optimization |
| **Maintainability** | Readability, documentation, testability |
| **Codebase Fit** | How well does it match existing patterns? |

Create a comparison matrix:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                  IMPLEMENTATION COMPARISON
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Aspect          | Solver 1 | Solver 2 | Solver 3 | Solver 4 | Solver 5 |
|-----------------|----------|----------|----------|----------|----------|
| Architecture    | MVC      | Service  | MVC      | MVC      | Modular  |
| Edge Cases      | 3        | 5        | 4        | 3        | 6        |
| Error Handling  | Basic    | Robust   | Good     | Basic    | Robust   |
| Type Safety     | ✓        | ✓✓       | ✓        | ✓        | ✓✓       |
| Codebase Match  | 90%      | 75%      | 95%      | 85%      | 80%      |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 8: Synthesize Best Solution

**Combine the best elements from each agent:**

1. **Select base implementation** - Choose the one that best matches codebase patterns
2. **Incorporate edge cases** - Add edge cases from other agents the base missed
3. **Enhance error handling** - Use the most robust error handling approach
4. **Improve type safety** - Merge type definitions and validations
5. **Document sources** - Track which elements came from which agent

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                     SYNTHESIS PLAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Base: Solver 3 (best codebase pattern match)

Incorporating from other agents:
├─ Solver 2: Robust error handling pattern
├─ Solver 5: Edge cases for [empty input, concurrent access]
├─ Solver 2: Type definitions for [UserInput, ValidationResult]
└─ Solver 4: Caching optimization

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 9: Implement Synthesized Solution

Implement the final synthesized solution that combines the best elements.

### Step 10: Report Results

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    FEATURE COUNCIL RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🔭 Scout Findings

- Files explored: [count]
- Patterns identified: [list]
- Key integration points: [list]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📊 Implementation Comparison

| Solver | Architecture | Edge Cases | Error Handling | Codebase Fit |
|--------|--------------|------------|----------------|--------------|
| 1      | [approach]   | [count]    | [quality]      | [%]          |
| 2      | [approach]   | [count]    | [quality]      | [%]          |
| ...    | ...          | ...        | ...            | ...          |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🔍 What Each Agent Contributed

### Solver 1
- Approach: [brief description]
- Unique strength: [what this agent did best]

### Solver 2
- Approach: [brief description]
- Unique strength: [what this agent did best]

... (for each solver)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🧬 Synthesis Breakdown

| Element | Source | Reason |
|---------|--------|--------|
| Base architecture | Solver 3 | Best codebase pattern match (95%) |
| Error handling | Solver 2 | Most comprehensive try/catch + logging |
| Edge case: empty input | Solver 5 | Only agent that handled this |
| Edge case: concurrent | Solver 5 | Race condition prevention |
| Type definitions | Solver 2 | Strictest typing |
| Caching layer | Solver 4 | Performance optimization |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📈 Final Solution Quality

- **Edge Cases Covered**: [total unique from all agents]
- **Error Handling**: [description]
- **Codebase Fit**: [% and explanation]
- **Type Safety**: [description]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ✅ Implemented Solution

[The synthesized implementation]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📁 Files Created/Modified

[List of all files with brief descriptions]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Configuration

| Mode | Agents | Use Case |
|------|--------|----------|
| `feature council of 3` | 1 scout + 3 solvers | Simple features |
| `feature council of 5` | 1 scout + 5 solvers | Good balance |
| `feature council of 7` | 1 scout + 7 solvers | Complex features |
| `feature council of 10` | 1 scout + 10 solvers | Maximum coverage |

If user just says `feature council`, ask them to choose.

---

## Why Scout + Implementers?

| Without Scout | With Scout |
|---------------|------------|
| Each agent explores (duplicated work) | Scout explores once |
| ~40K tokens per agent (exploration + impl) | ~25K tokens per agent (impl focused) |
| Frequent token limit hits | Rare token limit hits |
| Slower overall | Faster overall |
| Agents may miss files | Scout finds files, agents can find more |

**Solvers still have full tool access** - they can explore further if needed. The scout context is a head start, not a limitation.

---

## Difference from Debug Council

| Aspect | Debug Council | Feature Council |
|--------|---------------|-----------------|
| **Scout phase** | No (pure independence) | Yes (shared context) |
| **Why** | Different agents may find different bugs | Exploration is shared work |
| **Selection** | Majority voting | Synthesis/merge |
| **Output** | Single winning fix | Best-of-all combined |

---

## Agents

| Agent | Purpose |
|-------|---------|
| `feature-scout` | Explores codebase, gathers context |
| `feature-solver-1` through `feature-solver-10` | Implement with context |

All agents:
- Same temperature (0.7)
- Same tools (Read, Grep, Glob, LS)
- Use ultrathink (extended thinking)

---

## When to Use

✅ **Use feature-council for:**
- Complex features with many edge cases
- Features where you're unsure of best approach
- High-stakes production code
- When you want comprehensive coverage

❌ **Don't use for:**
- Simple CRUD operations
- Bug fixes (use debug-council instead)
- When speed matters more than coverage
