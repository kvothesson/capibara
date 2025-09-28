"""Test script for Capibara functionality."""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from capibara import Capibara

def test_basic_functionality():
    """Test basic Capibara functionality."""
    print("=== Testing Capibara Basic Functionality ===")
    
    # Initialize Capibara
    cb = Capibara()
    
    # Test 1: Simple script generation
    print("\n1. Testing simple script generation...")
    result = cb.run(
        "Create a simple script that adds two numbers",
        context={"a": 5, "b": 3}
    )
    
    print(f"Status: {result.status}")
    if result.status == "ok":
        print("✓ Simple script generation works")
    else:
        print(f"✗ Simple script generation failed: {result.output.get('message', 'Unknown error')}")
    
    # Test 2: Video concatenation template
    print("\n2. Testing video concatenation template...")
    result = cb.run(
        "Concatenate these videos with moviepy at 24fps",
        context={
            "inputs": ["intro.mp4", "clip.mp4"], 
            "output": "final.mp4",
            "fps": 24
        }
    )
    
    print(f"Status: {result.status}")
    if result.status == "ok":
        print("✓ Video concatenation template works")
        print(f"Expected outputs: {result.output}")
    else:
        print(f"✗ Video concatenation template failed: {result.output.get('message', 'Unknown error')}")
    
    # Test 3: MercadoLibre API template
    print("\n3. Testing MercadoLibre API template...")
    result = cb.run(
        "Use MercadoLibre API to fetch price and description",
        context={"item_id": "MLA123456789"},
        select=["title", "price"]
    )
    
    print(f"Status: {result.status}")
    if result.status == "ok":
        print("✓ MercadoLibre API template works")
        print(f"Selected fields: {result.output}")
    else:
        print(f"✗ MercadoLibre API template failed: {result.output.get('message', 'Unknown error')}")
    
    # Test 4: List cached scripts
    print("\n4. Testing script listing...")
    scripts = cb.list_scripts()
    print(f"Found {len(scripts)} cached scripts")
    for script in scripts:
        print(f"  - {script['fingerprint'][:12]}... ({script['language']})")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    test_basic_functionality()
