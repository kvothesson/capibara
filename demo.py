"""Demo script showing Capibara capabilities."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from capibara import Capibara

def main():
    print("🦫 Capibara Demo - From idea to executable code, in one step")
    print("=" * 60)
    
    # Initialize Capibara
    cb = Capibara()
    
    # Demo 1: Simple calculation
    print("\n1. Simple Calculation Script")
    print("-" * 30)
    result = cb.run(
        "Create a script that calculates the area of a rectangle",
        context={"width": 10, "height": 5}
    )
    
    if result.status == "ok":
        print("✓ Script generated and executed successfully")
        print(f"  Raw output: {result.raw}")
    else:
        print(f"✗ Error: {result.output.get('message', 'Unknown error')}")
    
    # Demo 2: List cached scripts
    print("\n2. Cached Scripts")
    print("-" * 30)
    scripts = cb.list_scripts()
    print(f"Found {len(scripts)} cached scripts:")
    for script in scripts:
        print(f"  - {script['fingerprint'][:12]}... ({script['language']}) - {len(script['deps'])} deps")
    
    # Demo 3: Video processing template (without execution)
    print("\n3. Video Processing Template")
    print("-" * 30)
    result = cb.run(
        "Concatenate these videos with moviepy at 24fps",
        context={
            "inputs": ["intro.mp4", "clip.mp4"], 
            "output": "final.mp4",
            "fps": 24
        }
    )
    
    if result.status == "ok":
        print("✓ Video processing script generated")
        print(f"  Expected artifacts: {result.artifacts}")
        print(f"  Expected outputs: {result.output}")
    else:
        print(f"✗ Error: {result.output.get('message', 'Unknown error')}")
        print(f"  Raw error: {result.raw}")
    
    # Demo 4: API integration template (without execution)
    print("\n4. API Integration Template")
    print("-" * 30)
    result = cb.run(
        "Use MercadoLibre API to fetch price and description",
        context={"item_id": "MLA123456789"},
        select=["title", "price"]
    )
    
    if result.status == "ok":
        print("✓ API integration script generated")
        print(f"  Selected fields: {result.output}")
    else:
        print(f"✗ Error: {result.output.get('message', 'Unknown error')}")
        print(f"  Raw error: {result.raw}")
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed! Check .capibara/scripts/ for generated artifacts.")
    print("\nTo use the CLI:")
    print("  capibara run 'Your prompt here' --context '{\"key\": \"value\"}'")
    print("  capibara list")
    print("  capibara show <fingerprint>")

if __name__ == "__main__":
    main()
