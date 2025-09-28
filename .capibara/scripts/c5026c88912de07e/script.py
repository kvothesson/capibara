# --- CAPIBARA ---
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
