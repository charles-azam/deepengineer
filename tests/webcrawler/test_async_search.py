import asyncio
import pytest
from deepengineer.webcrawler.async_search import (
    tavily_search_async,
    SearchResponse,
    get_tavily_usage,
    linkup_search_async,
    get_linkup_balance
)


@pytest.mark.expensive
@pytest.mark.asyncio
async def test_tavily_search_async():
    
    usage_before = get_tavily_usage()
    print(usage_before)
    

    response = await tavily_search_async(
        search_query="Would it be possible to make a thermal reactor with graphite and lead?",
    )
    
    print(response.answer)
    assert response is not None
    assert isinstance(response, SearchResponse)
    assert (
        response.query
        == "Would it be possible to make a thermal reactor with graphite and lead?"
    )
    assert response.answer is not None
    assert response.search_results is not None
    assert len(response.search_results) == 10
    assert response.search_results[0].title is not None
    assert response.search_results[0].url is not None
    assert response.search_results[0].content is not None
    assert any(result.raw_content is not None for result in response.search_results)

    usage_after = get_tavily_usage()
    print(usage_after)
    assert usage_after == usage_before + 1

@pytest.mark.expensive
@pytest.mark.asyncio
async def test_linkup_search_async():
    
    balance_before = get_linkup_balance()
    print(balance_before)

    response = await linkup_search_async(
        search_query="Would it be possible to make a thermal reactor with graphite and lead?",
    )
    print(response.answer)
    assert response is not None
    assert isinstance(response, SearchResponse)
    assert (
        response.query
        == "Would it be possible to make a thermal reactor with graphite and lead?"
    )
    assert len(response.search_results) >= 10
    assert response.search_results[0].title is not None
    assert response.search_results[0].url is not None
    assert response.search_results[0].content is not None
    assert response.search_results[0].raw_content is None

    balance_after = get_linkup_balance()
    print(balance_after)
    assert balance_after == balance_before - 0.005
