# Skills

Personal collection of agent skills using the open [SKILL.md standard](https://agentskills.io). Works with Claude (claude.ai, Claude Code, API), Cursor, and other AI assistants.

## Installation

### Claude.ai

1. Download the `.skill` file from [Releases](../../releases)
2. Go to Settings → Skills
3. Upload the file

### Claude Code

```bash
# Install as plugin from GitHub
/plugin add YOUR_USERNAME/skills

# Or install from local folder
/plugin add /path/to/skills
```

### Cursor / Other Tools

Copy the `skills/` folder to your project or follow your tool's skill installation docs.

---

## Skills

| Skill | Description |
|-------|-------------|
| [code-council](skills/code-council/) | Ensemble problem-solving that generates multiple independent code solutions, tests them, and synthesizes the best answer. Based on [self-consistency research](https://arxiv.org/abs/2311.17311). |

---

## Usage Examples

### code-council

```
code council: fix this bug in my function

code council: write a function to find duplicates in an array

code council of 5: critical production bug, need extra confidence
```

---

## Adding a New Skill

1. Create a folder: `skills/your-skill-name/`
2. Add `SKILL.md` with frontmatter:
   ```yaml
   ---
   name: your-skill-name
   description: What it does and when to use it
   ---
   ```
3. Add instructions in markdown below the frontmatter
4. Skills are auto-discovered from the `skills/` folder - no manifest update needed

---

## License

MIT
