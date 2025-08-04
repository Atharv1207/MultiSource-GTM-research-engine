import asyncio
import time

from app.fetcher.job_fetcher import JobBoardFetcher
from app.fetcher.news_fetcher import NewsFetcher
from app.models.research_request import ResearchRequest
from app.models.research_response import ResearchResponse, ResearchResult
from app.query.query_generator import QueryGenerator
from app.query.query_strategy import ParallelQueryStrategy
from app.utils.duplication import deduplicate_findings
from app.utils.scoring import score_confidence


class DataPipelineController:
    def __init__(self, user_intent: str):
        self.news_fetcher = NewsFetcher()
        self.job_fetcher = JobBoardFetcher()
        self.query_generator = QueryGenerator(user_intent)  # pass user intent
        self.query_strategy = ParallelQueryStrategy()  # your strategy class

    async def run_pipeline(self, request: ResearchRequest) -> ResearchResponse:
        start_time = time.time()
        company_domains = request.company_domains

        # Step 1: Generate queries per domain + source type
        queries_by_domain = {}
        for domain in company_domains:
            queries_by_domain[domain] = {}
            for source in self.query_strategy.sources:
                queries = await self.query_generator.generate_queries(source_type=source, n=5)  # async version needed
                queries_by_domain[domain][source] = queries

        # Step 2: Use QueryStrategy to fetch Bing results concurrently
        query_strategy_task = asyncio.create_task(self.query_strategy.fetch(queries_by_domain))
        news_task = asyncio.create_task(self.news_fetcher.fetch(company_domains))
        job_task = asyncio.create_task(self.job_fetcher.fetch(company_domains))

        all_results = await asyncio.gather(query_strategy_task, news_task, job_task, return_exceptions=True)
        strategy_results, news_results, job_results = all_results

        all_findings = []
        for result_group in [strategy_results, news_results, job_results]:
            if isinstance(result_group, Exception):
                continue
            all_findings.extend(result_group)

        # Step 3: Deduplicate and score
        deduped = deduplicate_findings(all_findings)
        scored_results = score_confidence(deduped, request.confidence_threshold)

        research_results = [
            ResearchResult(
                domain=item['domain'],
                confidence_score=item['confidence'],
                evidence_sources=item['sources'],
                findings=item['data'],
            )
            for item in scored_results
        ]

        total_time = int((time.time() - start_time) * 1000)

        return ResearchResponse(
            research_id=f"research-{int(time.time())}",
            total_companies=len(company_domains),
            search_strategies_generated=len(company_domains) * len(self.query_strategy.sources),
            total_searches_executed=len(all_findings),
            processing_time_ms=total_time,
            results=research_results,
            search_performance={
                "success_rate": round(len(scored_results) / max(len(all_findings), 1), 2),
                "avg_sources_per_domain": round(
                    sum(len(x['sources']) for x in scored_results) / max(len(scored_results), 1), 2
                ),
            }
        )