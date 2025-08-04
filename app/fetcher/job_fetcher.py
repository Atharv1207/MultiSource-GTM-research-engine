import httpx
import asyncio
from typing import List, Dict

RAPIDAPI_KEY = "your-rapidapi-key"  # 🔒 Replace this with your real key

class JobBoardFetcher:
    async def fetch_for_domain(self, client: httpx.AsyncClient, domain: str) -> Dict:
        query = domain.split(".")[0]  # Just use the company name from domain
        url = "https://jsearch.p.rapidapi.com/search"

        params = {"query": query, "num_pages": "1"}
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }

        try:
            response = await client.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            jobs = data.get("data", [])[:3]  # Limit to top 3 jobs
            return {
                "domain": domain,
                "data": [job["job_title"] for job in jobs],
                "sources": [job["job_apply_link"] for job in jobs]
            }
        except Exception as e:
            return {
                "domain": domain,
                "error": str(e),
                "data": [],
                "sources": []
            }

    async def fetch(self, domains: List[str]) -> List[Dict]:
        async with httpx.AsyncClient() as client:
            tasks = [self.fetch_for_domain(client, d) for d in domains]
            return await asyncio.gather(*tasks)
