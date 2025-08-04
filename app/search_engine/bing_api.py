import asyncio
from typing import List, Dict
from bing_client import BingSearchClient


async def _search_one_query(client: BingSearchClient, query: str, count: int) -> List[str]:
    try:
        return await client.search(query, count)
    except Exception as e:
        print(f"Search failed for query: {query}\nError: {e}")
        return []


async def _run_all_searches(queries: List[str], count: int = 10) -> Dict[str, List[str]]:
    client = BingSearchClient()
    tasks = [_search_one_query(client, q, count) for q in queries]
    results = await asyncio.gather(*tasks)
    return {q: res for q, res in zip(queries, results)}


def run_parallel_bing_searches(queries: List[str], count: int = 10) -> Dict[str, List[str]]:
    return asyncio.run(_run_all_searches(queries, count))
