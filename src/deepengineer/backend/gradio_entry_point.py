import gradio as gr
import asyncio
import threading
import time
from smolagents import Tool
from deepengineer.deepsearch.main_agent import main_search
import time

class SearchTool:
    
    def forward(self, input: str) -> str:
        time.sleep(1)
        #yield (f"Searching for {input}", None)
        return f"Found {input}"

class DrawTool:
    def forward(self, input: str) -> str:
        time.sleep(1)
        #yield (f"Drawing {input}", None)
        return f"Drawing {input}"

# Streaming runner
def run_agent(user_input):
    search_tool = SearchTool()
    draw_tool = DrawTool()
    final_answer = search_tool.forward(user_input) + draw_tool.forward(user_input)
    return final_answer

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
