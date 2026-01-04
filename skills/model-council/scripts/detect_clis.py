#!/usr/bin/env python3
"""
Detect available AI CLI tools and API keys for model-council.
"""

import os
import subprocess
import shutil
import json
from pathlib import Path


def load_env():
    """Load environment variables from .env file in repo root."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        env_file = current / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and value and key not in os.environ:
                            os.environ[key] = value
            return
        current = current.parent


load_env()


def check_cli(name: str, command: str = None) -> dict:
    """Check if a CLI tool is installed and accessible."""
    cmd = command or name
    path = shutil.which(cmd)
    
    return {
        "name": name,
        "command": cmd,
        "installed": path is not None,
        "path": path
    }


def check_api_key(name: str, env_var: str) -> dict:
    """Check if an API key is set."""
    key = os.environ.get(env_var, "")
    has_key = len(key) > 0
    
    return {
        "name": name,
        "env_var": env_var,
        "configured": has_key,
        "key_preview": f"{key[:8]}..." if has_key and len(key) > 8 else None
    }


def detect_all() -> dict:
    """Detect all available CLIs and API keys."""
    
    # CLI tools
    clis = [
        check_cli("claude", "claude"),
        check_cli("codex", "codex"),
        check_cli("gemini", "gemini"),
        check_cli("aider", "aider"),
        check_cli("cursor", "cursor"),
        check_cli("github-copilot", "gh copilot"),
    ]
    
    # API keys
    apis = [
        check_api_key("Anthropic (Claude)", "ANTHROPIC_API_KEY"),
        check_api_key("OpenAI (GPT)", "OPENAI_API_KEY"),
        check_api_key("Google (Gemini)", "GOOGLE_API_KEY"),
        check_api_key("xAI (Grok)", "XAI_API_KEY"),
    ]
    
    # Count available
    available_clis = [c for c in clis if c["installed"]]
    available_apis = [a for a in apis if a["configured"]]
    
    return {
        "clis": clis,
        "apis": apis,
        "summary": {
            "total_clis": len(available_clis),
            "total_apis": len(available_apis),
            "available_clis": [c["name"] for c in available_clis],
            "available_apis": [a["name"] for a in available_apis],
        }
    }


def main():
    results = detect_all()
    
    print("=" * 60)
    print("Model Council - Available Resources")
    print("=" * 60)
    
    print("\n📟 CLI Tools:")
    print("-" * 40)
    for cli in results["clis"]:
        status = "✅ Installed" if cli["installed"] else "❌ Not found"
        print(f"  {cli['name']:20} {status}")
        if cli["installed"]:
            print(f"                       Path: {cli['path']}")
    
    print("\n🔑 API Keys:")
    print("-" * 40)
    for api in results["apis"]:
        status = "✅ Configured" if api["configured"] else "❌ Not set"
        print(f"  {api['name']:20} {status}")
        if api["configured"]:
            print(f"                       {api['env_var']}={api['key_preview']}")
    
    print("\n📊 Summary:")
    print("-" * 40)
    print(f"  Available CLIs: {results['summary']['total_clis']}")
    print(f"  Available APIs: {results['summary']['total_apis']}")
    
    if results['summary']['available_clis']:
        print(f"\n  Ready to use (CLI): {', '.join(results['summary']['available_clis'])}")
    if results['summary']['available_apis']:
        print(f"  Ready to use (API): {', '.join(results['summary']['available_apis'])}")
    
    if results['summary']['total_clis'] == 0 and results['summary']['total_apis'] == 0:
        print("\n⚠️  No models available! Install CLI tools or set API keys.")
        print("\nTo install CLIs:")
        print("  npm install -g @openai/codex")
        print("  # See SKILL.md for more options")
        print("\nTo set API keys:")
        print("  export OPENAI_API_KEY='sk-...'")
        print("  export ANTHROPIC_API_KEY='sk-ant-...'")
    
    # Output JSON for programmatic use
    print("\n" + "=" * 60)
    print("JSON Output:")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
