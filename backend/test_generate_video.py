import os
import tempfile
import shutil
import re
import subprocess
import glob
from pathlib import Path
from manim_code_generated import generate_and_validate

def generate_educational_video(prompt):
    
    print(f"Generating Manim code for: {prompt}")
    
    
    manim_prompt = f"An educational video about: {prompt}."
    manim_code = generate_and_validate(manim_prompt, "python")
    
    print("\nManim code generated:")
    print(manim_code)
    
    
    with tempfile.TemporaryDirectory() as temp_dir:
        
        script_path = os.path.join(temp_dir, "manim_script.py")
        with open(script_path, "w" , encoding='utf-8') as f:
            f.write(manim_code)
        
        
        scene_class_match = re.search(r"class\s+(\w+)\s*\(\s*Scene\s*\)", manim_code)
        if not scene_class_match:
            print("Could not detect a Scene class in the generated code.")
            return None
        
        scene_class = scene_class_match.group(1)
        print(f"Detected scene class: {scene_class}")
        
        
        import hashlib
        output_id = hashlib.md5(prompt.encode()).hexdigest()[:8]
        
        
        output_dir = Path("videos")
        output_dir.mkdir(exist_ok=True)
        output_video = output_dir / f"{output_id}.mp4"
        
        
        media_dir = os.path.join(temp_dir, "media")
        os.makedirs(media_dir, exist_ok=True)
        
       
        print("Generating video, please wait...")
        cmd = [
            "python", "-m", "manim", 
            script_path, 
            scene_class,
            "-o", output_id,
            "--media_dir", media_dir,
            "-q", "m"  
        ]
        
        try:
            process = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("Manim execution stdout:")
            print(process.stdout)
            
            
            file_ready_match = re.search(r"File ready at\s+'(.+?\.mp4)'", process.stdout)
            
            if file_ready_match:
                generated_video_path = file_ready_match.group(1)
                print(f"Found video path in output: {generated_video_path}")
            else:
                
                print("Searching for the video file...")
                video_pattern = os.path.join(media_dir, "**", f"*{output_id}.mp4")
                video_files = glob.glob(video_pattern, recursive=True)
                
                if video_files:
                    generated_video_path = video_files[0]
                    print(f"Found video by searching: {generated_video_path}")
                else:
                    
                    video_files = glob.glob(os.path.join(media_dir, "**", "*.mp4"), recursive=True)
                    if video_files:
                        
                        video_files.sort(key=os.path.getctime, reverse=True)
                        generated_video_path = video_files[0]
                        print(f"Found most recent video: {generated_video_path}")
                    else:
                        print("ERROR: Could not find any generated video files")
                        return None
            
            if os.path.exists(generated_video_path):
                
                try:
                    shutil.copy(generated_video_path, output_video)
                    print(f"\nVideo successfully generated and saved to: {output_video}")
                    return str(output_video)
                except Exception as e:
                    print(f"Error copying video file: {e}")
                    return None
            else:
                print(f"ERROR: Found video path '{generated_video_path}' but file does not exist")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"Manim execution failed with return code {e.returncode}")
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            print("\nFailed to generate video")
            print("Make sure FFmpeg and LaTeX (optional) are properly installed.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return None

if __name__ == "__main__":
    prompt = input("Enter your educational video prompt: ")
    video_path = generate_educational_video(prompt)
    
    if video_path:

        try:
            if os.name == 'nt':  
                os.startfile(video_path)
            elif os.name == 'posix':  
                import subprocess
                subprocess.call(('open' if os.uname().sysname == 'Darwin' else 'xdg-open', video_path))
        except Exception as e:
            print(f"Could not automatically open the video: {e}")
            print(f"Please open the video manually at: {video_path}")
    else:
        print("Video generation failed.")
