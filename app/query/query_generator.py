from typing import List, Literal

import openai

SourceType = Literal["news", "jobs", "blogs", "forums", "docs"]


class QueryGenerator:
    async def generate_queries(self, source_type: SourceType, n: int = 5) -> List[str]:
        system_prompt = (
            f"You are a search query generator for {source_type}. "
            f"Given a user goal like '{self.intent}', generate {n} specific Bing/Google search queries. "
            "Queries must be phrased like real-world user searches."
        )

        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": self.intent}
            ],
            temperature=0.7,
        )
        content = response["choices"][0]["message"]["content"]
        queries = [q.strip("-• \n") for q in content.strip().split("\n") if q.strip()]
        return queries[:n]
