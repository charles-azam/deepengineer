import gradio as gr
from deepengineer.backend.gradio_tools import run_agent_stream

with gr.Blocks() as demo:
    gr.Markdown("# Agent Interface with Real‑Time Tool Logging")
    user_input  = gr.Textbox(label="User Message")
    agent_output = gr.Markdown(
        label="Agent Response", 
    )
    log_output = gr.Textbox(label="Tool Invocation Log", interactive=False)

    send = gr.Button("Send")
    send.click(
        fn=run_agent_stream,
        inputs=[user_input],
        outputs=[log_output, agent_output],
        concurrency_limit=2,
    )

if __name__ == "__main__":
    demo.launch()
