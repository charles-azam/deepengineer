import pytest
from deepengineer.deepsearch.scawl_web_agent import create_web_search_agent


def test_create_web_search_agent():
    create_web_search_agent()


@pytest.mark.skip(reason="This test is very long to run")
def test_run_web_search_agent():
    agent = create_web_search_agent()
    assert (
        agent.run(
            "Est il possible de faire un réacteur thermique avec du graphite et du plomb?"
        )
        is not None
    )
