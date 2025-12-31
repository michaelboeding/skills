---
name: model-council
description: This skill should be used when the user asks for "model council", "multi-model", "compare models", "ask multiple AIs", "consensus across models", "run on different models", or wants to get solutions from multiple AI providers (Claude, GPT, Gemini, Grok) and compare results. Orchestrates parallel execution across AI models and synthesizes the best answer.
---

# Model Council: Multi-Model Consensus

Run the same problem through multiple AI models in parallel, then compare and synthesize the best solution.

Unlike code-council (which uses one model with multiple approaches), model-council leverages **different model architectures** for true ensemble diversity.

## CRITICAL: Analysis Only - No Code Changes

**External models must NOT modify any code or files.** They provide analysis only.

When prompting external models, always include this instruction:
> "Analyze this problem and provide your recommendation. Do NOT modify any files. 
> Provide your analysis, suggested approach, and reasoning only. 
> Another system will make the final decision on implementation."

**Why?**
- Claude Code maintains full control and context
- External models lack access to the codebase
- Claude Code synthesizes all inputs and makes the final decision
- Prevents conflicting changes from multiple sources

## Why Multi-Model?

Different models have different:
- Training data and knowledge cutoffs
- Reasoning patterns and biases
- Strengths (math, code, creativity, etc.)

When multiple independent models agree → High confidence the answer is correct.

## Execution Modes

### Mode 1: CLI Agents (Uses Your Existing Logins)

Call CLI tools that use your logged-in accounts.

