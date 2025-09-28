# Generated Script

This script was generated from the prompt: "Create a script that fetches data from a REST API"

## Usage

```bash
python script.py '{"your": "context", "here": "data"}'
```

## Dependencies

requests==2.31.0

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
