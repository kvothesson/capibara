"""Capibara Core service implementation."""

import hashlib
import json
from datetime import datetime
from typing import Dict, Any

from .models import GenerationRequest, GenerationResponse, ScriptManifest, UpdateRequest, UpdateResponse


class MockLLM:
    """Mock LLM service for development and testing."""
    
    def __init__(self):
        self.templates = {
            "video_concat": {
                "script": '''# --- CAPIBARA ---
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
''',
                "requirements": "moviepy==1.0.3",
                "readme": """# Video Concatenation Script

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
""",
                "outputs": {
                    "artifacts": "list[str]",
                    "fps": "int",
                    "duration": "float"
                }
            },
            "mercadolibre_api": {
                "script": '''# --- CAPIBARA ---
# language: python
# entry: script.py
# deps: requests==2.31.0
# network: true
# template_version: 1.0.0
# --- /CAPIBARA ---

import json
import sys
import requests
from typing import Dict, Any

def main():
    # Parse context from command line
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "No context provided"}))
        return
    
    try:
        context = json.loads(sys.argv[1])
        item_id = context.get("item_id")
        
        if not item_id:
            print(json.dumps({"status": "error", "message": "No item_id provided"}))
            return
        
        # Fetch item data from MercadoLibre API
        url = f"https://api.mercadolibre.com/items/{item_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant fields
        result = {
            "status": "ok",
            "artifacts": [],
            "output": {
                "title": data.get("title"),
                "price": data.get("price"),
                "currency": data.get("currency_id"),
                "condition": data.get("condition"),
                "available_quantity": data.get("available_quantity"),
                "sold_quantity": data.get("sold_quantity")
            },
            "raw": data
        }
        
        print(json.dumps(result))
        
    except requests.RequestException as e:
        print(json.dumps({"status": "error", "message": f"API request failed: {str(e)}"}))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main()
''',
                "requirements": "requests==2.31.0",
                "readme": """# MercadoLibre API Script

This script fetches item data from the MercadoLibre API.

## Usage

```bash
python script.py '{"item_id": "MLA123456789"}'
```

## Parameters

- `item_id`: MercadoLibre item ID

## Output

The script returns JSON with:
- `title`: Item title
- `price`: Item price
- `currency`: Currency ID
- `condition`: Item condition
- `available_quantity`: Available quantity
- `sold_quantity`: Sold quantity
""",
                "outputs": {
                    "title": "str",
                    "price": "float",
                    "currency": "str",
                    "condition": "str",
                    "available_quantity": "int",
                    "sold_quantity": "int"
                }
            }
        }
    
    def generate_script(self, request: GenerationRequest) -> Dict[str, Any]:
        """Generate a script based on the request."""
        prompt_lower = request.prompt.lower()
        
        # Simple template matching based on keywords
        if any(keyword in prompt_lower for keyword in ["video", "concatenate", "moviepy", "mp4"]):
            template = self.templates["video_concat"]
        elif any(keyword in prompt_lower for keyword in ["mercadolibre", "mercado libre", "api", "price", "item"]):
            template = self.templates["mercadolibre_api"]
        else:
            # Default to a generic Python script
            template = {
                "script": f'''# --- CAPIBARA ---
# language: python
# entry: script.py
# deps: 
# network: false
# template_version: 1.0.0
# --- /CAPIBARA ---

import json
import sys

def main():
    # Parse context from command line
    if len(sys.argv) < 2:
        print(json.dumps({{"status": "error", "message": "No context provided"}}))
        return
    
    try:
        context = json.loads(sys.argv[1])
        
        # TODO: Implement your logic here
        # Prompt: {request.prompt}
        
        result = {{
            "status": "ok",
            "artifacts": [],
            "output": {{}},
            "raw": context
        }}
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({{"status": "error", "message": str(e)}}))

if __name__ == "__main__":
    main()
''',
                "requirements": "",
                "readme": f"""# Generated Script

This script was generated from the prompt: "{request.prompt}"

## Usage

```bash
python script.py '{{"your": "context", "here": "data"}}'
```

## TODO

This is a template script. You need to implement the actual logic based on your requirements.
""",
                "outputs": {}
            }
        
        return template


class CapibaraCore:
    """Capibara Core service for script generation."""
    
    def __init__(self):
        self.llm = MockLLM()
        self.template_version = "1.0.0"
    
    def generate_script(self, request: GenerationRequest) -> GenerationResponse:
        """Generate a script from a prompt and context."""
        try:
            # Generate script using LLM
            template = self.llm.generate_script(request)
            
            # Generate fingerprint
            fingerprint = self._generate_fingerprint(request)
            
            # Create manifest
            manifest = ScriptManifest(
                fingerprint=fingerprint,
                prompt_sha=self._hash_prompt(request.prompt),
                context_sha=self._hash_context(request.context),
                language=request.language,
                entry="script.py",
                runtime={"python": "3.11"},
                deps=template["requirements"].split("\n") if template["requirements"] else [],
                allow={"network": "requests" in template["requirements"], "fs": []},
                template_version=self.template_version,
                outputs=template["outputs"]
            )
            
            return GenerationResponse(
                status="ok",
                script=template["script"],
                manifest=manifest,
                requirements=template["requirements"],
                readme=template["readme"]
            )
            
        except Exception as e:
            return GenerationResponse(
                status="error",
                script="",
                manifest=ScriptManifest(
                    fingerprint="",
                    prompt_sha="",
                    context_sha="",
                    language=request.language,
                    entry="script.py",
                    runtime={"python": "3.11"},
                    template_version=self.template_version
                ),
                requirements="",
                readme="",
                error=str(e)
            )
    
    def check_updates(self, request: UpdateRequest) -> UpdateResponse:
        """Check if a script needs updates."""
        # For now, always return no updates needed
        # In a real implementation, this would check for:
        # - New template versions
        # - Dependency updates
        # - Security vulnerabilities
        return UpdateResponse(
            needs_update=False,
            reason=None,
            new_fingerprint=None
        )
    
    def _generate_fingerprint(self, request: GenerationRequest) -> str:
        """Generate a fingerprint for the request."""
        content = f"{request.prompt}|{json.dumps(request.context, sort_keys=True)}|{request.language}|{self.template_version}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _hash_prompt(self, prompt: str) -> str:
        """Hash the normalized prompt."""
        normalized = prompt.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    def _hash_context(self, context: Dict[str, Any]) -> str:
        """Hash the normalized context."""
        normalized = json.dumps(context, sort_keys=True)
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
