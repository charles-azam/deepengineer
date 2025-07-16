import queue

import pytest

from deepengineer.deepsearch.main_agent import main_search


@pytest.mark.expensive
def test_main_agent():
    log_queue = queue.Queue()
    while not log_queue.empty():
        print("Emptying log queue")
        log_queue.get_nowait()

    main_search(
        task="""
    Search a paper called "High Energy Physics Opportunities Using Reactor Antineutrinos" on arXiv, download it and extract the table of contents
    """,
        log_queue=log_queue,
    )