| CLI Tool | Model | Install Command | Notes |
|----------|-------|-----------------|-------|
| `claude` | Claude | Already running | This session |
| `codex` | OpenAI | `npm install -g @openai/codex` | Requires OpenAI login |
| `gemini` | Google | See [Gemini CLI docs](https://github.com/google-gemini/gemini-cli) | Requires Google login |
| `aider` | Any | `pip install aider-chat` | Configure with any provider |

**CLI Setup Instructions:**

```bash
# OpenAI Codex CLI
npm install -g @openai/codex
codex auth   # Login with your OpenAI account

# Google Gemini CLI  
npm install -g @anthropic-ai/gemini-cli
gemini auth  # Login with your Google account

# Aider (works with multiple providers)
pip install aider-chat
# Configure in ~/.aider.conf.yml or pass --model flag
```

### Mode 2: API Calls (Pay per token)

Direct API calls - more reliable but costs money.

Required environment variables:
- `ANTHROPIC_API_KEY` - For Claude API (https://console.anthropic.com/)
- `OPENAI_API_KEY` - For GPT-4 API (https://platform.openai.com/api-keys)
- `GOOGLE_API_KEY` - For Gemini API (https://aistudio.google.com/apikey)
- `XAI_API_KEY` - For Grok API (https://console.x.ai/)

## Configuration

### User Model Selection

Users can specify models inline:

```
model council with claude, gpt-4o, gemini: solve this problem

model council (claude + codex): fix this bug

model council all: use all available models
```

### Default Models

If not specified, use all available:
1. Check which CLI tools are installed
2. Check which API keys are set
3. Use what's available

### Config File (Optional)

Users can create `~/.model-council.yaml`:

```yaml
# Preferred models (in order)
models:
  - claude      # Use Claude Code CLI (current session)
  - codex       # Use Codex CLI if installed
  - gemini-cli  # Use Gemini CLI if installed
  
# Fallback to APIs if CLIs not available
fallback_to_api: true

# API models to use when falling back
api_models:
  anthropic: claude-sonnet-4-20250514
  openai: gpt-4o
  google: gemini-2.0-flash
  xai: grok-3
  
# Timeout per model (seconds)
timeout: 120

# Run in parallel or sequential
parallel: true
```

## Workflow

### Step 1: Parse Model Selection

Determine which models to use:
1. Check user's inline specification (e.g., "with claude, gpt-4o")
2. If none specified, detect available CLIs and APIs
3. Default: use all available models

### Step 2: Prepare the Analysis Prompt

**CRITICAL**: Format the problem as an analysis request, NOT a code modification request:

```
ANALYSIS REQUEST - DO NOT MODIFY ANY CODE

Problem: [describe the problem]

Context: [relevant code or information]

Please provide:
1. Your analysis of the problem
2. Your recommended approach
3. Reasoning for your recommendation
4. Any concerns or edge cases
5. Confidence level (high/medium/low)

DO NOT provide code changes. Only provide analysis and recommendations.
```

### Step 3: Execute in Parallel

For API mode, use:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/model-council/scripts/api_council.py \
  --prompt "your analysis prompt here" \
  --models "claude-sonnet,gpt-4o,gemini-flash"
```

To check available resources:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/model-council/scripts/detect_clis.py
```

### Step 4: Collect Responses

Gather all model responses with metadata:
- Model name and version
- Response time
- Token usage (if available)
- Full analysis text

### Step 5: Analyze Consensus (Claude Code Does This)

Compare responses looking for:
- **Agreement**: Do models recommend the same approach?
- **Unique insights**: Does one model catch something others missed?
- **Disagreements**: Where do models differ and why?
- **Confidence levels**: Which models are most confident?

### Step 6: Claude Code Makes the Decision

**Claude Code (this session) is the decision-maker.** Use ultrathink to:
1. Evaluate each model's analysis
2. Identify the strongest reasoning
3. Note areas of consensus and disagreement
4. Decide on the best approach
5. Implement the solution (only Claude Code modifies code)

### Step 7: Deliver Results

Provide:
1. **Claude Code's decision** (the chosen approach)
2. **Consensus score** (how many models agreed)
3. **Summary of each model's input**
4. **Rationale for the decision**
5. **Implementation** (Claude Code executes the changes)

## Resource Detection

To check available CLIs and API keys:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/model-council/scripts/detect_clis.py
```

This checks for:
- Installed CLI tools (codex, gemini, aider)
- Configured API keys (Anthropic, OpenAI, Google, xAI)

## Comparison: code-council vs model-council

| Aspect | code-council | model-council |
|--------|--------------|---------------|
| Models used | Claude only | Multiple (Claude, GPT, Gemini, etc.) |
| Diversity source | Different approaches | Different architectures |
| Cost | Free (current session) | API costs per token |
| Speed | Fast (single model) | Slower (parallel calls) |
| Best for | Quick iterations | High-stakes decisions |
| Code changes | Claude makes changes | Only Claude makes changes (others analyze) |

## When to Use Each

**Use code-council when:**
- You want fast iterations
- The problem is well-defined
- You trust Claude's reasoning

**Use model-council when:**
- High-stakes code (production, security)
- You want architectural diversity
- Models might have different knowledge
- You want to verify Claude's answer

## Error Handling

**CLI not found**: Skip that model, log warning, continue with others.

**API key missing**: Skip that provider, try CLI fallback if available.

**Timeout**: Return partial results, note which models timed out.

**No models available**: Error with setup instructions.

## Example Output

```
## Model Council Results

### Consensus: HIGH (3/3 models agree on approach)

### Individual Analyses:

#### Claude Sonnet (API)
- Recommendation: Use a hash map for O(1) lookup
- Reasoning: Reduces time complexity from O(n²) to O(n)
- Confidence: High
- Unique insight: Noted potential memory constraints for large datasets

#### GPT-4o (API)  
- Recommendation: Use a hash map for O(1) lookup
- Reasoning: Standard pattern for duplicate detection
- Confidence: High
- Unique insight: Suggested early termination optimization

#### Gemini Flash (API)
- Recommendation: Use a hash map for O(1) lookup
- Reasoning: Most efficient approach for this problem
- Confidence: High
- Unique insight: Referenced similar pattern in standard library

### Claude Code Decision:
Based on unanimous consensus, implementing hash map approach with:
- Early termination from GPT-4o's suggestion
- Memory consideration from Claude Sonnet's analysis

### Implementation:
[Claude Code now implements the chosen solution]
```
