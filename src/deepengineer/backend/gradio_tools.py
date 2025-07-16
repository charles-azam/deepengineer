import threading
import time
import queue
import re
from pathlib import Path

from deepengineer.deepsearch.main_agent import main_search
from deepengineer.common_path import DATA_DIR


def parse_markdown_images(markdown_text: str, image_dir: Path) -> str:
    """
    Replace image references ![Title](image_name.png) with ![Title](image_dir/image_name.png)
    """
    if not markdown_text or not image_dir:
        return markdown_text

    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'

    def replace_image_path(match):
        alt_text = match.group(1)
        image_name = match.group(2)
        # Always use image_dir/image_name
        new_path = str(Path(image_dir) / image_name)
        return f'![{alt_text}]({new_path})'

    return re.sub(image_pattern, replace_image_path, markdown_text)


def run_agent_stream(user_input: str):
    """
    Generator wired to Gradio:
      – starts the agent in a background thread
      – while the agent runs, flushes anything that tools
        have pushed into `log_queue`
      – finally yields the agent's answer with embedded images
    Yields tuples: (agent_output, log_output)
    """
    log_queue = queue.Queue()
    
    # empty queue before each run
    while not log_queue.empty():
        print("Emptying log queue")
        log_queue.get_nowait()

    answer_container = {"text": None, "image_dir": None}
    done = threading.Event()

    def _worker():
        answer_container["text"], answer_container["image_dir"] = main_search(user_input, log_queue)
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

    # Process the final answer to include images
    final_answer = answer_container["text"]
    image_dir = answer_container["image_dir"]
    
    if final_answer and image_dir:
        final_answer = parse_markdown_images(final_answer, image_dir)
        
    final_answer = final_answer.replace("```python", "")
    final_answer = final_answer.replace("```markdown", "")
    final_answer = final_answer.replace("```", "")

    # final yield: agent_output filled with processed markdown, log_output frozen
    yield (final_answer, log_buffer.rstrip())