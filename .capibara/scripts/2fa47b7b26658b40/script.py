# --- CAPIBARA ---
# language: python
# entry: script.py
# deps: 
# network: false
# template_version: 1.0.0
# --- /CAPIBARA ---

import json
import sys
from json2html import json2html

def generate_html_report(context):
    """
    Generate a simple HTML report from JSON data.

    Args:
        context (dict): A dictionary containing the report data.
            It should have the following structure:
            {
                'data': {
                    'title': 'Report Title',
                    'items': [item1, item2, ...]
                }
            }

    Returns:
        str: The HTML report as a string.
    """
    try:
        data = context['data']
        title = data['title']
        items = data['items']

        # Create a dictionary to hold the report data
        report_data = {
            'title': title,
            'items': items
        }

        # Convert the report data to HTML
        html_report = json2html.convert(json.dumps(report_data))

        return html_report

    except KeyError as e:
        raise ValueError(f"Missing key: {e}")
    except Exception as e:
        raise ValueError(f"Error generating report: {e}")

def main():
    # Parse context from command line
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "No context provided"}))
        return
    
    try:
        context = json.loads(sys.argv[1])
        html_report = generate_html_report(context)

        result = {
            "status": "ok",
            "artifacts": ["report.html"],  # List of created files
            "output": {"report": html_report},     # Structured output data
            "raw": {}         # Raw data for debugging
        }
        
        # Save the HTML report to a file
        with open("report.html", "w") as f:
            f.write(html_report)

        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main()