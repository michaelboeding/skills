# Skills

Personal collection of agent skills using the open [SKILL.md standard](https://agentskills.io). Works with Claude (claude.ai, Claude Code, API), Cursor, and other AI assistants.

## Installation

### Claude Code

```bash
# Add the marketplace
/plugin marketplace add michaelboeding/skills

# Install the plugin
/plugin install skills@michaelboeding-skills
```

### Claude.ai

1. Download the `.skill` file from [Releases](../../releases)
2. Go to Settings → Skills
3. Upload the file

### Cursor / Other Tools

Copy the `skills/` folder to your project or follow your tool's skill installation docs.

---

## Setup

### API Keys (Required for some skills)

Some skills require API keys to function. Copy the example environment file and add your keys:

```bash
cp env.example .env
```

Then export the variables in your shell profile (`~/.bashrc`, `~/.zshrc`, or `~/.bash_profile`):

```bash
# Image Generation APIs
export OPENAI_API_KEY="sk-..."          # For DALL-E 3
export STABILITY_API_KEY="sk-..."       # For Stable Diffusion
export REPLICATE_API_TOKEN="r8_..."     # For Flux, SDXL, etc.
```

Restart your terminal or run `source ~/.bashrc` (or equivalent) for changes to take effect.

**Where to get API keys:**
- OpenAI: https://platform.openai.com/api-keys
- Stability AI: https://platform.stability.ai/account/keys
- Replicate: https://replicate.com/account/api-tokens

---

## Skills

| Skill | Description | API Keys |
|-------|-------------|----------|
| [code-council](skills/code-council/) | Ensemble problem-solving that generates multiple independent code solutions, tests them, and synthesizes the best answer. Based on [self-consistency research](https://arxiv.org/abs/2311.17311). | None |
| [image-generation](skills/image-generation/) | Generate images using AI models (DALL-E 3, Stable Diffusion, Flux). Handles prompt crafting, API selection, and delivery. | `OPENAI_API_KEY`, `STABILITY_API_KEY`, or `REPLICATE_API_TOKEN` |

---

## Usage Examples

### code-council

Generate multiple code solutions and pick the best one:

```
code council: fix this bug in my function

code council: write a function to find duplicates in an array

code council of 5: critical production bug, need extra confidence
```

### image-generation

Generate images with AI:

```
generate an image of a sunset over mountains

create a cyberpunk cityscape at night

make a watercolor painting of a cat
```

---

## License

MIT
