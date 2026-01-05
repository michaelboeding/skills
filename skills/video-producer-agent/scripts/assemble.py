#!/usr/bin/env python3
"""
Assemble a complete video from a project.json configuration.
Orchestrates video generation, audio generation, and final assembly.
"""

import argparse
import json
import subprocess
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
import time


def get_skill_path(skill_name: str, script_name: str) -> Path:
    """Get the path to a skill script, checking multiple locations."""
    # Try relative path first (when running from skills repo)
    script_dir = Path(__file__).parent.parent.parent
    skill_path = script_dir / skill_name / "scripts" / script_name
    if skill_path.exists():
        return skill_path
    
    # Try CLAUDE_PLUGIN_ROOT environment variable
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        skill_path = Path(plugin_root) / "skills" / skill_name / "scripts" / script_name
        if skill_path.exists():
            return skill_path
    
    # Try common plugin cache locations
    home = Path.home()
    cache_paths = [
        home / ".claude" / "plugins" / "cache",
        home / ".cursor" / "extensions" / "skills",
    ]
    for cache in cache_paths:
        if cache.exists():
            for subdir in cache.iterdir():
                if subdir.is_dir() and "skills" in subdir.name.lower():
                    skill_path = subdir / "skills" / skill_name / "scripts" / script_name
                    if skill_path.exists():
                        return skill_path
    
    raise FileNotFoundError(f"Could not find {skill_name}/{script_name}")


def run_script(script_path: Path, args: list, cwd: str = None, timeout: int = 600, stream: bool = True) -> dict:
    """Run a Python script and return result.
    
    Args:
        stream: If True, stream output to console in real-time
    """
    cmd = [sys.executable, str(script_path)] + args
    
    try:
        if stream:
            # Stream output in real-time
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=cwd,
                bufsize=1
            )
            
            output_lines = []
            start = time.time()
            
            for line in proc.stdout:
                output_lines.append(line)
                # Show key progress lines
                line_stripped = line.strip()
                if any(x in line_stripped.lower() for x in ['generating', 'complete', 'error', '✅', '❌', '🔄', 'scene', 'batch', 'elapsed']):
                    print(f"    {line_stripped}")
                elif time.time() - start > 30 and 'still' in line_stripped.lower():
                    print(f"    {line_stripped}")
            
            proc.wait(timeout=timeout)
            
            if proc.returncode != 0:
                return {
                    "success": False,
                    "error": "".join(output_lines[-20:]),
                    "stdout": "".join(output_lines)
                }
            
            return {
                "success": True,
                "stdout": "".join(output_lines),
                "stderr": ""
            }
        else:
            # Capture output (original behavior)
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=timeout
            )
            
            if proc.returncode != 0:
                return {
                    "success": False,
                    "error": proc.stderr[-1000:] if proc.stderr else "Unknown error",
                    "stdout": proc.stdout
                }
            
            return {
                "success": True,
                "stdout": proc.stdout,
                "stderr": proc.stderr
            }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Timeout after {timeout}s"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_ffmpeg(args: list, cwd: str = None, timeout: int = 300) -> dict:
    """Run FFmpeg command."""
    cmd = ["ffmpeg", "-y"] + args
    
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout
        )
        
        if proc.returncode != 0:
            return {
                "success": False,
                "error": proc.stderr[-500:] if proc.stderr else "Unknown error"
            }
        
        return {"success": True}
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"FFmpeg timeout after {timeout}s"}
    except Exception as e:
        return {"success": False, "error": str(e)}


