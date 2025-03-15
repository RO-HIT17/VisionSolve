import os
import tempfile
import subprocess
import uuid
import re
import sys
import shutil

class ManimRunner:
    
    def __init__(self, output_dir="media/videos"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def clean_manim_code(self, code):
        code = re.sub(r'^```python\s*', '', code, flags=re.MULTILINE)
        code = re.sub(r'^```\s*$', '', code, flags=re.MULTILINE)
        
        if "from manim import *" not in code and "import manim" not in code:
            code = "from manim import *\n\n" + code
        code = re.sub(r'^import \*\s*$', 'from manim import *', code, flags=re.MULTILINE)

        return code
    
    def run_manim_code(self, manim_code):
        manim_code = self.clean_manim_code(manim_code)
            
        temp_dir = tempfile.mkdtemp()
        file_id = str(uuid.uuid4())[:8]
        script_path = os.path.join(temp_dir, f"manim_script_{file_id}.py")
        
        scene_class = None
        class_pattern = re.compile(r'class\s+(\w+)\s*\(\s*Scene\s*\)')
        match = class_pattern.search(manim_code)
        if match:
            scene_class = match.group(1)
        
        if not scene_class:
            print("ERROR: Could not find Scene class in the generated code")
            print("Generated code:")
            print(manim_code)
            return None
        
        print(f"Detected scene class: {scene_class}")
            
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(manim_code)
        
        try:
            cmd = [
                sys.executable, "-m", "manim",
                script_path, scene_class,
                "-o", file_id,
                "--media_dir", self.output_dir,
                "-q", "m"
            ]
            
            print(f"Executing: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=os.path.dirname(script_path)
            )
            
            if result.returncode != 0:
                print(f"Manim execution error (code {result.returncode}):")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                return None
            
            print("Manim execution stdout:")
            print(result.stdout)
                
            video_path = None
            for line in result.stdout.splitlines():
                if "File ready at" in line and ".mp4" in line:
                    path_match = re.search(r"'([^']+\.mp4)'", line)
                    if path_match:
                        video_path = path_match.group(1)
                        break
            
            if video_path and os.path.exists(video_path):
                print(f"Video file found at: {video_path}")
                return video_path
            
            search_patterns = [
                os.path.join(self.output_dir, "**", f"{scene_class}.mp4"),
                os.path.join(self.output_dir, "**", f"{file_id}*.mp4"),
                os.path.join("media", "videos", "**", f"{scene_class}.mp4")
            ]
            
            for pattern in search_patterns:
                import glob
                matching_files = glob.glob(pattern, recursive=True)
                if matching_files:
                    video_path = matching_files[0]
                    print(f"Video file found through search: {video_path}")
                    return video_path
                    
            print("ERROR: Could not find generated video file")
            print(f"Standard output: {result.stdout}")
            return None
            
        except Exception as e:
            print(f"Error running Manim: {str(e)}")
            return None
