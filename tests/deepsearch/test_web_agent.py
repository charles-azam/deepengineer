import pytest
from deepengineer.deepsearch.scawl_web_agent import create_web_search_agent


def test_create_web_search_agent():
    create_web_search_agent()


@pytest.mark.skip(reason="This test is very long to run")
def test_run_web_search_agent():
    agent = create_web_search_agent()
    assert (
        agent.run(
            'Search a paper called "High Energy Physics Opportunities Using Reactor Antineutrinos" on arXiv, download it and extract the table of contents'
        )
        is not None
    )

