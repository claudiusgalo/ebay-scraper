from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional
from ebay_scraper import fetch_sold_listings, calculate_stats

app = FastAPI()

class StatsResponse(BaseModel):
    mean: float
    median: float
    stddev: float
    max: float
    min: float
    daily_rate_of_change: Optional[float] = None  # <-- this is the key fix
    sample_size: int

@app.get("/ebay_stats", response_model=StatsResponse)
def ebay_stats(
    search_term: str = Query(..., description="eBay search query"),
    proxy: str = Query(None, description="Proxy URL (e.g. http://user:pass@host:port)"),
    max_pages: int = Query(1, description="How many pages to fetch")
):
    listings = fetch_sold_listings(search_term, proxy, max_pages)
    stats = calculate_stats(listings)
    if not stats:
        return StatsResponse(
            mean=0, median=0, stddev=0, max=0, min=0, daily_rate_of_change=0, sample_size=0
        )
    return stats
