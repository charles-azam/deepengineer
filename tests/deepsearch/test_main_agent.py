from deepengineer.deepsearch.main_agent import main_search
import queue


def test_main_agent():
    log_queue = queue.Queue()

    main_search(
        task="""
    Search a paper called "High Energy Physics Opportunities Using Reactor Antineutrinos" on arXiv, download it and extract the table of contents
    """, log_queue=log_queue
    )
