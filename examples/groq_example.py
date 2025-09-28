#!/usr/bin/env python3
"""Example showing how to use Capibara with Groq for code generation."""

import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from capibara.core.service import CapibaraCore
from capibara.core.models import GenerationRequest


def main():
    """Main function demonstrating Groq integration."""
    print("🚀 Capibara + Groq Code Generation Example")
    print("=" * 60)
    
    # Check for API key
    if not os.environ.get("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY not found!")
        print("\nTo use this example with Groq:")
        print("1. Get your API key from https://console.groq.com/")
        print("2. Set the environment variable:")
        print("   export GROQ_API_KEY='your-api-key-here'")
        print("3. Run this script again")
        print("\n🔄 Running with MockLLM for demonstration...")
    else:
        print("✅ GROQ_API_KEY found - using Groq for code generation")
    
    # Initialize Capibara
    core = CapibaraCore(use_groq=bool(os.environ.get("GROQ_API_KEY")))
    
    # Example prompts for different use cases
    examples = [
        {
            "name": "Weather API Script",
            "prompt": "Create a script that fetches current weather data from OpenWeatherMap API for a given city",
            "context": {
                "city": "London",
                "api_key": "your_openweather_api_key",
                "units": "metric"
            }
        },
        {
            "name": "CSV Data Processor",
            "prompt": "Generate a script that reads a CSV file, calculates basic statistics (mean, median, mode) for numeric columns, and outputs results to JSON",
            "context": {
                "input_file": "sales_data.csv",
                "output_file": "statistics.json",
                "numeric_columns": ["price", "quantity", "revenue"]
            }
        },
        {
            "name": "Image Resizer",
            "prompt": "Create a script that resizes images in a directory to a specified width and height, maintaining aspect ratio",
            "context": {
                "input_directory": "./images",
                "output_directory": "./resized",
                "max_width": 800,
                "max_height": 600,
                "quality": 85
            }
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n📝 Example {i}: {example['name']}")
        print("-" * 40)
        print(f"Prompt: {example['prompt']}")
        print(f"Context: {json.dumps(example['context'], indent=2)}")
        
        try:
            # Create request
            request = GenerationRequest(
                prompt=example['prompt'],
                context=example['context'],
                language="python"
            )
            
            # Generate script
            print("\n🤖 Generating script...")
            response = core.generate_script(request)
            
            if response.status == "ok":
                print("✅ Script generated successfully!")
                print(f"📄 Length: {len(response.script)} chars")
                print(f"📦 Dependencies: {response.requirements}")
                print(f"🔒 Network: {response.manifest.allow.get('network', False)}")
                
                # Save generated files
                output_dir = Path(f"generated_example_{i}")
                output_dir.mkdir(exist_ok=True)
                
                with open(output_dir / "script.py", "w") as f:
                    f.write(response.script)
                with open(output_dir / "requirements.txt", "w") as f:
                    f.write(response.requirements)
                with open(output_dir / "README.md", "w") as f:
                    f.write(response.readme)
                
                print(f"💾 Files saved to: {output_dir}/")
                
                # Show script preview
                print("\n📋 Script Preview:")
                lines = response.script.split('\n')[:15]
                for line in lines:
                    print(f"  {line}")
                if len(response.script.split('\n')) > 15:
                    print("  ...")
                
            else:
                print(f"❌ Generation failed: {response.error}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 All examples completed!")
    print("\n💡 Next steps:")
    print("1. Set GROQ_API_KEY to use real AI code generation")
    print("2. Run the generated scripts to test them")
    print("3. Customize the prompts for your specific needs")


if __name__ == "__main__":
    main()
