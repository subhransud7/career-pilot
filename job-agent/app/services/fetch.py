import httpx
from bs4 import BeautifulSoup

def fetch_post_content(url: str):

    headers = {"User-Agent": "Mozilla/5.0"}

    response = httpx.get(url, headers=headers, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")

    text = soup.get_text(separator="\n")

    return text[:8000]  # Prevent token explosion
