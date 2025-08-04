import os
import httpx
from typing import List

BING_API_KEY = os.getenv("BING_API_KEY")
BING_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/search"


class BingSearchClient:
    def __init__(self, api_key: str = BING_API_KEY):
        if not api_key:
            raise ValueError("Bing API key not provided")
        self.headers = {"Ocp-Apim-Subscription-Key": api_key}

    async def search(self, query: str, count: int = 10) -> List[str]:
        params = {
            "q": query,
            "count": count,
            "responseFilter": "Webpages",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(BING_SEARCH_URL, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            webpages = data.get("webPages", {}).get("value", [])
            return [entry["url"] for entry in webpages if "url" in entry]
