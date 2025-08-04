from typing import List, Dict
from app.search_engine.bing_api import run_parallel_bing_searches


class ParallelQueryStrategy:
    def __init__(self):
        self.sources = ["news", "jobs", "blogs", "articles"]

    async def fetch(self, queries_by_domain: Dict[str, Dict[str, List[str]]]) -> List[Dict]:
        """queries_by_domain: {
            "cisco.com": {
                "news": ["cisco layoffs", "cisco job cuts"],
                "jobs": [...],
                ...
            },
            ...
        }
        """
        all_findings = []

        for domain, source_queries in queries_by_domain.items():
            for source, queries in source_queries.items():
                print(f"\n{domain} | {source} → {len(queries)} queries")

                results = await run_parallel_bing_searches(queries)

                # Tag each result with domain + source
                for result in results:
                    all_findings.append({
                        "domain": domain,
                        "source": source,
                        "title": result.get("title"),
                        "url": result.get("url"),
                        "snippet": result.get("snippet"),
                    })

        return all_findings
