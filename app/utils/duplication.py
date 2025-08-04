from typing import List, Dict
from collections import defaultdict
from difflib import SequenceMatcher

SIMILARITY_THRESHOLD = 0.85


def are_similar(text1: str, text2: str) -> bool:
    return SequenceMatcher(None, text1, text2).ratio() > SIMILARITY_THRESHOLD


def deduplicate_findings(findings: List[Dict]) -> List[Dict]:
    """
    Input format for each finding:
    {
        "domain": "example.com",
        "data": "Acme Corp recently raised $5M...",
        "sources": ["https://example.com/about", "https://newsapi.com/story/123"]
    }

    Output: Deduplicated list with merged sources
    """

    domain_grouped = defaultdict(list)

    for finding in findings:
        domain = finding["domain"]
        domain_grouped[domain].append(finding)

    deduped_results = []

    for domain, items in domain_grouped.items():
        merged = []

        while items:
            current = items.pop(0)
            similar_group = [current]

            i = 0
            while i < len(items):
                if are_similar(current["data"], items[i]["data"]):
                    similar_group.append(items[i])
                    items.pop(i)
                else:
                    i += 1

            merged_data = {
                "domain": domain,
                "data": current["data"],  # keep one of the similar texts
                "sources": list(set(source for item in similar_group for source in item["sources"]))
            }
            deduped_results.append(merged_data)

    return deduped_results
