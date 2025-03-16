import os
import tempfile
import shutil
import re
import subprocess
import glob
from pathlib import Path
from manim_code_generater import generate_and_validate

def clean_text_for_speech(text):
    cleaned = re.sub(r'\[SYNC:\s*\d+\]', '', text)
    
    cleaned = re.sub(r'\[PAUSE\]', '', cleaned)
    
    cleaned = re.sub(r'\\[a-zA-Z]+(?:\{[^}]*\})*', ' ', cleaned)
    
    cleaned = re.sub(r'[\\{}_\^]', ' ', cleaned)
    
    cleaned = re.sub(r'\$\$[^$]*\$\$', 'equation', cleaned) 
    cleaned = re.sub(r'\$[^$]*\$', 'symbol', cleaned)  
    
    cleaned = re.sub(r'[<>=+*/|]', ' ', cleaned)
    
    cleaned = re.sub(r'\[([^\]]+)\]', '', cleaned)
    
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    replacements = {
        'K_{\mu\nu}': 'K mu nu',
        '\dot{g}_{\mu\nu}': 'g dot mu nu',
        '\partial': 'partial',
        '\nabla': 'del',
        '\infty': 'infinity',
        '\int': 'integral',
        '\sum': 'sum',
        '\prod': 'product',
    }
    
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    
    return cleaned.strip()

def text_to_speech(text, output_file, voice_quality='high'):
    try:
        cleaned_text = clean_text_for_speech(text)
        
        output_file = str(output_file)
        
        try:
            from gtts import gTTS
            tts = gTTS(text=cleaned_text, lang='en', slow=False)
            tts.save(output_file)
            print(f"Audio generated with gTTS and saved to {output_file}")
            return True
        except ImportError:
            print("gTTS not available, trying alternative TTS...")
        
        try:
            import pyttsx3
            engine = pyttsx3.init()
            
            if voice_quality == 'high':
                voices = engine.getProperty('voices')
                if len(voices) > 1:
                    engine.setProperty('voice', voices[1].id)
                
                engine.setProperty('rate', 150)  
                engine.setProperty('volume', 0.9) 
            
            engine.save_to_file(cleaned_text, output_file)
            engine.runAndWait()
            print(f"Audio generated with pyttsx3 and saved to {output_file}")
            
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                return True
            else:
                print(f"Warning: Audio file was not created at {output_file}")
                return False
                
        except ImportError:
            print("pyttsx3 not available, trying system commands...")
        
        if os.name == 'posix':
            if os.path.exists('/usr/bin/say'):  
                subprocess.run(['say', '-o', output_file, cleaned_text], check=True)
                print(f"Audio generated with macOS 'say' command and saved to {output_file}")
                return True
            elif os.path.exists('/usr/bin/espeak'):  
                subprocess.run(['espeak', '-w', output_file, cleaned_text], check=True)
                print(f"Audio generated with 'espeak' command and saved to {output_file}")
                return True
        elif os.name == 'nt':
            try:
              
                ps_script = f'Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.SetOutputToWaveFile("{output_file}"); $synth.Speak("{cleaned_text}"); $synth.Dispose();'
                subprocess.run(['powershell', '-command', ps_script], check=True, capture_output=True)
                print(f"Audio generated with Windows speech synthesis and saved to {output_file}")
                return True
            except subprocess.SubprocessError:
                pass
                
        print("No TTS library or command found. Please install gtts or pyttsx3:")
        print("pip install gtts pyttsx3")
        return False
    
    except Exception as e:
        print(f"Error generating audio: {e}")
        return False

