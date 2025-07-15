import gradio as gr
import asyncio
import threading
import time
from smolagents import Tool
from deepengineer.deepsearch.main_agent import main_search
import time

# Streaming runner
def run_agent(user_input):
    for i in range(5):
        yield (f"{i}", None)
        time.sleep(1)
    yield (None, f"Final answer: {user_input}")

# Build Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("## Agent Interface with Real-Time Tool Logging")

    user_input = gr.Textbox(label="User Message")
    agent_output = gr.Textbox(label="Agent Response")
    log_output = gr.Textbox(label="Tool Invocation Log", interactive=False)

    # Button with streaming
    send_button = gr.Button("Send")
    send_button.click(
        fn=run_agent,
        inputs=[user_input],
        outputs=[agent_output, log_output],
    )

if __name__ == "__main__":
    demo.launch()
