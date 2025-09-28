"""LLM service implementation using Groq."""

import os
import re
from typing import Dict, Any, Optional
from groq import Groq


class GroqLLMService:
    """LLM service using Groq for code generation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Groq LLM service."""
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"
    
    def generate_script(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a script using Groq LLM."""
        context = context or {}
        
        # Create a detailed prompt for code generation
        system_prompt = """You are an expert Python developer. Generate executable Python scripts that follow the Capibara framework.

IMPORTANT: The script must start with the exact Capibara header format and include the complete Python code.

Required format:
```python
# --- CAPIBARA ---
# language: python
# entry: script.py
# deps: package1==1.0.0,package2==2.0.0
# network: true/false
# template_version: 1.0.0
# --- /CAPIBARA ---

import json
import sys
# ... other imports

def main():
    # Parse context from command line
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "No context provided"}))
        return
    
    try:
        context = json.loads(sys.argv[1])
        # ... your logic here
        
        result = {
            "status": "ok",
            "artifacts": [],  # List of created files
            "output": {},     # Structured output data
            "raw": {}         # Raw data for debugging
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main()
```

Generate ONLY the complete script with the exact header format shown above. Do not include any explanations or markdown formatting."""

        user_prompt = f"""Generate a Python script for: {prompt}

Context: {context}

Make sure to:
- Include all necessary imports
- Specify correct dependencies in the deps field
- Set network: true if the script needs internet access
- Return proper JSON responses
- Handle edge cases and errors
- Make the code clean and well-documented"""

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.1,  # Low temperature for more deterministic code
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            
            # Extract script from delimiters
            script = self._extract_script(content)
            if not script:
                raise ValueError("No valid script found in LLM response")
            
            # Add Capibara header if not present
            if not script.startswith("# --- CAPIBARA ---"):
                script = self._add_capibara_header(script, prompt, context)
            
            # Parse metadata from script
            metadata = self._parse_metadata(script)
            
            # Generate requirements and readme
            requirements = self._generate_requirements(metadata.get("deps", ""))
            readme = self._generate_readme(prompt, script, metadata)
            
            return {
                "script": script,
                "requirements": requirements,
                "readme": readme,
                "metadata": metadata,
                "outputs": self._infer_outputs(script)
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate script with Groq: {str(e)}")
    
    def _extract_script(self, content: str) -> Optional[str]:
        """Extract script content between delimiters."""
        # Look for the script between delimiters
        start_pattern = r"# --- CAPIBARA_START ---"
        end_pattern = r"# --- CAPIBARA_END ---"
        
        start_match = re.search(start_pattern, content)
        end_match = re.search(end_pattern, content)
        
        if start_match and end_match:
            return content[start_match.end():end_match.start()].strip()
        
        # Fallback: look for code blocks
        code_block_pattern = r"```python\s*(.*?)\s*```"
        match = re.search(code_block_pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Look for Capibara header and extract everything after it
        header_pattern = r"# --- CAPIBARA ---\s*(.*?)\s*# --- /CAPIBARA ---"
        header_match = re.search(header_pattern, content, re.DOTALL)
        if header_match:
            # Return everything after the header
            header_end = header_match.end()
            return content[header_end:].strip()
        
        # Last resort: return the whole content if it looks like Python
        if "def main():" in content and "if __name__ == \"__main__\":" in content:
            return content.strip()
        
        return None
    
    def _add_capibara_header(self, script: str, prompt: str, context: Dict[str, Any]) -> str:
        """Add Capibara header to script if not present."""
        # Analyze script to determine dependencies and network usage
        deps = []
        network_required = False
        
        # Check for common dependencies
        if "import requests" in script or "from requests" in script:
            deps.append("requests==2.31.0")
            network_required = True
        if "import pandas" in script or "from pandas" in script:
            deps.append("pandas==2.0.0")
        if "import numpy" in script or "from numpy" in script:
            deps.append("numpy==1.24.0")
        if "import pillow" in script or "from PIL" in script:
            deps.append("pillow==10.0.0")
        if "import matplotlib" in script or "from matplotlib" in script:
            deps.append("matplotlib==3.7.0")
        if "import opencv" in script or "import cv2" in script:
            deps.append("opencv-python==4.8.0")
        
        # Check for network usage patterns
        if any(pattern in script.lower() for pattern in ["http", "api", "url", "request", "fetch", "download"]):
            network_required = True
        
        # Build dependencies string
        deps_str = ",".join(deps) if deps else ""
        
        # Create header
        header = f"""# --- CAPIBARA ---
# language: python
# entry: script.py
# deps: {deps_str}
# network: {str(network_required).lower()}
# template_version: 1.0.0
# --- /CAPIBARA ---

"""
        
        return header + script
    
    def _parse_metadata(self, script: str) -> Dict[str, Any]:
        """Parse Capibara metadata from script header."""
        metadata = {
            "language": "python",
            "entry": "script.py",
            "deps": "",
            "network": False,
            "template_version": "1.0.0"
        }
        
        # Extract metadata from header
        header_pattern = r"# --- CAPIBARA ---\s*(.*?)\s*# --- /CAPIBARA ---"
        header_match = re.search(header_pattern, script, re.DOTALL)
        
        if header_match:
            header_content = header_match.group(1)
            for line in header_content.split('\n'):
                line = line.strip()
                if line.startswith('#') and ':' in line:
                    key, value = line[1:].split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == "language":
                        metadata["language"] = value
                    elif key == "entry":
                        metadata["entry"] = value
                    elif key == "deps":
                        metadata["deps"] = value
                    elif key == "network":
                        metadata["network"] = value.lower() == "true"
                    elif key == "template_version":
                        metadata["template_version"] = value
        
        return metadata
    
    def _generate_requirements(self, deps: str) -> str:
        """Generate requirements.txt content from dependencies."""
        if not deps:
            return ""
        
        # Split by comma and clean up
        packages = [dep.strip() for dep in deps.split(',') if dep.strip()]
        return '\n'.join(packages)
    
    def _generate_readme(self, prompt: str, script: str, metadata: Dict[str, Any]) -> str:
        """Generate README.md content."""
        readme = f"""# Generated Script

This script was generated from the prompt: "{prompt}"

## Usage

```bash
python script.py '{{"your": "context", "here": "data"}}'
```

## Dependencies

{self._generate_requirements(metadata.get("deps", "")) or "No external dependencies required"}

## Features

- Accepts JSON context via command line arguments
- Returns structured JSON output
- Handles errors gracefully
- Production-ready code

## Output Format

The script returns JSON with the following structure:
- `status`: "ok" or "error"
- `artifacts`: List of created files
- `output`: Structured output data
- `raw`: Raw data for debugging
"""
        return readme
    
    def _infer_outputs(self, script: str) -> Dict[str, str]:
        """Infer output types from the script content."""
        outputs = {}
        
        # Look for common output patterns
        if "artifacts" in script:
            outputs["artifacts"] = "list[str]"
        if "output" in script:
            outputs["output"] = "dict"
        if "raw" in script:
            outputs["raw"] = "dict"
        
        return outputs
