import aiohttp
import asyncio
import os
from typing import List, Dict

BING_NEWS_API_KEY = os.getenv("BING_NEWS_API_KEY")
BING_NEWS_ENDPOINT = "https://api.bing.microsoft.com/v7.0/news/search"

HEADERS = {
    "Ocp-Apim-Subscription-Key": BING_NEWS_API_KEY
}

class NewsFetcher:
    async def fetch_news_for_domain(self, session, domain: str) -> Dict:
        params = {
            "q": domain,
            "count": 3,  # top 3 headlines
            "mkt": "en-US"
        }

        try:
            async with session.get(BING_NEWS_ENDPOINT, headers=HEADERS, params=params) as resp:
                data = await resp.json()
                articles = data.get("value", [])
                return {
                    "domain": domain,
                    "data": [article["name"] for article in articles],
                    "sources": [article["url"] for article in articles]
                }
        except Exception as e:
            return {
                "domain": domain,
                "error": str(e),
                "data": [],
                "sources": []
            }

    async def fetch(self, domains: List[str]) -> List[Dict]:
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_news_for_domain(session, d) for d in domains]
            return await asyncio.gather(*tasks)
