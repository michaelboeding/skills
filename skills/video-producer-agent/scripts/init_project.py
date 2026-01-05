#!/usr/bin/env python3
"""
Initialize a new video project with standard folder structure.
Creates project.json template and storyboard.md.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime


# Default project template
DEFAULT_PROJECT = {
    "name": "",
    "description": "",
    "created": "",
    "duration_target": 30,
    "aspect_ratio": "16:9",
    "resolution": "720p",
    "audio_strategy": "custom",  # "veo_audio" | "custom" | "silent"
    
    "scenes": [
        {
            "id": 1,
            "name": "scene1_intro",
            "prompt": "Describe the visual for this scene...",
            "duration": 6,
            "notes": ""
        }
    ],
    
    "voiceover": {
        "enabled": True,
        "text": "Write the voiceover script here...",
        "voice": "Charon",
        "style": "Professional, warm, engaging"
    },
    
    "music": {
        "enabled": True,
        "prompt": "Describe the music style...",
        "duration": 35,
        "bpm": 100,
        "brightness": 0.5
    },
    
    "assembly": {
        "transition": "fade",
        "transition_duration": 0.5,
        "music_volume": 0.3,
        "fade_in": 1.0,
        "fade_out": 2.0
    }
}

DEFAULT_STORYBOARD = '''# {project_name} - Storyboard

## Overview
**Duration Target:** {duration}s
**Aspect Ratio:** {aspect_ratio}
**Style:** [Describe the overall style]

---

## Scene Breakdown

### Scene 1: [Title] (0-6s)
**Visual:** [Describe what we see]
**Audio:** [Music only / Voiceover: "..."]
**Notes:** [Any special effects, transitions]

### Scene 2: [Title] (6-12s)
**Visual:** [Describe what we see]
**Audio:** [Voiceover: "..."]
**Notes:** []

### Scene 3: [Title] (12-18s)
**Visual:** [Describe what we see]
**Audio:** [Voiceover: "..." + music swells]
**Notes:** []

---

## Voiceover Script

> [Write the complete voiceover script here.
> This will be used for TTS generation.]

---

## Music Direction

- **Style:** [e.g., Modern electronic, cinematic, upbeat]
- **Energy:** [Low / Medium / High]
- **Key moments:** [e.g., "Build at 15s, resolve at end"]

---

## Technical Notes

- [ ] Audio strategy: custom (strip Veo audio, add VO + music)
- [ ] Transitions: fade (0.5s)
- [ ] Resolution: 720p
'''


def init_project(
    name: str,
    output_dir: str = None,
    duration: int = 30,
    aspect_ratio: str = "16:9",
    audio_strategy: str = "custom",
    num_scenes: int = 3
) -> dict:
    """Initialize a new video project.
    
    Args:
        name: Project name (used for folder)
        output_dir: Parent directory (defaults to current dir)
        duration: Target video duration in seconds
        aspect_ratio: Video aspect ratio (16:9, 9:16, 1:1)
        audio_strategy: "veo_audio", "custom", or "silent"
        num_scenes: Number of scene placeholders to create
    
    Returns:
        dict with project info and paths
    """
    # Sanitize project name for folder
    safe_name = name.lower().replace(" ", "_").replace("-", "_")
    safe_name = "".join(c for c in safe_name if c.isalnum() or c == "_")
    
    # Determine project path
    if output_dir:
        project_path = Path(output_dir) / safe_name
    else:
        project_path = Path.cwd() / safe_name
    
    # Check if exists
    if project_path.exists():
        return {"error": f"Project already exists: {project_path}"}
    
    try:
        # Create folder structure
        folders = ["scenes", "audio", "work", "output"]
        for folder in folders:
            (project_path / folder).mkdir(parents=True, exist_ok=True)
        
        # Create project.json
        project_config = DEFAULT_PROJECT.copy()
        project_config["name"] = name
        project_config["created"] = datetime.now().isoformat()
        project_config["duration_target"] = duration
        project_config["aspect_ratio"] = aspect_ratio
        project_config["audio_strategy"] = audio_strategy
        
        # Adjust scenes based on num_scenes and duration
        scene_duration = duration // num_scenes
        scenes = []
        for i in range(num_scenes):
            scenes.append({
                "id": i + 1,
                "name": f"scene{i+1}",
                "prompt": f"Describe scene {i+1} visual...",
                "duration": scene_duration if i < num_scenes - 1 else duration - (scene_duration * (num_scenes - 1)),
                "notes": ""
            })
        project_config["scenes"] = scenes
        
        # Adjust music duration
        project_config["music"]["duration"] = duration + 5  # Extra for fade out
        
        # Write project.json
        project_file = project_path / "project.json"
        with open(project_file, "w") as f:
            json.dump(project_config, f, indent=2)
        
        # Write storyboard.md
        storyboard_content = DEFAULT_STORYBOARD.format(
            project_name=name,
            duration=duration,
            aspect_ratio=aspect_ratio
        )
        storyboard_file = project_path / "storyboard.md"
        with open(storyboard_file, "w") as f:
            f.write(storyboard_content)
        
        # Write .gitignore for work folder
        gitignore_file = project_path / ".gitignore"
        with open(gitignore_file, "w") as f:
            f.write("work/\n*.wav\n*.mp3\n*.mp4\n!output/*.mp4\n")
        
        return {
            "success": True,
            "project_path": str(project_path),
            "project_file": str(project_file),
            "storyboard_file": str(storyboard_file),
            "folders": {
                "scenes": str(project_path / "scenes"),
                "audio": str(project_path / "audio"),
                "work": str(project_path / "work"),
                "output": str(project_path / "output")
            }
        }
        
    except Exception as e:
        return {"error": f"Failed to create project: {e}"}


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new video project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a new 30-second product video project
  python init_project.py --name "Product Launch Video" --duration 30
  
  # Create project in specific directory
  python init_project.py --name "Demo Video" --output ~/Videos/projects/
  
  # Create vertical video for social
  python init_project.py --name "Instagram Reel" --aspect-ratio 9:16 --duration 15
  
  # Create project with Veo's native audio
  python init_project.py --name "Cinematic Scene" --audio-strategy veo_audio

After creation:
  1. Edit project.json - fill in scene prompts, voiceover text, music style
  2. Edit storyboard.md - plan your video structure
  3. Run: python assemble.py --project /path/to/project/
        """
    )
    
    parser.add_argument("--name", "-n", required=True,
                        help="Project name")
    parser.add_argument("--output", "-o",
                        help="Parent directory for project folder")
    parser.add_argument("--duration", "-d", type=int, default=30,
                        help="Target video duration in seconds (default: 30)")
    parser.add_argument("--aspect-ratio", "-a", default="16:9",
                        choices=["16:9", "9:16", "1:1", "4:3"],
                        help="Video aspect ratio (default: 16:9)")
    parser.add_argument("--audio-strategy", default="custom",
                        choices=["custom", "veo_audio", "silent"],
                        help="Audio strategy (default: custom)")
    parser.add_argument("--scenes", "-s", type=int, default=3,
                        help="Number of scene placeholders (default: 3)")
    
    args = parser.parse_args()
    
    print(f"🎬 Initializing video project: {args.name}")
    
    result = init_project(
        args.name,
        args.output,
        args.duration,
        args.aspect_ratio,
        args.audio_strategy,
        args.scenes
    )
    
    if "error" in result:
        print(f"❌ Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"✅ Project created!")
        print(f"\n📁 Project folder: {result['project_path']}")
        print(f"\n📄 Files created:")
        print(f"   • project.json - Edit scene prompts, voiceover, music settings")
        print(f"   • storyboard.md - Plan your video structure")
        print(f"\n📂 Folders:")
        print(f"   • scenes/  - Generated video clips go here")
        print(f"   • audio/   - Voiceover and music files")
        print(f"   • work/    - Intermediate files (auto-cleaned)")
        print(f"   • output/  - Final video output")
        print(f"\n🎯 Next steps:")
        print(f"   1. Edit project.json with your scene prompts and settings")
        print(f"   2. Run: python assemble.py --project {result['project_path']}")


if __name__ == "__main__":
    main()
