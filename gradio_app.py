import gradio as gr
import threading, time, queue, logging

# ---------- 1.  A thread‑safe queue for log messages ----------

    
class _BaseTool:
    def __init__(self, log_queue: queue.Queue | None = None):
        self.log_queue = log_queue

    def push_log(self, msg: str):
        if self.log_queue:
            self.log_queue.put(msg)

    def forward(self, input: str) -> str:
        raise NotImplementedError("Subclasses must implement forward method")

# ---------- 2.  Tools that report progress ----------
class SearchTool(_BaseTool):
    def forward(self, query: str) -> str:
        self.push_log(f"🔍 SearchTool → {query}")
        time.sleep(2)                      # expensive work…
        out = f"Found {query}"
        self.push_log(f"✅ SearchTool done")
        return out

class DrawTool(_BaseTool):
    def forward(self, prompt: str) -> str:
        self.push_log(f"🎨 DrawTool → {prompt}")
        time.sleep(2)
        out = f"Drawing {prompt}"
        self.push_log(f"✅ DrawTool done")
        return out

# ---------- 3.  Your unchanged agent -------------------------
def agent(user_input: str, log_queue: queue.Queue) -> str:
    st, dt = SearchTool(log_queue), DrawTool(log_queue)
    return st.forward(user_input) + dt.forward(user_input) + st.forward(user_input) + dt.forward(user_input)

# ---------- 4.  Wrapper that streams -------------------------
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
        log_queue.get_nowait()

    answer_container = {"text": None}
    done = threading.Event()

    def _worker():
        answer_container["text"] = agent(user_input, log_queue)
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

# ---------- 5.  Gradio UI ------------------------------------
with gr.Blocks() as demo:
    gr.Markdown("## Agent Interface with Real‑Time Tool Logging")
    user_input  = gr.Textbox(label="User Message")
    agent_output = gr.Textbox(label="Agent Response")
    log_output   = gr.Textbox(label="Tool Invocation Log", interactive=False)

    send = gr.Button("Send")
    send.click(
        fn=run_agent_stream,
        inputs=[user_input],
        outputs=[agent_output, log_output],
        concurrency_limit=4,
    )

if __name__ == "__main__":
    demo.launch()