class VideoAssembler:
    """Orchestrates the video assembly pipeline."""
    
    def __init__(self, project_path: str, dry_run: bool = False, skip_generation: bool = False):
        self.project_path = Path(project_path)
        self.dry_run = dry_run
        self.skip_generation = skip_generation
        
        # Load project config
        self.project_file = self.project_path / "project.json"
        if not self.project_file.exists():
            raise FileNotFoundError(f"project.json not found in {project_path}")
        
        with open(self.project_file) as f:
            self.config = json.load(f)
        
        # Set up paths
        self.scenes_dir = self.project_path / "scenes"
        self.audio_dir = self.project_path / "audio"
        self.work_dir = self.project_path / "work"
        self.output_dir = self.project_path / "output"
        
        # Ensure directories exist
        for d in [self.scenes_dir, self.audio_dir, self.work_dir, self.output_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def log(self, msg: str, level: str = "info"):
        """Print a log message."""
        icons = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️", "step": "🔄"}
        print(f"{icons.get(level, '•')} {msg}")
    
    def print_progress_banner(self, current_step: int, step_name: str, step_times: dict):
        """Print a progress banner showing all steps."""
        steps = [
            ("1", "Generate Scenes", "generate_scenes"),
            ("2", "Strip Audio", "strip_audio"),
            ("3", "Generate Voiceover", "generate_voiceover"),
            ("4", "Generate Music", "generate_music"),
            ("5", "Mix Audio", "mix_audio"),
            ("6", "Concatenate Video", "concatenate_videos"),
            ("7", "Merge Audio+Video", "merge_audio_video"),
        ]
        
        # Filter based on audio strategy
        if self.config["audio_strategy"] == "veo_audio":
            steps = [s for s in steps if s[2] not in ["strip_audio", "generate_voiceover", "generate_music", "mix_audio", "merge_audio_video"]]
        elif self.config["audio_strategy"] == "silent":
            steps = [s for s in steps if s[2] not in ["generate_voiceover", "generate_music", "mix_audio", "merge_audio_video"]]
        
        print("\n" + "━" * 60)
        print(f"📊 ASSEMBLY PROGRESS - {self.config['name']}")
        print("━" * 60)
        
        for i, (num, name, key) in enumerate(steps):
            if key in step_times:
                if step_times[key].get("success"):
                    status = f"✅ Complete ({step_times[key].get('time', 0):.1f}s)"
                else:
                    status = "❌ Failed"
            elif key == step_name:
                status = "🔄 Running..."
            else:
                status = "⏳ Pending"
            
            print(f"  {num}. {name:<20} → {status}")
        
        print("━" * 60 + "\n")
    
    def assemble(self) -> dict:
        """Run the full assembly pipeline."""
        start_time = time.time()
        step_times = {}
        
        print("\n" + "=" * 60)
        print("🎬 VIDEO ASSEMBLY STARTING")
        print("=" * 60)
        print(f"  Project: {self.config['name']}")
        print(f"  Scenes: {len(self.config.get('scenes', []))}")
        print(f"  Audio: {self.config['audio_strategy']}")
        print(f"  Duration: ~{self.config.get('duration_target', 30)}s target")
        print("=" * 60 + "\n")
        
        self.log(f"Starting assembly for: {self.config['name']}", "step")
        self.log(f"Audio strategy: {self.config['audio_strategy']}")
        
        results = {
            "project": self.config["name"],
            "steps": []
        }
        
        try:
            # Step 1: Generate video scenes
            if not self.skip_generation:
                self.print_progress_banner(1, "generate_scenes", step_times)
                step_start = time.time()
                step_result = self.generate_scenes()
                step_times["generate_scenes"] = {"success": step_result.get("success"), "time": time.time() - step_start}
                results["steps"].append({"name": "generate_scenes", **step_result})
                if not step_result.get("success"):
                    return {"success": False, "error": "Scene generation failed", **results}
            else:
                self.log("Skipping scene generation (--skip-generation)", "warning")
                step_times["generate_scenes"] = {"success": True, "time": 0}
            
            # Step 2: Handle audio based on strategy
            if self.config["audio_strategy"] == "custom":
                # Strip audio from scenes
                self.print_progress_banner(2, "strip_audio", step_times)
                step_start = time.time()
                step_result = self.strip_audio_from_scenes()
                step_times["strip_audio"] = {"success": step_result.get("success"), "time": time.time() - step_start}
                results["steps"].append({"name": "strip_audio", **step_result})
                if not step_result.get("success"):
                    return {"success": False, "error": "Audio stripping failed", **results}
                
                # Generate voiceover
                if self.config.get("voiceover", {}).get("enabled", True) and not self.skip_generation:
                    self.print_progress_banner(3, "generate_voiceover", step_times)
                    step_start = time.time()
                    step_result = self.generate_voiceover()
                    step_times["generate_voiceover"] = {"success": step_result.get("success"), "time": time.time() - step_start}
                    results["steps"].append({"name": "generate_voiceover", **step_result})
                    if not step_result.get("success"):
                        self.log("Voiceover generation failed, continuing without", "warning")
                
                # Generate music
                if self.config.get("music", {}).get("enabled", True) and not self.skip_generation:
                    self.print_progress_banner(4, "generate_music", step_times)
                    step_start = time.time()
                    step_result = self.generate_music()
                    step_times["generate_music"] = {"success": step_result.get("success"), "time": time.time() - step_start}
                    results["steps"].append({"name": "generate_music", **step_result})
                    if not step_result.get("success"):
                        self.log("Music generation failed, continuing without", "warning")
                
                # Mix audio
                self.print_progress_banner(5, "mix_audio", step_times)
                step_start = time.time()
                step_result = self.mix_audio()
                step_times["mix_audio"] = {"success": step_result.get("success"), "time": time.time() - step_start}
                results["steps"].append({"name": "mix_audio", **step_result})
                
            elif self.config["audio_strategy"] == "silent":
                self.print_progress_banner(2, "strip_audio", step_times)
                step_start = time.time()
                step_result = self.strip_audio_from_scenes()
                step_times["strip_audio"] = {"success": step_result.get("success"), "time": time.time() - step_start}
                results["steps"].append({"name": "strip_audio", **step_result})
            
            # Step 3: Concatenate video clips
            self.print_progress_banner(6, "concatenate_videos", step_times)
            step_start = time.time()
            step_result = self.concatenate_videos()
            step_times["concatenate_videos"] = {"success": step_result.get("success"), "time": time.time() - step_start}
            results["steps"].append({"name": "concatenate_videos", **step_result})
            if not step_result.get("success"):
                return {"success": False, "error": "Video concatenation failed", **results}
            
            # Step 4: Merge audio with video (if custom audio)
            if self.config["audio_strategy"] == "custom":
                self.print_progress_banner(7, "merge_audio_video", step_times)
                step_start = time.time()
                step_result = self.merge_audio_video()
                step_times["merge_audio_video"] = {"success": step_result.get("success"), "time": time.time() - step_start}
                results["steps"].append({"name": "merge_audio_video", **step_result})
                if not step_result.get("success"):
                    return {"success": False, "error": "Audio/video merge failed", **results}
            
            # Calculate total time
            elapsed = time.time() - start_time
            results["success"] = True
            results["total_time"] = round(elapsed, 1)
            results["output_file"] = str(self.get_output_filename())
            
            # Final progress banner
            self.print_progress_banner(99, "done", step_times)
            
            self.log(f"Assembly complete in {elapsed:.1f}s", "success")
            self.log(f"Output: {results['output_file']}")
            
            return results
            
        except Exception as e:
            return {"success": False, "error": str(e), **results}
    
    def generate_scenes(self) -> dict:
        """Generate video scenes using Veo."""
        self.log("Generating video scenes with Veo...", "step")
        
        if self.dry_run:
            return {"success": True, "dry_run": True}
        
        try:
            veo_script = get_skill_path("video-generation", "veo.py")
        except FileNotFoundError as e:
            return {"success": False, "error": str(e)}
        
        # Create batch JSON for Veo
        scenes = self.config.get("scenes", [])
        if not scenes:
            return {"success": False, "error": "No scenes defined in project.json"}
        
        # Validate durations - Veo only accepts 4, 6, or 8 seconds
        VALID_DURATIONS = [4, 6, 8]
        invalid_scenes = []
        for scene in scenes:
            dur = scene.get("duration", 6)
            if dur not in VALID_DURATIONS:
                invalid_scenes.append(f"Scene {scene.get('id', '?')}: {dur}s")
        
        if invalid_scenes:
            self.log(f"Invalid scene durations detected (Veo requires 4, 6, or 8 seconds):", "error")
            for s in invalid_scenes:
                print(f"    ❌ {s}")
            print(f"\n    💡 Fix: Edit project.json and set all scene durations to 4, 6, or 8")
            return {"success": False, "error": f"Invalid durations: {', '.join(invalid_scenes)}. Veo only accepts 4, 6, or 8 seconds."}
        
        batch_config = []
        for scene in scenes:
            batch_config.append({
                "prompt": scene["prompt"],
                "duration": scene.get("duration", 6),
                "output": f"{scene['name']}.mp4"
            })
        
        # Write batch file
        batch_file = self.work_dir / "scenes_batch.json"
        with open(batch_file, "w") as f:
            json.dump(batch_config, f, indent=2)
        
        # Run Veo batch generation
        args = [
            "--batch", str(batch_file),
            "--aspect-ratio", self.config.get("aspect_ratio", "16:9"),
            "--resolution", self.config.get("resolution", "720p")
        ]
        
        result = run_script(veo_script, args, cwd=str(self.scenes_dir), timeout=1200)
        
        if result["success"]:
            # Verify files were created
            generated = list(self.scenes_dir.glob("*.mp4"))
            return {
                "success": True,
                "files": [f.name for f in generated],
                "count": len(generated)
            }
        
        return result
    
    def strip_audio_from_scenes(self) -> dict:
        """Strip audio from all scene videos."""
        self.log("Stripping audio from video clips...", "step")
        
        if self.dry_run:
            return {"success": True, "dry_run": True}
        
        try:
            strip_script = get_skill_path("media-utils", "video_strip_audio.py")
        except FileNotFoundError:
            # Fall back to FFmpeg directly
            self.log("Using FFmpeg directly for audio stripping", "info")
            return self._strip_audio_ffmpeg()
        
        # Get scene files
        scene_files = sorted(self.scenes_dir.glob("*.mp4"))
        if not scene_files:
            return {"success": False, "error": "No scene files found"}
        
        args = [
            "-i", *[str(f) for f in scene_files],
            "--output-dir", str(self.work_dir),
            "--prefix", "silent_"
        ]
        
        result = run_script(strip_script, args)
        
        if result["success"]:
            silent_files = list(self.work_dir.glob("silent_*.mp4"))
            return {
                "success": True,
                "files": [f.name for f in silent_files],
                "count": len(silent_files)
            }
        
        return result
    
    def _strip_audio_ffmpeg(self) -> dict:
        """Strip audio using FFmpeg directly."""
        scene_files = sorted(self.scenes_dir.glob("*.mp4"))
        stripped = []
        
        for scene in scene_files:
            output = self.work_dir / f"silent_{scene.name}"
            result = run_ffmpeg(["-i", str(scene), "-an", "-c:v", "copy", str(output)])
            
            if result["success"]:
                stripped.append(output.name)
            else:
                return {"success": False, "error": f"Failed to strip {scene.name}: {result['error']}"}
        
        return {"success": True, "files": stripped, "count": len(stripped)}
    
    def generate_voiceover(self) -> dict:
        """Generate voiceover using Gemini TTS."""
        self.log("Generating voiceover...", "step")
        
        if self.dry_run:
            return {"success": True, "dry_run": True}
        
        vo_config = self.config.get("voiceover", {})
        if not vo_config.get("text"):
            return {"success": False, "error": "No voiceover text in project.json"}
        
        try:
            tts_script = get_skill_path("voice-generation", "gemini_tts.py")
        except FileNotFoundError as e:
            return {"success": False, "error": str(e)}
        
        output_file = self.audio_dir / "voiceover.wav"
        
        args = [
            "--text", vo_config["text"],
            "--voice", vo_config.get("voice", "Charon"),
            "-o", str(output_file)
        ]
        
        if vo_config.get("style"):
            args.extend(["--style", vo_config["style"]])
        
        result = run_script(tts_script, args, timeout=300)
        
        if result["success"] and output_file.exists():
            return {"success": True, "file": str(output_file)}
        
        return result
    
    def generate_music(self) -> dict:
        """Generate background music using Lyria."""
        self.log("Generating background music...", "step")
        
        if self.dry_run:
            return {"success": True, "dry_run": True}
        
        music_config = self.config.get("music", {})
        if not music_config.get("prompt"):
            return {"success": False, "error": "No music prompt in project.json"}
        
        try:
            lyria_script = get_skill_path("music-generation", "lyria.py")
        except FileNotFoundError as e:
            return {"success": False, "error": str(e)}
        
        output_file = self.audio_dir / "background_music.wav"
        
        args = [
            "--prompt", music_config["prompt"],
            "--duration", str(music_config.get("duration", 30)),
            "-o", str(output_file)
        ]
        
        if music_config.get("bpm"):
            args.extend(["--bpm", str(music_config["bpm"])])
        if music_config.get("brightness"):
            args.extend(["--brightness", str(music_config["brightness"])])
        
        result = run_script(lyria_script, args, timeout=300)
        
        if result["success"] and output_file.exists():
            return {"success": True, "file": str(output_file)}
        
        return result
    
    def mix_audio(self) -> dict:
        """Mix voiceover with background music."""
        self.log("Mixing audio tracks...", "step")
        
        if self.dry_run:
            return {"success": True, "dry_run": True}
        
        voiceover_file = self.audio_dir / "voiceover.wav"
        music_file = self.audio_dir / "background_music.wav"
        output_file = self.audio_dir / "final_mix.mp3"
        
        # Check what files we have
        has_vo = voiceover_file.exists()
        has_music = music_file.exists()
        
        if not has_vo and not has_music:
            self.log("No audio files to mix", "warning")
            return {"success": True, "warning": "No audio files generated"}
        
        if has_vo and has_music:
            # Mix both
            try:
                mix_script = get_skill_path("media-utils", "audio_mix.py")
                
                assembly = self.config.get("assembly", {})
                args = [
                    "--voice", str(voiceover_file),
                    "--music", str(music_file),
                    "--music-volume", str(assembly.get("music_volume", 0.3)),
                    "-o", str(output_file)
                ]
                
                if assembly.get("fade_in"):
                    args.extend(["--fade-in", str(assembly["fade_in"])])
                if assembly.get("fade_out"):
                    args.extend(["--fade-out", str(assembly["fade_out"])])
                
                result = run_script(mix_script, args)
                
                if result["success"] and output_file.exists():
                    return {"success": True, "file": str(output_file)}
                
                # Fall back to FFmpeg
                return self._mix_audio_ffmpeg(voiceover_file, music_file, output_file)
                
            except FileNotFoundError:
                return self._mix_audio_ffmpeg(voiceover_file, music_file, output_file)
        
        elif has_vo:
            # Just copy voiceover
            shutil.copy(voiceover_file, output_file)
            return {"success": True, "file": str(output_file), "note": "voiceover only"}
        
        else:
            # Just copy music
            shutil.copy(music_file, output_file)
            return {"success": True, "file": str(output_file), "note": "music only"}
    
    def _mix_audio_ffmpeg(self, voice: Path, music: Path, output: Path) -> dict:
        """Mix audio using FFmpeg directly."""
        assembly = self.config.get("assembly", {})
        music_vol = assembly.get("music_volume", 0.3)
        
        filter_complex = (
            f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo[v];"
            f"[1:a]volume={music_vol}[m];"
            f"[v][m]amix=inputs=2:duration=longest[out]"
        )
        
        result = run_ffmpeg([
            "-i", str(voice),
            "-i", str(music),
            "-filter_complex", filter_complex,
            "-map", "[out]",
            "-c:a", "aac", "-b:a", "192k",
            str(output)
        ])
        
        if result["success"]:
            return {"success": True, "file": str(output)}
        return result
    
    def concatenate_videos(self) -> dict:
        """Concatenate all video clips."""
        self.log("Concatenating video clips...", "step")
        
        if self.dry_run:
            return {"success": True, "dry_run": True}
        
        # Determine which files to use
        if self.config["audio_strategy"] in ["custom", "silent"]:
            video_files = sorted(self.work_dir.glob("silent_*.mp4"))
        else:
            video_files = sorted(self.scenes_dir.glob("*.mp4"))
        
        if not video_files:
            return {"success": False, "error": "No video files to concatenate"}
        
        output_file = self.work_dir / "video_concatenated.mp4"
        
        # Try using video_concat.py
        try:
            concat_script = get_skill_path("media-utils", "video_concat.py")
            
            assembly = self.config.get("assembly", {})
            args = [
                "-i", *[str(f) for f in video_files],
                "-o", str(output_file)
            ]
            
            if assembly.get("transition"):
                args.extend(["--transition", assembly["transition"]])
            if assembly.get("transition_duration"):
                args.extend(["--duration", str(assembly["transition_duration"])])
            
            result = run_script(concat_script, args)
            
            if result["success"] and output_file.exists():
                return {"success": True, "file": str(output_file)}
            
        except FileNotFoundError:
            pass
        
        # Fall back to FFmpeg concat
        return self._concatenate_ffmpeg(video_files, output_file)
    
    def _concatenate_ffmpeg(self, video_files: list, output: Path) -> dict:
        """Concatenate using FFmpeg concat demuxer."""
        concat_list = self.work_dir / "concat_list.txt"
        
        with open(concat_list, "w") as f:
            for vf in video_files:
                f.write(f"file '{vf}'\n")
        
        result = run_ffmpeg([
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list),
            "-c", "copy",
            str(output)
        ])
        
        if result["success"]:
            return {"success": True, "file": str(output)}
        return result
    
    def merge_audio_video(self) -> dict:
        """Merge final audio with concatenated video."""
        self.log("Merging audio with video...", "step")
        
        if self.dry_run:
            return {"success": True, "dry_run": True}
        
        video_file = self.work_dir / "video_concatenated.mp4"
        audio_file = self.audio_dir / "final_mix.mp3"
        output_file = self.get_output_filename()
        
        if not video_file.exists():
            return {"success": False, "error": "Concatenated video not found"}
        
        if not audio_file.exists():
            # No audio to merge, just copy video
            shutil.copy(video_file, output_file)
            return {"success": True, "file": str(output_file), "note": "no audio"}
        
        # Try video_audio_merge.py
        try:
            merge_script = get_skill_path("media-utils", "video_audio_merge.py")
            
            args = [
                "--video", str(video_file),
                "--audio", str(audio_file),
                "-o", str(output_file)
            ]
            
            result = run_script(merge_script, args)
            
            if result["success"] and output_file.exists():
                return {"success": True, "file": str(output_file)}
                
        except FileNotFoundError:
            pass
        
        # Fall back to FFmpeg
        result = run_ffmpeg([
            "-i", str(video_file),
            "-i", str(audio_file),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(output_file)
        ])
        
        if result["success"]:
            return {"success": True, "file": str(output_file)}
        return result
    
    def get_output_filename(self) -> Path:
        """Generate output filename based on project name."""
        name = self.config["name"].lower().replace(" ", "_")
        name = "".join(c for c in name if c.isalnum() or c == "_")
        return self.output_dir / f"{name}_final.mp4"


