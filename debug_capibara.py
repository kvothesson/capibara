"""Debug script for Capibara."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    print("1. Testing imports...")
    from capibara import Capibara
    print("✓ Imports successful")
    
    print("\n2. Testing Capibara initialization...")
    cb = Capibara()
    print("✓ Capibara initialized")
    
    print("\n3. Testing simple script generation...")
    result = cb.run(
        "Create a simple script that adds two numbers",
        context={"a": 5, "b": 3}
    )
    
    print(f"Result type: {type(result)}")
    print(f"Result status: {result.status}")
    print(f"Result output: {result.output}")
    print(f"Result raw: {result.raw}")
    
    if hasattr(result, '_data'):
        print(f"Result _data: {result._data}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
