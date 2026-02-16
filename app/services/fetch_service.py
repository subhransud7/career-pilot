import httpx
from bs4 import BeautifulSoup


class FetchService:
    def fetch(self, url: str) -> str:
        response = httpx.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text(separator="\n").strip()[:8000]
