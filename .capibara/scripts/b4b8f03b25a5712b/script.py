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

def fetch_data_from_api(url):
    """
    Fetches data from a given REST API URL.

    Args:
        url (str): The URL of the REST API.

    Returns:
        dict: The response data from the API.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Error connecting to the API: {conn_err}")
    except requests.exceptions.Timeout as time_err:
        print(f"Timeout error occurred: {time_err}")
    except requests.exceptions.RequestException as err:
        print(f"Something went wrong: {err}")
    return None

def main():
    # Parse context from command line
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "No context provided"}))
        return
    
    try:
        context = json.loads(sys.argv[1])
        url = context.get('url')
        if not url:
            print(json.dumps({"status": "error", "message": "URL not provided in the context"}))
            return
        
        data = fetch_data_from_api(url)
        if data is None:
            print(json.dumps({"status": "error", "message": "Failed to fetch data from the API"}))
            return
        
        result = {
            "status": "ok",
            "artifacts": [],  # List of created files
            "output": {"data": data},     # Structured output data
            "raw": {}         # Raw data for debugging
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main()