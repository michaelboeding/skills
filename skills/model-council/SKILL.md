---
name: model-council
description: This skill should be used when the user asks for "model council", "multi-model", "compare models", "ask multiple AIs", "consensus across models", "run on different models", or wants to get solutions from multiple AI providers (Claude, GPT, Gemini, Grok) and compare results. Orchestrates parallel execution across AI models/CLIs and synthesizes the best answer.
---

# Model Council: Multi-Model Consensus

Run the same problem through multiple AI models in parallel, then compare and synthesize the best solution.

Unlike code-council (which uses one model with multiple approaches), model-council leverages **different model architectures** for true ensemble diversity.

## Why Multi-Model?

Different models have different:
- Training data and knowledge cutoffs
- Reasoning patterns and biases
- Strengths (math, code, creativity, etc.)

When multiple independent models agree → High confidence the answer is correct.

## Execution Modes

### Mode 1: CLI Agents (Recommended - Uses Your Existing Accounts)

Call CLI tools that use your logged-in accounts - no extra API costs!

| CLI Tool | Model | Install |
|----------|-------|---------|
| `claude` | Claude (this session) | Already running |
| `codex` | OpenAI Codex CLI | `npm install -g @openai/codex` |
| `gemini` | Google Gemini CLI | `npm install -g @anthropic-ai/gemini-cli` |
| `aider` | Any (configurable) | `pip install aider-chat` |

### Mode 2: API Calls (Pay per token)

Direct API calls - more reliable but costs money.

Required environment variables:
- `ANTHROPIC_API_KEY` - For Claude API
- `OPENAI_API_KEY` - For GPT-4 API
- `GOOGLE_API_KEY` - For Gemini API
- `XAI_API_KEY` - For Grok API

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
2. If none specified, check config file
3. If no config, detect available CLIs and APIs

### Step 2: Prepare the Prompt

Format the problem for each model:
- Keep the core problem identical
- Adjust formatting if needed for specific models
- Include any necessary context

### Step 3: Execute in Parallel

For CLI mode, use the orchestrator script:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/model-council/scripts/orchestrate.py \
  --prompt "your problem here" \
  --models "claude,codex,gemini" \
  --parallel
```

For API mode:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/model-council/scripts/api_council.py \
  --prompt "your problem here" \
  --models "claude-sonnet,gpt-4o,gemini-flash"
```

### Step 4: Collect Responses

Gather all model responses with metadata:
- Model name and version
- Response time
- Token usage (if available)
- Full response

### Step 5: Analyze Consensus

Compare responses looking for:
- **Agreement**: Do models produce the same answer/approach?
- **Unique insights**: Does one model catch something others missed?
- **Disagreements**: Where do models differ and why?

### Step 6: Synthesize Best Answer

Use ultrathink to:
1. Evaluate each response's correctness
2. Identify the strongest reasoning
3. Combine best elements from multiple responses
4. Produce final synthesized answer

### Step 7: Deliver Results

Provide:
1. **Final synthesized answer** (best combined solution)
2. **Consensus score** (how many models agreed)
3. **Individual responses** (for transparency)
4. **Insights** (what each model contributed)

## CLI Detection

To check available CLIs:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/model-council/scripts/detect_clis.py
```

This checks for:
- `claude` - Claude Code CLI
- `codex` - OpenAI Codex CLI
- `gemini` - Gemini CLI
- `aider` - Aider (multi-model)
- `cursor` - Cursor AI (if applicable)

## Comparison: code-council vs model-council

| Aspect | code-council | model-council |
|--------|--------------|---------------|
| Models used | Claude only | Multiple (Claude, GPT, Gemini, etc.) |
| Diversity source | Different approaches | Different architectures |
| Cost | Free (uses current session) | Free (CLIs) or paid (APIs) |
| Speed | Fast (single model) | Slower (parallel calls) |
| Best for | Quick iterations | High-stakes decisions |

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

### Consensus: HIGH (3/3 models agree)

### Synthesized Solution:
[Combined best answer here]

### Individual Responses:

#### Claude (via CLI)
[Response...]
Reasoning quality: High
Unique contribution: Caught edge case with null input

#### GPT-4o (via Codex CLI)  
[Response...]
Reasoning quality: High
Unique contribution: Suggested performance optimization

#### Gemini (via CLI)
[Response...]
Reasoning quality: Medium
Unique contribution: Referenced relevant documentation

### Confidence: HIGH
All models converged on the same core solution with complementary insights.
```
