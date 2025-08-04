from pydantic import BaseModel
from typing import List


class ResearchRequest(BaseModel):
    research_goal: str
    company_domains: List[str]
    search_depth: str  # "quick" | "standard" | "comprehensive"
    max_parallel_searches: int
    confidence_threshold: float
