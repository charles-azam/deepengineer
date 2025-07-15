import gradio as gr
import threading, time, queue, logging

# ---------- 1.  A thread‑safe queue for log messages ----------
log_queue = queue.Queue()

def push_log(msg: str):
    """Helper so tools can push log lines."""
    log_queue.put(msg)

# ---------- 2.  Tools that report progress ----------
class SearchTool:
    def forward(self, query: str) -> str:
        push_log(f"🔍 SearchTool → {query}")
        time.sleep(1)                      # expensive work…
        out = f"Found {query}"
        push_log(f"✅ SearchTool done")
        return out

class DrawTool:
    def forward(self, prompt: str) -> str:
        push_log(f"🎨 DrawTool → {prompt}")
        time.sleep(1)
        out = f"Drawing {prompt}"
        push_log(f"✅ DrawTool done")
        return out

# ---------- 3.  Your unchanged agent -------------------------
def agent(user_input: str) -> str:
    st, dt = SearchTool(), DrawTool()
    return st.forward(user_input) + dt.forward(user_input)

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
    # empty queue before each run
    while not log_queue.empty():
        log_queue.get_nowait()

    answer_container = {"text": None}
    done = threading.Event()

    def _worker():
        answer_container["text"] = agent(user_input)
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
    )

if __name__ == "__main__":
    demo.launch()
