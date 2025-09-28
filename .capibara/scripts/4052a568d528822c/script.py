# --- CAPIBARA ---
# language: python
# entry: script.py
# deps: moviepy==1.0.3
# network: false
# template_version: 1.0.0
# --- /CAPIBARA ---

import json
import sys
from pathlib import Path
from moviepy.editor import VideoFileClip, concatenate_videoclips

def main():
    # Parse context from command line
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "No context provided"}))
        return
    
    try:
        context = json.loads(sys.argv[1])
        inputs = context.get("inputs", [])
        output = context.get("output", "output.mp4")
        fps = context.get("fps", 24)
        
        if not inputs:
            print(json.dumps({"status": "error", "message": "No input videos provided"}))
            return
        
        # Load video clips
        clips = []
        for input_file in inputs:
            if not Path(input_file).exists():
                print(json.dumps({"status": "error", "message": f"File not found: {input_file}"}))
                return
            clips.append(VideoFileClip(input_file))
        
        # Concatenate videos
        final_clip = concatenate_videoclips(clips)
        final_clip = final_clip.set_fps(fps)
        
        # Write output
        final_clip.write_videofile(output, fps=fps)
        final_clip.close()
        
        # Return results
        result = {
            "status": "ok",
            "artifacts": [output],
            "output": {
                "fps": fps,
                "duration": final_clip.duration
            },
            "raw": {
                "input_files": inputs,
                "output_file": output,
                "total_duration": final_clip.duration
            }
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main()
