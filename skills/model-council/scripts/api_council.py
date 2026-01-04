#!/usr/bin/env python3
"""
API-based Model Council - Call multiple AI APIs in parallel.
Requires API keys for each provider.
"""

import argparse
import os
import sys
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import time
from pathlib import Path


def load_env():
    """Load environment variables from .env file.
    
    Checks these locations in order:
    1. ~/.config/skills/.env (recommended)
    2. ~/.env (home directory)
    3. Walk up from script location (for local development)
    """
    def parse_env_file(env_file: Path):
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
            return True
        return False
    
    home = Path.home()
    if parse_env_file(home / ".config" / "skills" / ".env"):
        return
    if parse_env_file(home / ".env"):
        return
    
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if parse_env_file(current / ".env"):
            return
        current = current.parent


load_env()


# Model configurations
MODELS = {
    # Anthropic
    "claude-sonnet": {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-20250514",
        "env_var": "ANTHROPIC_API_KEY",
        "url": "https://api.anthropic.com/v1/messages",
    },
    "claude-opus": {
        "provider": "anthropic", 
        "model_id": "claude-opus-4-20250514",
        "env_var": "ANTHROPIC_API_KEY",
        "url": "https://api.anthropic.com/v1/messages",
    },
    # OpenAI
    "gpt-4o": {
        "provider": "openai",
        "model_id": "gpt-4o",
        "env_var": "OPENAI_API_KEY",
        "url": "https://api.openai.com/v1/chat/completions",
    },
    "gpt-4-turbo": {
        "provider": "openai",
        "model_id": "gpt-4-turbo",
        "env_var": "OPENAI_API_KEY", 
        "url": "https://api.openai.com/v1/chat/completions",
    },
    "o1": {
        "provider": "openai",
        "model_id": "o1",
        "env_var": "OPENAI_API_KEY",
        "url": "https://api.openai.com/v1/chat/completions",
    },
    # Google
    "gemini-flash": {
        "provider": "google",
        "model_id": "gemini-2.0-flash",
        "env_var": "GOOGLE_API_KEY",
        "url": "https://generativelanguage.googleapis.com/v1beta/models",
    },
    "gemini-pro": {
        "provider": "google",
        "model_id": "gemini-1.5-pro",
        "env_var": "GOOGLE_API_KEY",
        "url": "https://generativelanguage.googleapis.com/v1beta/models",
    },
    # xAI
    "grok": {
        "provider": "xai",
        "model_id": "grok-3",
        "env_var": "XAI_API_KEY",
        "url": "https://api.x.ai/v1/chat/completions",
    },
}


def call_anthropic(prompt: str, model_config: dict) -> dict:
    """Call Anthropic Claude API."""
    api_key = os.environ.get(model_config["env_var"])
    if not api_key:
        return {"error": f"{model_config['env_var']} not set. Get key at https://console.anthropic.com/"}
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    data = {
        "model": model_config["model_id"],
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        request = Request(model_config["url"], data=json.dumps(data).encode(), headers=headers, method="POST")
        start_time = time.time()
        with urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode())
            elapsed = time.time() - start_time
            
            return {
                "success": True,
                "response": result["content"][0]["text"],
                "model": model_config["model_id"],
                "provider": "anthropic",
                "elapsed_seconds": round(elapsed, 2),
                "usage": result.get("usage", {})
            }
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        return {"error": f"Anthropic API error ({e.code}): {error_body}"}
    except Exception as e:
        return {"error": f"Anthropic request failed: {str(e)}"}


def call_openai(prompt: str, model_config: dict) -> dict:
    """Call OpenAI API."""
    api_key = os.environ.get(model_config["env_var"])
    if not api_key:
        return {"error": f"{model_config['env_var']} not set. Get key at https://platform.openai.com/api-keys"}
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model_config["model_id"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4096
    }
    
    try:
        request = Request(model_config["url"], data=json.dumps(data).encode(), headers=headers, method="POST")
        start_time = time.time()
        with urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode())
            elapsed = time.time() - start_time
            
            return {
                "success": True,
                "response": result["choices"][0]["message"]["content"],
                "model": model_config["model_id"],
                "provider": "openai",
                "elapsed_seconds": round(elapsed, 2),
                "usage": result.get("usage", {})
            }
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        return {"error": f"OpenAI API error ({e.code}): {error_body}"}
    except Exception as e:
        return {"error": f"OpenAI request failed: {str(e)}"}


