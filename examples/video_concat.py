"""Example: Video concatenation with Capibara."""

from capibara import Capibara

def main():
    # Initialize Capibara
    cb = Capibara()
    
    # Example 1: Concatenate videos
    print("=== Video Concatenation Example ===")
    
    result = cb.run(
        "Concatenate these videos with moviepy at 24fps",
        context={
            "inputs": ["intro.mp4", "clip.mp4"], 
            "output": "final.mp4",
            "fps": 24
        }
    )
    
    print(f"Status: {result.status}")
    print(f"Artifacts: {result.artifacts}")
    if result.status == "ok":
        print(f"FPS: {result.fps}")
        print(f"Duration: {result.duration}")
        print(f"Raw output: {result.raw}")

if __name__ == "__main__":
    main()
