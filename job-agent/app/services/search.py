import os
import httpx
from datetime import datetime, timedelta

GOOGLE_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_SEARCH_CX")

def search_linkedin_posts(keywords: str, days: int, max_results: int = 10):

    date_filter = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

    query = f'site:linkedin.com/posts "{keywords}" after:{date_filter}'

    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": min(max_results, 10)
    }

    response = httpx.get(url, params=params, timeout=20)
    data = response.json()

    links = []

    for item in data.get("items", []):
        links.append(item["link"])

    return links
