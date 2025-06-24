print("Starting test_local.py")
from ebay_scraper import fetch_sold_listings, calculate_stats
print("Imports successful")

search_term = "sydney sweeny bath water"  # Change this to anything you want
proxy = None                   # Example: "http://user:pass@host:port"
max_pages = 1                  # Try 1 first to avoid being blocked

listings = fetch_sold_listings(search_term, proxy, max_pages)
print(f"Fetched {len(listings)} sold listings.")

if listings:
    stats = calculate_stats(listings)
    print("Statistics:")
    for k, v in stats.items():
        print(f"{k}: {v}")
else:
    print("No listings found.")
