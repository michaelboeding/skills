---
name: code-council
description: Ensemble problem-solving approach using ultrathink (maximum extended thinking) to generate multiple independent code solutions, execute tests, compare results, and deliver the best implementation. Use when the user asks for "code council", wants multiple coding approaches compared, requests higher-quality/verified code, needs help debugging, or asks to "try multiple ways" on coding problems, algorithms, bug fixes, or technical implementations.
---

# Code Council: Multi-Approach Code Problem Solving

Generate multiple independent code solutions, execute tests, compare results, and deliver the best implementation.

Based on self-consistency research: multiple diverse reasoning paths that converge on the same answer are more likely correct than a single attempt.

## Thinking Mode

**IMPORTANT**: When this skill is triggered, use maximum extended thinking (ultrathink) to ensure deep reasoning for each approach. This allocates the highest computational budget for thorough analysis.

The multi-approach methodology requires significant reasoning depth to:
- Generate truly independent solutions (not superficial variations)
- Analyze trade-offs comprehensively
- Synthesize insights across approaches

## Mode Detection

**Bug Fix Mode** (user provides broken code + error/unexpected behavior):
- Analyze the error context (stack trace, error message, unexpected output)
- Identify root cause before generating fixes
- Show diffs of what changed
- Explain *why* it was broken

**New Code Mode** (user requests new functionality):
- Generate fresh implementations
- Focus on different algorithms/patterns

## Workflow

### Step 1: Understand the Problem

For bug fixes:
- Parse the error message / stack trace
- Identify the failing input or condition
- State the root cause hypothesis

For new code:
- Clarify requirements and edge cases

**If working in an existing codebase:**
- Note the existing code style, patterns, and conventions
- Identify the architectural patterns in use (MVC, functional, OOP, etc.)
- Solutions should match the codebase's design and flow

### Step 2: Generate Independent Solutions with Chain-of-Thought

Create 3 separate implementations. For each approach:

1. **Reason first**: Explain the approach and why it should work before writing code
2. **Implement**: Write the code
3. **Keep independent**: Use different variable names, structures, and logic patterns

Approaches:
- **Approach A (Straightforward)**: Direct, conventional implementation
- **Approach B (Alternative)**: Different algorithm or pattern
- **Approach C (Optimized)**: Focus on performance or elegance

The goal is diverse reasoning paths - not just syntactic variation.

### Step 3: Execute Tests

Actually run each solution in the computer environment. Test:
- Basic functionality (happy path)
- Edge cases (empty input, single element, large input, boundary values)
- Error conditions (invalid input, null/None, wrong types)
- The specific failing case (for bug fixes)

Record actual pass/fail results from execution.

### Step 4: Analyze Each Solution

Evaluate:
- **Correctness**: Actual test results from execution
- **Efficiency**: Time/space complexity
- **Readability**: Clear naming, logical structure, easy to understand?
- **Maintainability**: Easy to modify, extend, debug later?
- **Codebase Fit**: Matches existing patterns, style, and conventions?
- **Robustness**: Error handling, input validation
- **Security**: Vulnerabilities? (injection, XSS, path traversal, etc.)

### Step 5: Check for Consensus

**Key insight from research**: If multiple independent approaches produce the same output or use the same core logic, that's a strong signal of correctness.

- Do 2+ approaches agree on the answer/logic? → High confidence
- Do all approaches disagree? → Investigate why, may need more approaches
- Does one approach find an edge case others missed? → Incorporate that insight

### Step 6: Compare

| Criteria | Approach A | Approach B | Approach C |
|----------|-----------|-----------|-----------|
| Tests Passing | ?/? | ?/? | ?/? |
| Time Complexity | O(?) | O(?) | O(?) |
| Space Complexity | O(?) | O(?) | O(?) |
| Readability | Low/Med/High | Low/Med/High | Low/Med/High |
| Maintainability | Low/Med/High | Low/Med/High | Low/Med/High |
| Codebase Fit | Low/Med/High/N/A | Low/Med/High/N/A | Low/Med/High/N/A |

### Step 7: Meta-Evaluation

After comparing, explicitly reason about which solution is best:

"Evaluating these approaches: [reason about the trade-offs]. The most consistent and correct solution is [X] because [rationale]."

This meta-evaluation step catches issues the comparison table might miss.

### Step 8: Synthesize Best Solution

- **Select**: Choose best if one is clearly superior
- **Merge**: Combine best elements from multiple approaches (e.g., A's algorithm + C's error handling)
- **Refine**: Improve the winner based on insights from others

### Step 9: Deliver

Provide:
1. Final recommended code
2. For bug fixes: diff showing what changed + explanation of why it was broken
3. Test results confirming it works
4. Confidence level (High if consensus, Medium if close call, Low if uncertain)
5. Why this approach won (1-2 sentences)
6. Any trade-offs to be aware of

## Configuration

**Default Settings:**
- 3 approaches
- Ultrathink enabled (maximum extended thinking)

**Variations:**
- "code council of 2" - simpler problems (still uses ultrathink)
- "code council of 5" - critical/complex code needing extra confidence
- "quick code council" - faster mode, reduced thinking budget (not recommended for complex problems)

## Why This Works

Research shows:
- Multiple reasoning paths that converge = higher accuracy
- Consensus among diverse approaches is a strong correctness signal
- Meta-evaluation (LLM choosing best answer) matches execution-based verification
- Chain-of-thought before code catches logical errors early
