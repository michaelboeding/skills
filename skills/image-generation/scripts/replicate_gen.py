#!/usr/bin/env python3
"""
Replicate Image Generation Script
Requires: REPLICATE_API_TOKEN environment variable
"""

import argparse
import os
import sys
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import time


# Popular image generation models on Replicate
MODELS = {
    "flux-pro": "black-forest-labs/flux-pro",
    "flux-schnell": "black-forest-labs/flux-schnell", 
    "flux-dev": "black-forest-labs/flux-dev",
    "sdxl": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    "sdxl-lightning": "bytedance/sdxl-lightning-4step:5f24084160c9089501c1b3545d9be3c27883ae2239b6f412990e82d4a6210f8f"
}


def generate_image(prompt: str, model: str = "flux-schnell", 
                   aspect_ratio: str = "1:1", num_outputs: int = 1) -> dict:
    """Generate an image using Replicate API."""
    
    api_token = os.environ.get("REPLICATE_API_TOKEN")
    if not api_token:
        return {"error": "REPLICATE_API_TOKEN environment variable not set. Please set it in your shell or .env file."}
    
    # Get model identifier
    model_id = MODELS.get(model, model)
    
    # Determine API endpoint based on model format
    if ":" in model_id:
        # Versioned model
        url = "https://api.replicate.com/v1/predictions"
        data = {
            "version": model_id.split(":")[1],
            "input": {
                "prompt": prompt,
                "num_outputs": num_outputs
            }
        }
    else:
        # Official model (use deployments API)
        url = f"https://api.replicate.com/v1/models/{model_id}/predictions"
        data = {
            "input": {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "num_outputs": num_outputs,
                "output_format": "png"
            }
        }
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Create prediction
        request = Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode())
        
        prediction_url = result.get("urls", {}).get("get") or f"https://api.replicate.com/v1/predictions/{result['id']}"
        
        # Poll for completion
        print("Waiting for generation to complete...")
        max_attempts = 60
        for attempt in range(max_attempts):
            poll_request = Request(prediction_url, headers=headers)
            with urlopen(poll_request, timeout=30) as response:
                status = json.loads(response.read().decode())
            
            if status["status"] == "succeeded":
                output = status.get("output", [])
                if isinstance(output, list) and len(output) > 0:
                    image_url = output[0]
                elif isinstance(output, str):
                    image_url = output
                else:
                    return {"error": f"Unexpected output format: {output}"}
                
                return {
                    "success": True,
                    "url": image_url,
                    "model": model_id,
                    "prompt": prompt,
                    "prediction_id": status["id"]
                }
            
            elif status["status"] == "failed":
                return {"error": f"Generation failed: {status.get('error', 'Unknown error')}"}
            
            elif status["status"] == "canceled":
                return {"error": "Generation was canceled"}
            
            # Still processing
            time.sleep(2)
        
        return {"error": "Generation timed out after 2 minutes"}
            
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        try:
            error_json = json.loads(error_body)
            error_message = error_json.get("detail", error_body)
        except:
            error_message = error_body
        return {"error": f"API error ({e.code}): {error_message}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


def main():
    parser = argparse.ArgumentParser(description="Generate images using Replicate")
    parser.add_argument("--prompt", "-p", required=True, help="Image generation prompt")
    parser.add_argument("--model", "-m", default="flux-schnell",
                        choices=list(MODELS.keys()),
                        help="Model to use (default: flux-schnell)")
    parser.add_argument("--aspect-ratio", "-a", default="1:1",
                        choices=["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"],
                        help="Aspect ratio (default: 1:1)")
    parser.add_argument("--num", "-n", type=int, default=1,
                        help="Number of images to generate (default: 1)")
    
    args = parser.parse_args()
    
    print(f"Generating image with Replicate ({args.model})...")
    print(f"Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}")
    print(f"Aspect ratio: {args.aspect_ratio}")
    print()
    
    result = generate_image(args.prompt, args.model, args.aspect_ratio, args.num)
    
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print("✓ Image generated successfully!")
        print(f"URL: {result['url']}")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
