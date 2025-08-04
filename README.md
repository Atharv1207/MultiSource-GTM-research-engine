<h2>Parallel Multi-Source Data Pipeline</h2>

<h4>
This project implements a robust data pipeline for parallel retrieval, deduplication, and ranking of research data across multiple sources (job boards, news sites, search engines). The pipeline uses asynchronous fetching, query strategy management, scoring, and circuit breaker integration points for reliability.
</h4>


<h3>Project Overview</h3>
The system consists of the following key components:

```main.py```

Entry point of the application.
Starts the overall orchestration of the data pipeline.
Typically wires up the controller, routes, and supporting services.

```data_pipeline_controller.py```

Core orchestration logic.\
Coordinates:
1. Search query generation.
2. Parallel execution of fetchers.
3. Deduplication of results.
4. Scoring and ranking of final output.
5. Acts as the main "brain" tying together all other modules.

```research_request.py```

Defines the request model describing:
1. What topic or keywords to search.
2. Optional filters or parameters.
3. Used by controllers and query generators to initiate processing.

```research_response.py```

Defines the response model returned to clients.

Contains:

1. Aggregated results.

2. Metadata (e.g., scoring, deduplication status).

```query_generator.py```

Creates search queries dynamically:

For example: combining keywords, applying synonyms, or generating multiple variations.
Supports strategies such as keyword expansion or custom templates.

```query_strategy.py```

Implements strategies for selecting the optimal queries:

E.g., choosing based on historical performance, heuristics, or scoring.
Determines which queries will be executed in a given pipeline run.

```job_fetcher.py```

Specialized fetcher for job listings. Responsible for:
1. Making HTTP calls to job APIs or scraping endpoints.

2. ormalizing the response data into a consistent format.

```news_fetcher.py```
Specialized fetcher for news articles.

Similar responsibilities to job_fetcher.py but tailored for news sources.

```bing_api.py```
Encapsulates the Bing Search API logic:

1. Assembling API requests.

2. Handling authentication.

3. Managing result pagination.

```bing_client.py```

Low-level HTTP client for interacting with Bing:

1. Makes raw API calls.

2. Handles retries, error checking, and rate limiting logic.

3. Serves as a dependency for bing_api.py.

```research_route.py```

Defines the web route/endpoint to trigger research operations.

Example:  /research HTTP endpoint.

Handles incoming requests and returns pipeline results.

```html_fetcher.py```

Fetches raw HTML content of specific URLs.
Used when richer extraction is required beyond the API (e.g., scraping).

```duplication.py```

Contains deduplication logic:

1. Computes fingerprints or hashes of results.
2. Filters out duplicate or near-duplicate content.

```scoring.py```

Implements scoring and ranking of all fetched results.
Criteria might include:

1. Relevance to the query.
2. Recency.
3. Source trust level.
4. Produces a final sorted output.

<h3>How the End-to-End Flow Works</h3>
1. Request Received: A client sends a research request via research_route.py.\
2. Controller Invoked: data_pipeline_controller.py takes the request and initializes:
   1. Query generation (query_generator.py).
   2. Query strategy selection (query_strategy.py).
   
3. Parallel Search Execution
   1. For each query: Job fetcher, news fetcher, and Bing API run in parallel.
   2. This leverages async calls or thread pools for concurrency.

4. Optional HTML Fetching: For some URLs, html_fetcher.py retrieves detailed content.

5. Deduplication: Results are combined and passed to duplication.py to remove duplicates.
6. Scoring: Deduplicated results are scored and ranked via scoring.py.

7. Response: Final ranked results are packaged into research_response.py and returned via the route.

Key Features\
✅ Parallel multi-source search\
✅ Modular fetchers\
✅ Deduplication\
✅ Scoring and ranking\
✅ Extensible query generation\
✅ Clean separation of concerns\


Future Improvements:
- Add circuit breakers to protect against unstable sources.
- Implement caching of fetched results.
- Support more search engines (Google, DuckDuckGo).
- Integrate vector-based similarity scoring.