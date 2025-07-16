import threading
import time
import queue

from deepengineer.deepsearch.main_agent import main_search


def run_agent_stream(user_input: str):
    """
    Generator wired to Gradio:
      – starts the agent in a background thread
      – while the agent runs, flushes anything that tools
        have pushed into `log_queue`
      – finally yields the agent’s answer
    Yields tuples: (agent_output, log_output)
    """
    log_queue = queue.Queue()
    
    # empty queue before each run
    while not log_queue.empty():
        print("Emptying log queue")
        log_queue.get_nowait()

    answer_container = {"text": None}
    done = threading.Event()

    def _worker():
        answer_container["text"] = main_search(user_input, log_queue)
        done.set()

    threading.Thread(target=_worker, daemon=True).start()

    # stream logs until the agent finishes
    log_buffer = ""
    while not done.is_set() or not log_queue.empty():
        while not log_queue.empty():
            log_line = log_queue.get()
            log_buffer += log_line + "\n"
            # keep agent_output None until we have the final answer
            yield (None, log_buffer.rstrip())
        time.sleep(0.1)

    # one last flush in case something arrived after last poll
    while not log_queue.empty():
        log_line = log_queue.get()
        log_buffer += log_line + "\n"

    # final yield: agent_output filled, log_output frozen
    yield (answer_container["text"], log_buffer.rstrip())