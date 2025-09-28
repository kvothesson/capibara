# Video Concatenation Script

This script concatenates multiple video files using MoviePy.

## Usage

```bash
python script.py '{"inputs": ["video1.mp4", "video2.mp4"], "output": "final.mp4", "fps": 24}'
```

## Parameters

- `inputs`: List of input video file paths
- `output`: Output video file path (default: output.mp4)
- `fps`: Target frame rate (default: 24)

## Output

The script will create a concatenated video file and return JSON with:
- `artifacts`: List of created files
- `fps`: Actual frame rate used
- `duration`: Total duration of the output video
