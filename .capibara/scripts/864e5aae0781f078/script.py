# --- CAPIBARA ---
# language: python
# entry: script.py
# deps: 
# network: false
# template_version: 1.0.0
# --- /CAPIBARA ---

import json
import sys

def add_numbers(context):
    """
    Adds two numbers from the context.

    Args:
        context (dict): Dictionary containing 'a' and 'b' keys with numeric values.

    Returns:
        dict: Dictionary with the result of the addition.
    """
    try:
        a = context['a']
        b = context['b']
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise ValueError("Both 'a' and 'b' must be numbers")
        result = a + b
        return {
            "status": "ok",
            "artifacts": [],
            "output": {"result": result},
            "raw": {}
        }
    except KeyError as e:
        return {
            "status": "error",
            "message": f"Missing key: {str(e)}"
        }
    except ValueError as e:
        return {
            "status": "error",
            "message": str(e)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def main():
    # Parse context from command line
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "No context provided"}))
        return
    
    try:
        context = json.loads(sys.argv[1])
        result = add_numbers(context)
        print(json.dumps(result))
    except json.JSONDecodeError:
        print(json.dumps({"status": "error", "message": "Invalid JSON context"}))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main()