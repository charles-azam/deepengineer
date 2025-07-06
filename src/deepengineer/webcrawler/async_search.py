import os
import asyncio
import requests
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum

from linkup import LinkupClient, LinkupSourcedAnswer
from tavily import AsyncTavilyClient

from langchain_community.retrievers import ArxivRetriever
from langchain_community.utilities.pubmed import PubMedAPIWrapper

class SearchResult(BaseModel):
    """Represents a single search result from any search API."""
    title: str = Field(..., description="Title of the search result")
    url: str = Field(..., description="URL of the result")
    content: str = Field(..., description="Summary/snippet of content")
    raw_content: Optional[str] = Field(None, description="Full page content if available")

class SearchResponse(BaseModel):
    """Represents a search response from any search API."""
    query: str = Field(..., description="The original search query")
    answer: str | None = Field(None, description="Direct answer from the search API if available")
    search_results: list[SearchResult] = Field(default_factory=list, description="List of search results")
    
class ScientificDomains(str, Enum):
    wikipedia = "wikipedia.org"
    arxiv = "arxiv.org"
    pubmed = "pubmed.ncbi.nlm.nih.gov"
    sciencedirect = "sciencedirect.com"

def get_tavily_usage():
    url = "https://api.tavily.com/usage"
    headers = {"Authorization": f"Bearer {os.getenv('TAVILY_API_KEY')}"}
    response = requests.request("GET", url, headers=headers)
    response_json = response.json()
    usage = int(response_json["key"]["usage"])
    return usage


async def tavily_search_async(
    search_query: str,
    max_results: int = 10,
    include_answer: Literal["basic", "advanced"] | None = "advanced",
    include_raw_content: Literal["text", "markdown"] | None = "markdown",
    include_images: bool = False,
    search_depth: Literal['basic', 'advanced'] | None = "basic",
    include_domains: list[ScientificDomains] = None,
) -> SearchResponse:
    """
    Performs concurrent web searches with the Tavily API
    """
    tavily_async_client = AsyncTavilyClient()
    
    search_response = await tavily_async_client.search(
        query=search_query,
        search_depth=search_depth,
        include_answer=include_answer,
        include_raw_content=include_raw_content,
        max_results=max_results,
        include_images=include_images,
        include_domains=include_domains,
    )
    
    search_results = [
        SearchResult(
            title=result.get('title', ''),
            url=result.get('url', ''),
            content=result.get('content', ''),
            raw_content=result.get('raw_content')
        )
        for result in search_response.get('results', [])
    ]

    # Convert to our Pydantic models
    responses: SearchResponse = SearchResponse(
        query=search_query,
        answer=search_response.get('answer', None),
        search_results=search_results
    )
    return responses


def get_linkup_balance():
    url = "https://api.linkup.so/v1/credits/balance"
    
    headers = {"Authorization": f"Bearer {os.getenv('LINKUP_API_KEY')}"}

    response = requests.request("GET", url, headers=headers)
    response_json = response.json()
    balance = float(response_json["balance"])
    return balance


async def linkup_search_async(
    search_query: str,
    depth: Literal["standard", "deep"] = "standard",
    output_type: Literal['searchResults', 'sourcedAnswer', 'structured'] = "sourcedAnswer",
    include_images: bool = False,
    include_domains: list[ScientificDomains] = None,
) -> SearchResponse:
    """
    Performs concurrent web searches using the Linkup API.
    """
    
    client = LinkupClient()
    search_response: LinkupSourcedAnswer = await client.async_search(
        query=search_query,
        depth=depth,
        output_type=output_type,
        include_images=include_images,
        include_domains=include_domains,
    )
    
    search_results = [
        SearchResult(
            title=result.name,
            url=result.url,
            content=result.snippet,
            raw_content=None,
        )
        for result in search_response.sources
    ]

    # Convert to our Pydantic models
    responses: SearchResponse = SearchResponse(
        query=search_query,
        answer=search_response.answer,
        search_results=search_results
    )
    return responses





async def arxiv_search_async(
    search_query: str,
) -> SearchResponse:
    response = await linkup_search_async(search_query, include_domains=[ScientificDomains.arxiv])
    return response


async def pubmed_search_async(
    search_query: str,
) -> SearchResponse:
    response = await linkup_search_async(search_query, include_domains=[ScientificDomains.pubmed])
    return response

async def sciencedirect_search_async(
    search_query: str,
) -> SearchResponse:
    response = await linkup_search_async(search_query, include_domains=[ScientificDomains.sciencedirect])
    return response

async def scientific_search_async(
    search_query: str,
) -> SearchResponse:
    response = await linkup_search_async(search_query, include_domains=[ScientificDomains.wikipedia, ScientificDomains.arxiv, ScientificDomains.pubmed, ScientificDomains.sciencedirect])
    return response