def combine_video_audio(video_path, audio_path, output_path):
    try:
        
        video_path = str(video_path)
        audio_path = str(audio_path)
        output_path = str(output_path)
        
        if not os.path.exists(video_path):
            print(f"Error: Video file does not exist: {video_path}")
            return False
            
        if not os.path.exists(audio_path):
            print(f"Error: Audio file does not exist: {audio_path}")
            return False
        
        print(f"Combining video ({video_path}) with audio ({audio_path})")
        
        try:
            subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
        except (FileNotFoundError, subprocess.SubprocessError):
            print("Error: ffmpeg not found. Please install ffmpeg and make sure it's in your PATH.")
            return False

        video_duration_cmd = ["ffmpeg", "-i", video_path, "-f", "null", "-"]
        result = subprocess.run(video_duration_cmd, stderr=subprocess.PIPE, text=True, check=False)
        duration_match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})", result.stderr)
        
        if duration_match:
            hours, minutes, seconds = map(float, duration_match.groups())
            video_duration = hours * 3600 + minutes * 60 + seconds
            print(f"Video duration: {video_duration:.2f} seconds")
            
            audio_duration_cmd = ["ffmpeg", "-i", audio_path, "-f", "null", "-"]
            audio_result = subprocess.run(audio_duration_cmd, stderr=subprocess.PIPE, text=True, check=False)
            audio_match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})", audio_result.stderr)
            
            if audio_match:
                hours, minutes, seconds = map(float, audio_match.groups())
                audio_duration = hours * 3600 + minutes * 60 + seconds
                print(f"Audio duration: {audio_duration:.2f} seconds")
                
                audio_input = audio_path
                if audio_duration < video_duration:
                    print("Audio is shorter than video, extending audio...")
                    loops = int(video_duration / audio_duration) + 1
                    temp_audio = output_path.replace(".mp4", "_temp.mp3")
                    loop_cmd = [
                        "ffmpeg", "-i", audio_path, 
                        "-filter_complex", f"aloop=loop={loops}:size=32767", 
                        "-t", str(video_duration), temp_audio
                    ]
                    subprocess.run(loop_cmd, check=True)
                    audio_input = temp_audio
                
                cmd = [
                    "ffmpeg", 
                    "-i", video_path, 
                    "-i", audio_input, 
                    "-map", "0:v", 
                    "-map", "1:a", 
                    "-c:v", "copy", 
                    "-shortest",
                    output_path
                ]
                
                subprocess.run(cmd, check=True)
                print(f"Video with audio saved to {output_path}")
                
                if audio_input != audio_path and os.path.exists(audio_input):
                    os.remove(audio_input)
                
                return True
        
        print("Combining video and audio directly...")
        cmd = [
            "ffmpeg", 
            "-i", video_path, 
            "-i", audio_path, 
            "-c:v", "copy", 
            "-c:a", "aac", 
            "-shortest", 
            output_path
        ]
        subprocess.run(cmd, check=True)
        print(f"Video with audio saved to {output_path}")
        return True
        
    except subprocess.SubprocessError as e:
        print(f"Error combining video and audio: {e}")
        return False

def adjust_video_speed(video_path, output_path, speed_factor=0.75):
    try:
        slowdown_factor = 1.0 / speed_factor
        cmd = [
            "ffmpeg", "-i", video_path,
            "-filter:v", f"setpts={slowdown_factor}*PTS",
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            output_path
        ]
        subprocess.run(cmd, check=True)
        print(f"Video speed adjusted (slowed down by factor: {slowdown_factor:.2f}) and saved to {output_path}")
        return True
    except subprocess.SubprocessError as e:
        print(f"Error adjusting video speed: {e}")
        return False

