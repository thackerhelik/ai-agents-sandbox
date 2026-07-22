from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from ddgs import DDGS

# custom search tool based on duckduckgo
class SearchToolInput(BaseModel):
    """Input schema for the Internet Search Tool."""
    search_query: str = Field(
        ...,
        description=(
            "The search query. CRITICAL: You must search like a human. " \
            "Use broad, simple keywords (e.g., 'San Francisco large conference venues'). "
            "Do NOT use exact-match quotes."
        )
    )

class SearchTool(BaseTool):
    name: str = "internet_search"
    description: str = (
        "Search the live internet for up-to-date company facts and news. "
        "Use simple keywords like 'DeepLearning AI news'."
    )
    args_schema: type[BaseModel] = SearchToolInput

    def _run(self, search_query: str) -> str:
        raw_results = list(DDGS().text(search_query, max_results=3))

        if not raw_results:
            return (
                f"Action Failed: No internet searches found for the query '{search_query}'. "
                "CRITICAL: You must try again using completely different, simpler, and broader keywords. "
                "REMOVE all exact-match quotes."
            )

        clean_text = "Here are the search results:\n\n"
        for result in raw_results:
            clean_text += f"Title: {result.get('title')}\n"
            clean_text += f"URL: {result.get('href')}\n"
            clean_text += f"Information: {result.get('body')}\n\n"

        return clean_text