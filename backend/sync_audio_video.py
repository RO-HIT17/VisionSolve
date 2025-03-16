import re
import os
import subprocess
import tempfile
from pathlib import Path

def extract_sync_points(narration_script):
    sync_points = []
    sections = re.findall(r'\[SYNC:\s*(\d+)\]\s*(.*?)(?=\[SYNC:|$)', narration_script, re.DOTALL)
    
    for timestamp, text in sections:
        try:
            from test_generate_video import clean_text_for_speech
            clean_text = clean_text_for_speech(text.strip())
        except ImportError:
            clean_text = re.sub(r'\[SYNC:\s*\d+\]', '', text.strip())
            clean_text = re.sub(r'\[PAUSE\]', '', clean_text)
            clean_text = re.sub(r'\[([^\]]+)\]', '', clean_text)
            clean_text = re.sub(r'\\[a-zA-Z]+(?:\{[^}]*\})*', '', clean_text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        sync_points.append({
            'timestamp': int(timestamp),
            'text': clean_text
        })
    
    return sync_points

def create_segmented_audio(narration_script, output_dir):
    from manim_code_generater import generate_synced_narration
    from test_generate_video import text_to_speech
    
    sync_points = extract_sync_points(narration_script)
    
    if len(sync_points) > 6:  
        print(f"Warning: Limiting narration from {len(sync_points)} to 5 sync points for brevity")
        if len(sync_points) >= 4:
            first = sync_points[0]
            last = sync_points[-1]
            
            middle_indices = []
            if len(sync_points) >= 6:
                segment_size = (len(sync_points) - 2) / 3
                for i in range(1, 4):
                    middle_indices.append(int(i * segment_size))
            else:
                middle_indices = [len(sync_points) // 3, 2 * len(sync_points) // 3]
            
            middle_points = [sync_points[i] for i in middle_indices]
            
            sync_points = [first] + middle_points + [last]
        else:
            pass
    
    audio_segments = []
    
    for i, point in enumerate(sync_points):
        segment_file = os.path.join(output_dir, f"segment_{i:03d}.mp3")
        
        text = point['text']
        words = text.split()
        if len(words) > 25:  
            print(f"Truncating sync point {i} from {len(words)} words to 25 words")
            text = ' '.join(words[:25])
            point['text'] = text
            
        if text_to_speech(text, segment_file):
            audio_segments.append({
                'timestamp': point['timestamp'],
                'file': segment_file,
                'text': text
            })
    
    return audio_segments

def create_silence_file(duration_sec, output_file):
    try:
        cmd = [
            "ffmpeg", "-f", "lavfi", "-i", 
            f"anullsrc=r=44100:cl=stereo", "-t", 
            str(duration_sec), "-q:a", "0", "-c:a", "libmp3lame",
            output_file
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.SubprocessError as e:
        print(f"Error creating silence file: {e}")
        return False

def analyze_video_pacing(video_path):
    try:
        cmd = [
            "ffmpeg", "-i", video_path, 
            "-vf", "select=gt(scene\\,0.2),metadata=print:file=-", 
            "-f", "null", "-"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        scene_changes = []
        for line in result.stderr.split('\n'):
            if 'pts_time' in line:
                match = re.search(r'pts_time:(\d+\.\d+)', line)
                if match:
                    scene_changes.append(float(match.group(1)))
        
        if len(scene_changes) >= 2:
            durations = [scene_changes[i+1] - scene_changes[i] for i in range(len(scene_changes)-1)]
            avg_scene_duration = sum(durations) / len(durations)
        else:
            avg_scene_duration = 3.0 
            
        return {
            'scene_changes': scene_changes,
            'avg_scene_duration': avg_scene_duration
        }
    except Exception as e:
        print(f"Error analyzing video pacing: {e}")
        return {'scene_changes': [], 'avg_scene_duration': 3.0}

def assemble_synchronized_audio(audio_segments, total_duration, output_file, video_analysis=None):
    with tempfile.TemporaryDirectory() as temp_dir:
        concat_file = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_file, 'w') as f:
            last_end_time = 0
            for i, segment in enumerate(audio_segments):
                current_time = segment['timestamp']
                
                if video_analysis and video_analysis['scene_changes']:
                    closest_scene = min(video_analysis['scene_changes'], 
                                       key=lambda x: abs(x - current_time))
                    if abs(closest_scene - current_time) < 1.5:
                        current_time = closest_scene
                
                if current_time > last_end_time:
                    silence_duration = current_time - last_end_time
                    silence_file = os.path.join(temp_dir, f"silence_{i:03d}.mp3")
                    if create_silence_file(silence_duration, silence_file):
                        f.write(f"file '{os.path.abspath(silence_file)}'\n")
                
                f.write(f"file '{os.path.abspath(segment['file'])}'\n")
                
                if 'text' in segment:
                    word_count = len(segment['text'].split())
                else:
                    try:
                        audio_info_cmd = ["ffprobe", "-i", segment['file'], "-show_format", "-v", "quiet", "-print_format", "json"]
                        audio_info = subprocess.run(audio_info_cmd, capture_output=True, text=True)
                        import json
                        duration = float(json.loads(audio_info.stdout)["format"]["duration"])
                        word_count = int(duration * 2.5)
                    except:
                        word_count = 10  
                
                segment_duration = max(1.5, word_count / 2.5)  
                last_end_time = current_time + segment_duration
        
        if total_duration > last_end_time:
            final_silence = os.path.join(temp_dir, "final_silence.mp3")
            if create_silence_file(total_duration - last_end_time, final_silence):
                with open(concat_file, 'a') as f:
                    f.write(f"file '{os.path.abspath(final_silence)}'\n")
        
        try:
            cmd = [
                "ffmpeg", "-f", "concat", "-safe", "0",
                "-i", concat_file, "-c:a", "libmp3lame",
                "-q:a", "0", output_file
            ]
            subprocess.run(cmd, check=True)
            return True
        except subprocess.SubprocessError as e:
            print(f"Error assembling audio: {e}")
            return False

def synchronize_audio_with_video(video_path, narration_script_path, output_path):
    if isinstance(narration_script_path, str) and os.path.exists(narration_script_path):
        with open(narration_script_path, 'r', encoding='utf-8') as f:
            narration_script = f.read()
    else:
        narration_script = narration_script_path 
        
    with tempfile.TemporaryDirectory() as temp_dir:
        video_analysis = analyze_video_pacing(video_path)
        duration_cmd = ["ffmpeg", "-i", video_path, "-f", "null", "-"]
        result = subprocess.run(duration_cmd, stderr=subprocess.PIPE, text=True, check=False)
        duration_match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})", result.stderr)
        
        if duration_match:
            hours, minutes, seconds = map(float, duration_match.groups())
            video_duration = hours * 3600 + minutes * 60 + seconds
            
            audio_segments = create_segmented_audio(narration_script, temp_dir)
            if not audio_segments:
                print("Error: Failed to create audio segments")
                return False
            
            synchronized_audio = os.path.join(temp_dir, "synchronized_audio.mp3")
            if not assemble_synchronized_audio(audio_segments, video_duration, synchronized_audio, video_analysis):
                print("Error: Failed to assemble synchronized audio")
                return False
            
            audio_duration_cmd = ["ffmpeg", "-i", synchronized_audio, "-f", "null", "-"]
            audio_result = subprocess.run(audio_duration_cmd, stderr=subprocess.PIPE, text=True, check=False)
            audio_match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})", audio_result.stderr)
            
            if audio_match:
                hours, minutes, seconds = map(float, audio_match.groups())
                audio_duration = hours * 3600 + minutes * 60 + seconds
                
                print(f"Video duration: {video_duration:.1f}s, Audio duration: {audio_duration:.1f}s")
                
                try:
                    cmd = [
                        "ffmpeg", "-i", video_path, "-i", synchronized_audio,
                        "-map", "0:v", "-map", "1:a", 
                        "-c:v", "copy", "-c:a", "aac", 
                        "-shortest", output_path
                    ]
                    subprocess.run(cmd, check=True)
                    print(f"Synchronized video created at {output_path}")
                    return True
                except subprocess.SubprocessError as e:
                    print(f"Error combining video with synchronized audio: {e}")
                    return False
            else:
                print("Error: Could not determine audio duration")
                return False
        else:
            print("Error: Could not determine video duration")
            return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Synchronize narration with video")
    parser.add_argument("video", help="Path to the video file")
    parser.add_argument("narration", help="Path to the narration script file")
    parser.add_argument("output", help="Path for the output video file")
    
    args = parser.parse_args()
    
    with open(args.narration, 'r') as f:
        narration_script = f.read()
    
    synchronize_audio_with_video(args.video, narration_script, args.output)
