#!/bin/bash
# Quick script to force-update the skills plugin in Claude Code
# Run this after pulling new changes from GitHub

echo "🔄 Updating skills plugin..."

# Clear the cache
rm -rf ~/.claude/plugins/cache/michaelboeding-skills
rm -rf ~/.claude/plugins/cache/temp_local_*

echo "✅ Cache cleared"
echo ""
echo "Now do ONE of the following:"
echo ""
echo "Option 1 (if plugin is from marketplace):"
echo "  In Claude Code, run:"
echo "    /plugin update skills@michaelboeding-skills"
echo ""
echo "Option 2 (force reinstall):"
echo "  In Claude Code, run:"
echo "    /plugin remove skills@michaelboeding-skills"
echo "    /plugin install skills@michaelboeding-skills"
echo ""
echo "Then RESTART Claude Code (quit and reopen)"
