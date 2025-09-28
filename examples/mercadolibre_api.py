"""Example: MercadoLibre API with Capibara."""

from capibara import Capibara

def main():
    # Initialize Capibara
    cb = Capibara()
    
    # Example 2: Fetch item data from MercadoLibre
    print("=== MercadoLibre API Example ===")
    
    result = cb.run(
        "Use MercadoLibre API to fetch price and description",
        context={"item_id": "MLA123456789"},
        select=["title", "price"]
    )
    
    print(f"Status: {result.status}")
    if result.status == "ok":
        print(f"Title: {result.title}")
        print(f"Price: {result.price}")
        print(f"Raw data: {result.raw}")
    else:
        print(f"Error: {result.output.get('message', 'Unknown error')}")

if __name__ == "__main__":
    main()
