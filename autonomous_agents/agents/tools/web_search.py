"""
Web search tool for autonomous agents.
Provides internet search capabilities using DuckDuckGo.
"""

import json
from typing import List, Dict, Any
from strands import tool


try:
    from duckduckgo_search import DDGS
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web for information.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 5)

    Returns:
        JSON string with search results including titles, links, and snippets
    """
    if not SEARCH_AVAILABLE:
        return json.dumps({"error": "Web search not available. Install duckduckgo-search package."})

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

            # Format results
            formatted_results = []
            for idx, result in enumerate(results, 1):
                formatted_results.append({
                    "position": idx,
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("body", "")
                })

            return json.dumps({
                "query": query,
                "results_count": len(formatted_results),
                "results": formatted_results
            }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}"})


@tool
def web_search_news(query: str, max_results: int = 5) -> str:
    """
    Search for recent news articles.

    Args:
        query: News search query
        max_results: Maximum number of results (default: 5)

    Returns:
        JSON string with news results
    """
    if not SEARCH_AVAILABLE:
        return json.dumps({"error": "Web search not available."})

    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=max_results))

            formatted_results = []
            for idx, result in enumerate(results, 1):
                formatted_results.append({
                    "position": idx,
                    "title": result.get("title", ""),
                    "link": result.get("url", ""),
                    "source": result.get("source", ""),
                    "date": result.get("date", ""),
                    "body": result.get("body", "")
                })

            return json.dumps({
                "query": query,
                "results_count": len(formatted_results),
                "results": formatted_results
            }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"News search failed: {str(e)}"})
