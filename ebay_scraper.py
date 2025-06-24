import requests
from bs4 import BeautifulSoup
import urllib.parse
import numpy as np
import pandas as pd
from datetime import datetime
from typing import List

def fetch_sold_listings(search_term, proxy_url=None, max_pages=1):
    headers = {"User-Agent": "Mozilla/5.0"}
    results = []
    session = requests.Session()
    if proxy_url:
        session.proxies = {
            "http": proxy_url,
            "https": proxy_url
        }

    for page in range(1, max_pages+1):
        url = (
            f"https://www.ebay.com/sch/i.html?_nkw={urllib.parse.quote_plus(search_term)}"
            f"&LH_Sold=1&LH_Complete=1&_ipg=100&_pgn={page}"
        )
        resp = session.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(".s-item")
        for item in items:
            title = item.select_one(".s-item__title")
            price = item.select_one(".s-item__price")
            date = item.select_one(".s-item__title--tagblock .POSITIVE")
            link = item.select_one(".s-item__link")
            date_str = date.get_text(strip=True) if date else ""
            # Try to find date in "Ended: Jun 5, 2024" format in description
            desc = item.select_one(".s-item__title--tagblock")
            if desc:
                for s in desc.stripped_strings:
                    if s.startswith("Ended: "):
                        date_str = s.replace("Ended: ", "")
            if title and price and link:
                # Extract just the price number (handle $ and commas)
                price_txt = price.get_text(strip=True).replace("$", "").replace(",", "").split(" ")[0]
                try:
                    price_val = float(price_txt)
                except:
                    continue
                # Parse date if possible
                try:
                    sold_date = pd.to_datetime(date_str)
                except:
                    sold_date = pd.NaT
                results.append({
                    "title": title.get_text(strip=True),
                    "price": price_val,
                    "url": link.get("href"),
                    "sold_date": sold_date,
                })
    return results

def calculate_stats(listings: List[dict]):
    if not listings:
        return {}
    df = pd.DataFrame(listings)
    # Only drop rows where price is missing
    df = df.dropna(subset=["price"])
    if df.empty:
        return {}
    # Sort by date for rate calculations (if 'sold_date' exists)
    df = df.sort_values("sold_date")
    prices = df["price"].values
    dates = pd.to_datetime(df["sold_date"])
    # Calculate daily rate of change (percent)
    daily_roc = None
    if len(df) > 1 and not dates.isnull().all():
        # Only calculate if dates are valid
        valid_dates = dates.dropna()
        if len(valid_dates) > 1:
            date_diff = (valid_dates.iloc[-1] - valid_dates.iloc[0]).days
            if date_diff > 0:
                daily_roc = ((prices[-1] - prices[0]) / prices[0]) / date_diff
            else:
                daily_roc = 0
    stats = {
        "mean": float(np.mean(prices)),
        "median": float(np.median(prices)),
        "stddev": float(np.std(prices)),
        "max": float(np.max(prices)),
        "min": float(np.min(prices)),
        "daily_rate_of_change": float(daily_roc) if daily_roc is not None else None,
        "sample_size": int(len(prices)),
    }
    return stats
