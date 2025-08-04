from pydantic import BaseModel
from typing import List


class Findings(BaseModel):
    ai_fraud_detection: bool
    technologies: List[str]
    evidence: List[str]
    signals_found: int


class ResearchResult(BaseModel):
    domain: str
    confidence_score: float
    evidence_sources: int
    findings: Findings


class SearchPerformance(BaseModel):
    queries_per_second: float
    cache_hit_rate: float
    failed_requests: int


class ResearchResponse(BaseModel):
    research_id: str
    total_companies: int
    search_strategies_generated: int
    total_searches_executed: int
    processing_time_ms: int
    results: List[ResearchResult]
    search_performance: SearchPerformance