def main():
    parser = argparse.ArgumentParser(
        description="Assemble a complete video from project.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Assemble a project (full pipeline)
  python assemble.py --project ~/Videos/my_project/
  
  # Skip generation (use existing scene files)
  python assemble.py --project ~/Videos/my_project/ --skip-generation
  
  # Dry run (show what would be done)
  python assemble.py --project ~/Videos/my_project/ --dry-run

Pipeline:
  1. Generate scenes (Veo 3.1)
  2. Strip audio (if custom audio strategy)
  3. Generate voiceover (Gemini TTS)
  4. Generate music (Lyria)
  5. Mix audio (voice + music)
  6. Concatenate video clips
  7. Merge audio with video
  8. Output final video
        """
    )
    
    parser.add_argument("--project", "-p", required=True,
                        help="Path to project folder (containing project.json)")
    parser.add_argument("--skip-generation", action="store_true",
                        help="Skip scene/audio generation, use existing files")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without executing")
    
    args = parser.parse_args()
    
    try:
        assembler = VideoAssembler(
            args.project,
            dry_run=args.dry_run,
            skip_generation=args.skip_generation
        )
        
        result = assembler.assemble()
        
        if result.get("success"):
            print("\n" + "=" * 60)
            print("🎬 VIDEO ASSEMBLY COMPLETE")
            print("=" * 60)
            print(f"  Project: {result['project']}")
            print(f"  Output:  {result['output_file']}")
            print(f"  Time:    {result['total_time']}s")
            print("=" * 60)
        else:
            print(f"\n❌ Assembly failed: {result.get('error', 'Unknown error')}")
            if result.get("steps"):
                print("\nCompleted steps:")
                for step in result["steps"]:
                    status = "✅" if step.get("success") else "❌"
                    print(f"  {status} {step['name']}")
            sys.exit(1)
            
    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
