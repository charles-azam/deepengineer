from deepengineer.webcrawler.async_search import linkup_search_async, SearchResponse, SearchResult, ScientificDomains
from linkup import LinkupClient, LinkupSourcedAnswer
from typing import Literal
import time
import asyncio

def _linkup_search_sync(
    search_query: str,
    depth: Literal["standard", "deep"] = "standard",
    output_type: Literal['searchResults', 'sourcedAnswer', 'structured'] = "sourcedAnswer",
    include_images: bool = False,
    include_domains: list[ScientificDomains] = None,

) -> SearchResponse:
    client = LinkupClient()
    search_response: LinkupSourcedAnswer = client.search(
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

def linkup_search_speed_test():
    
    """
    
Conclusion: no need to rewrite the async version to sync version. It takes roughly 6 seconds in both cases
    """
    
    print("Testing linkup search speed asynchronously...")
    start_time = time.time()
    for i in range(5):
        start_loop_time = time.time()
        output = asyncio.run(linkup_search_async(
            search_query="Would it be possible to make a thermal reactor with graphite and lead?",
        ))
        print(output.answer[:10])
        end_loop_time = time.time()
        print(f"Time taken for loop {i}: {end_loop_time - start_loop_time} seconds")
        
        
    print("Testing linkup search speed syncronoulsy...")
    start_time = time.time()
    for i in range(5):
        start_loop_time = time.time()
        _linkup_search_sync(
            search_query="Would it be possible to make a thermal reactor with graphite and lead?",
        )
        end_loop_time = time.time()
        print(f"Time taken for loop {i}: {end_loop_time - start_loop_time} seconds")

    end_time = time.time()
    print(f"Total time taken: {end_time - start_time} seconds")
    
    
    