def generate_educational_video(prompt, with_audio=True, sync_narration=False, voice_quality='high', adjust_speed=False):
    print(f"Generating Manim code for: {prompt}")
    
    manim_prompt = f"An educational video about: {prompt}."
    
    import inspect
    sig = inspect.signature(generate_and_validate)
    
    if 'with_audio' in sig.parameters:
        if with_audio:
            if 'sync_narration' in sig.parameters and sync_narration:
                manim_code, narration_script = generate_and_validate(
                    manim_prompt, "python", with_audio=True, sync_narration=True
                )
            else:
                manim_code, narration_script = generate_and_validate(
                    manim_prompt, "python", with_audio=True
                )
        else:
            manim_code = generate_and_validate(manim_prompt, "python", with_audio=False)
            narration_script = None
    else:
        manim_code = generate_and_validate(manim_prompt, "python")
        narration_script = None
        
        if with_audio:
            try:
                if sync_narration and hasattr(manim_code_generater, 'generate_synced_narration'):
                    from manim_code_generater import generate_synced_narration
                    narration_script = generate_synced_narration(manim_code, prompt)
                    print("\nSynchronized narration script generated separately.")
                else:
                    from manim_code_generater import generate_narration_script
                    narration_script = generate_narration_script(prompt)
                    print("\nNarration script generated separately.")
            except ImportError:
                print("\nWarning: Audio narration requested but narration script generation function not available.")
                narration_script = f"This is an educational video about {prompt}."
    
    print("\nManim code generated:")
    print(manim_code)
    
    if sync_narration and narration_script and "[SYNC:" in narration_script:
        print("\nProcessing synchronized narration script...")
        processed_script = process_synced_narration(narration_script)
    else:
        processed_script = narration_script
    
    with tempfile.TemporaryDirectory() as temp_dir:
        script_path = os.path.join(temp_dir, "manim_script.py")
        with open(script_path, "w", encoding='utf-8') as f:
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
                
                if (video_files):
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
        
        if not os.path.exists(output_video):
            print(f"ERROR: Expected output video not found at {output_video}")
            return None
            
        if with_audio and processed_script:
            print("Generating audio narration...")
            audio_dir = os.path.abspath(str(output_dir))
            audio_path = os.path.join(audio_dir, f"{output_id}_audio.mp3")
            
            if text_to_speech(processed_script, audio_path, voice_quality=voice_quality):
                print("Audio narration generated successfully")
                
                if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                    print(f"Audio file confirmed at {audio_path}")
                    
                    output_video_abs = os.path.abspath(str(output_video))
                    
                    if adjust_speed:
                        print("Adjusting video speed to better match narration...")
                        slowed_video_path = os.path.join(audio_dir, f"{output_id}_slowed.mp4")
                        
                        if adjust_video_speed(output_video_abs, slowed_video_path, speed_factor=0.75):
                            print("Video speed adjusted successfully")
                            output_video_abs = slowed_video_path
                    
                    output_with_audio = os.path.join(audio_dir, f"{output_id}_with_audio.mp4")
                    
                    if sync_narration and "[SYNC:" in narration_script:
                        print("Using advanced audio-video synchronization...")
                        try:
                            from sync_audio_video import synchronize_audio_with_video
                            script_file = os.path.join(audio_dir, f"{output_id}_narration.txt")
                            with open(script_file, 'w', encoding='utf-8') as f:
                                f.write(narration_script)
                            
                            if synchronize_audio_with_video(output_video_abs, script_file, output_with_audio):
                                print(f"Synchronized video created at {output_with_audio}")
                                return output_with_audio
                        except ImportError:
                            print("Advanced synchronization not available, falling back to standard method")
                            pass
                    
                    print("Combining video and audio...")
                    if combine_video_audio(output_video_abs, audio_path, output_with_audio):
                        print(f"Video with audio created at {output_with_audio}")
                        return output_with_audio
                else:
                    print(f"Error: Audio file not found at {audio_path}")
            
            print("Audio processing failed or skipped, returning video without audio")
            
        return str(output_video)

def process_synced_narration(narration_script):
    sections = re.findall(r'\[SYNC:\s*(\d+)\]\s*(.*?)(?=\[SYNC:|$)', narration_script, re.DOTALL)
    
    if not sections:
        print("Warning: Could not parse synchronized narration markers. Using script as is.")
        return clean_text_for_speech(narration_script)
    
    if len(sections) > 5:
        print(f"Warning: Found {len(sections)} sync points, which is more than recommended. Using only the first 5.")
        sections = sections[:5]
    
    processed_sections = []
    for timestamp, content in sections:
        cleaned_content = clean_text_for_speech(content)
        
        words = cleaned_content.split()
        if len(words) > 20:
            print(f"Warning: Section at timestamp {timestamp}s has {len(words)} words, truncating to 20.")
            cleaned_content = ' '.join(words[:20])
        
        processed_sections.append(cleaned_content)
    
    processed_script = ". ".join(processed_sections)
    
    total_words = len(processed_script.split())
    if total_words > 75:
        print(f"Warning: Total narration has {total_words} words, which exceeds the recommended maximum of 75.")
    
    return processed_script

if __name__ == "__main__":
    prompt = input("Enter your educational video prompt: ")
    with_audio = input("Generate audio narration? (y/n, default: y): ").lower() != 'n'
    
    voice_quality = 'medium'
    sync_narration = True  
    adjust_speed = False  
    
    if with_audio:
        sync_narration_input = input("Synchronize narration with animation? (y/n, default: y): ").lower()
        if sync_narration_input == 'n':
            sync_narration = False
            
        voice_quality = input("Voice quality (low/medium/high, default: medium): ").lower() or 'medium'
        if voice_quality not in ['low', 'medium', 'high']:
            voice_quality = 'medium'
        
        adjust_speed = input("Keep video at normal speed? (y/n, default: y): ").lower() == 'n'
    
    video_path = generate_educational_video(prompt, with_audio=with_audio, 
                                         sync_narration=sync_narration,
                                         voice_quality=voice_quality,
                                         adjust_speed=adjust_speed)
    
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
