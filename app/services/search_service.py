import httpx
from app.core.config import get_settings


class SearchService:
    def __init__(self):
        self.settings = get_settings()

    def search_linkedin_posts(self, keywords: str, days: int, max_results: int) -> list[str]:
        if not self.settings.serper_api_key:
            return []

        query = f'site:linkedin.com/posts "{keywords}"'
        wanted = max(1, min(max_results, self.settings.max_search_results_cap))
        collected: list[str] = []
        page = 1

        while len(collected) < wanted:
            payload = {
                "q": query,
                "num": min(10, wanted - len(collected)),
                "page": page,
                "tbs": f"qdr:d{max(days, 1)}",
            }
            response = httpx.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": self.settings.serper_api_key, "Content-Type": "application/json"},
                json=payload,
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()
            organic = data.get("organic", [])
            if not organic:
                break
            for item in organic:
                link = item.get("link")
                if link:
                    collected.append(link)
            page += 1

        return collected[:wanted]
