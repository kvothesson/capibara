# --- CAPIBARA ---
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
        print(json.dumps({"status": "error", "message": "No context provided"}))
        return
    
    try:
        context = json.loads(sys.argv[1])
        
        # TODO: Implement your logic here
        # Prompt: Create a script that calculates the area of a rectangle
        
        result = {
            "status": "ok",
            "artifacts": [],
            "output": {},
            "raw": context
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main()
