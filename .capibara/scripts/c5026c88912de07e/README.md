# MercadoLibre API Script

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