def call_google(prompt: str, model_config: dict) -> dict:
    """Call Google Gemini API."""
    api_key = os.environ.get(model_config["env_var"])
    if not api_key:
        return {"error": f"{model_config['env_var']} not set. Get key at https://aistudio.google.com/apikey"}
    
    url = f"{model_config['url']}/{model_config['model_id']}:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 4096}
    }
    
    try:
        request = Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
        start_time = time.time()
        with urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode())
            elapsed = time.time() - start_time
            
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            
            return {
                "success": True,
                "response": text,
                "model": model_config["model_id"],
                "provider": "google",
                "elapsed_seconds": round(elapsed, 2),
                "usage": result.get("usageMetadata", {})
            }
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        return {"error": f"Google API error ({e.code}): {error_body}"}
    except Exception as e:
        return {"error": f"Google request failed: {str(e)}"}


def call_xai(prompt: str, model_config: dict) -> dict:
    """Call xAI Grok API."""
    api_key = os.environ.get(model_config["env_var"])
    if not api_key:
        return {"error": f"{model_config['env_var']} not set. Get key at https://console.x.ai/"}
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model_config["model_id"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4096
    }
    
    try:
        request = Request(model_config["url"], data=json.dumps(data).encode(), headers=headers, method="POST")
        start_time = time.time()
        with urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode())
            elapsed = time.time() - start_time
            
            return {
                "success": True,
                "response": result["choices"][0]["message"]["content"],
                "model": model_config["model_id"],
                "provider": "xai",
                "elapsed_seconds": round(elapsed, 2),
                "usage": result.get("usage", {})
            }
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        return {"error": f"xAI API error ({e.code}): {error_body}"}
    except Exception as e:
        return {"error": f"xAI request failed: {str(e)}"}


def call_model(model_name: str, prompt: str) -> dict:
    """Call a model by name."""
    if model_name not in MODELS:
        return {"error": f"Unknown model: {model_name}. Available: {list(MODELS.keys())}"}
    
    config = MODELS[model_name]
    provider = config["provider"]
    
    if provider == "anthropic":
        return call_anthropic(prompt, config)
    elif provider == "openai":
        return call_openai(prompt, config)
    elif provider == "google":
        return call_google(prompt, config)
    elif provider == "xai":
        return call_xai(prompt, config)
    else:
        return {"error": f"Unknown provider: {provider}"}


def run_council(prompt: str, models: list, parallel: bool = True) -> dict:
    """Run the model council."""
    results = {}
    
    if parallel:
        with ThreadPoolExecutor(max_workers=len(models)) as executor:
            futures = {executor.submit(call_model, model, prompt): model for model in models}
            for future in as_completed(futures):
                model = futures[future]
                try:
                    results[model] = future.result()
                except Exception as e:
                    results[model] = {"error": str(e)}
    else:
        for model in models:
            print(f"Calling {model}...")
            results[model] = call_model(model, prompt)
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Run Model Council via APIs")
    parser.add_argument("--prompt", "-p", required=True, help="The prompt to send to all models")
    parser.add_argument("--models", "-m", default="claude-sonnet,gpt-4o,gemini-flash",
                        help="Comma-separated list of models (default: claude-sonnet,gpt-4o,gemini-flash)")
    parser.add_argument("--sequential", "-s", action="store_true",
                        help="Run sequentially instead of parallel")
    parser.add_argument("--list-models", "-l", action="store_true",
                        help="List available models")
    
    args = parser.parse_args()
    
    if args.list_models:
        print("Available models:")
        for name, config in MODELS.items():
            print(f"  {name:20} ({config['provider']}) - {config['model_id']}")
        return
    
    models = [m.strip() for m in args.models.split(",")]
    
    print(f"🏛️ Model Council")
    print(f"Models: {', '.join(models)}")
    print(f"Mode: {'Sequential' if args.sequential else 'Parallel'}")
    print("-" * 60)
    
    results = run_council(args.prompt, models, parallel=not args.sequential)
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    successful = 0
    for model, result in results.items():
        print(f"\n### {model}")
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            successful += 1
            print(f"✅ Success ({result['elapsed_seconds']}s)")
            print(f"Response preview: {result['response'][:200]}...")
    
    print(f"\n📊 Summary: {successful}/{len(models)} models succeeded")
    
    # Output full JSON
    print("\n" + "=" * 60)
    print("Full JSON Output:")
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
