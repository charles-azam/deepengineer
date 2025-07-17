import gradio as gr
import time
from deepengineer.backend.gradio_tools import run_agent_stream
from deepengineer.common_path import DATA_DIR

# Custom CSS for hardware engineering theme
custom_css = """
.gradio-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.main-header {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: white;
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.main-header h1 {
    margin: 0;
    font-size: 2.5rem;
    font-weight: 700;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.main-header p {
    margin: 0.5rem 0 0 0;
    font-size: 1.1rem;
    opacity: 0.9;
}

.input-container {
    background: transparent;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 1rem;
}

.log-container {
    background: transparent;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 2rem;
}

.log-header {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
    padding: 0.5rem;
    background: var(--background-fill-secondary);
    border-radius: 5px;
}

.log-icon {
    margin-right: 0.5rem;
    color: var(--body-text-color);
}

.log-title {
    font-weight: 600;
    color: var(--body-text-color);
    margin: 0;
}

.processing-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    background: linear-gradient(135deg, #28a745, #20c997);
    color: white;
    border-radius: 10px;
    margin-bottom: 1rem;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.7; }
    100% { opacity: 1; }
}

.spinner {
    border: 0.1875rem solid #f3f3f3;
    border-top: 0.1875rem solid #3498db;
    border-radius: 50%;
    width: 1.25rem;
    height: 1.25rem;
    animation: spin 1s linear infinite;
    margin-right: 0.5rem;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.response-container {
    background: var(--background-fill-primary);
    border: 1px solid var(--border-color-primary);
    border-radius: 10px;
    padding: 1.5rem;
    margin-top: 1rem;
}

.send-button {
    background: linear-gradient(135deg, #007bff, #0056b3) !important;
    color: white !important;
    border: none !important;
    padding: 0.5rem 1.5rem !important;
    border-radius: 0.5rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0.125rem 0.5rem rgba(0,123,255,0.3) !important;
    min-width: 7.5rem !important;
    max-width: 12.5rem !important;
}

.send-button:hover {
    transform: translateY(-0.0625rem) !important;
    box-shadow: 0 0.25rem 0.75rem rgba(0,123,255,0.4) !important;
}

.send-button:disabled {
    background: #6c757d !important;
    transform: none !important;
    box-shadow: none !important;
}

.log-text {
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    line-height: 1.4;
    color: var(--body-text-color);
    background: var(--background-fill-secondary);
    border: 0.0625rem solid var(--border-color-primary);
    border-radius: 0.3125rem;
    padding: 1rem;
    max-height: 18.75rem;
    overflow-y: auto;
}

.log-entry {
    margin-bottom: 0.5rem;
    padding: 0.25rem 0;
    border-bottom: 1px solid var(--border-color-primary);
}

.log-entry:last-child {
    border-bottom: none;
}

.timestamp {
    color: var(--body-text-color-subdued);
    font-size: 0.8rem;
}

.tool-name {
    color: #007bff;
    font-weight: 600;
}

.tool-description {
    color: var(--body-text-color);
}

.hardware-icon {
    font-size: 2rem;
    margin-right: 1rem;
}

/* Dark mode specific adjustments */
.dark .input-container {
    background: transparent;
}

.dark .log-container {
    background: transparent;
}

.dark .response-container {
    background: var(--background-fill-primary);
    border-color: var(--border-color-primary);
}

.dark .log-text {
    background: var(--background-fill-secondary);
    border-color: var(--border-color-primary);
    color: var(--body-text-color);
}

.dark .log-header {
    background: var(--background-fill-secondary);
}

.dark .log-title {
    color: var(--body-text-color);
}

.dark .log-icon {
    color: var(--body-text-color);
}

.dark .timestamp {
    color: var(--body-text-color-subdued);
}

.dark .tool-description {
    color: var(--body-text-color);
}

.model-selector-compact {
    background: transparent;
    border: none;
    padding: 0;
    margin-bottom: 0.5rem;
}

.model-selector-compact .gr-dropdown {
    background: var(--background-fill-primary);
    color: var(--body-text-color);
    border: 0.0625rem solid var(--border-color-primary);
    border-radius: 0.375rem;
    padding: 0.25rem 0.5rem;
    font-size: 0.9rem;
    max-width: 12.5rem !important;
}

.model-selector-compact .gr-dropdown:hover {
    background: var(--background-fill-secondary);
    border-color: var(--border-color-accent);
}

.model-selector-compact .gr-dropdown .gr-dropdown-label {
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 0.25rem;
}
"""

def format_log_entry(log_text):
    """Format log entries with timestamps and better structure"""
    if not log_text:
        return ""
    
    lines = log_text.split('\n')
    formatted_lines = []
    
    for line in lines:
        if line.strip():
            # Add timestamp and format tool calls
            timestamp = time.strftime("%H:%M:%S")
            if "Tool:" in line or "tool:" in line:
                formatted_lines.append(f"<div class='log-entry'><span class='timestamp'>[{timestamp}]</span> <span class='tool-name'>🔧 {line.strip()}</span></div>")
            elif "Searching" in line or "searching" in line:
                formatted_lines.append(f"<div class='log-entry'><span class='timestamp'>[{timestamp}]</span> <span class='tool-name'>🔍 {line.strip()}</span></div>")
            elif "Processing" in line or "processing" in line:
                formatted_lines.append(f"<div class='log-entry'><span class='timestamp'>[{timestamp}]</span> <span class='tool-name'>⚙️ {line.strip()}</span></div>")
            elif "Drawing" in line or "drawing" in line:
                formatted_lines.append(f"<div class='log-entry'><span class='timestamp'>[{timestamp}]</span> <span class='tool-name'>🎨 {line.strip()}</span></div>")
            else:
                formatted_lines.append(f"<div class='log-entry'><span class='timestamp'>[{timestamp}]</span> <span class='tool-description'>{line.strip()}</span></div>")
    
    return "".join(formatted_lines)

def run_agent_with_ui(user_input: str, model_id: str):
    """Enhanced agent runner with better UI feedback"""
    if not user_input.strip():
        return "", ""
    
    # Initialize empty outputs
    log_buffer = ""
    agent_output = ""
    
    # Stream from the agent
    for agent_result, log_result in run_agent_stream(user_input, model_id):
        if log_result:
            log_buffer = log_result
        if agent_result:
            agent_output = agent_result
        
        # Format the log for display
        formatted_log = format_log_entry(log_buffer)
        
        yield agent_output, formatted_log

# Create the Gradio interface
with gr.Blocks(css=custom_css, title="DeepDraft - Hardware Engineering Assistant") as demo:
    
    # Header with hardware engineering theme
    with gr.Row():
        gr.HTML("""
            <div class="main-header">
                <h1>🔧 DeepDraft</h1>
                <p>Advanced Hardware Engineering Assistant</p>
                <p>Powered by AI-driven analysis and visualization</p>
            </div>
        """)
    
    # Model selection (compact)
    with gr.Row():
        with gr.Column(scale=1):
            model_selector = gr.Dropdown(
                choices=[
                    ("🤖 Mistral Medium", "mistral/mistral-medium-latest"),
                    ("🧠 DeepSeek Reasoner", "deepseek/deepseek-reasoner"),
                    ("🚀 DeepSeek Chat", "deepseek/deepseek-chat"),
                    ("⚡ Mistral Small", "mistral/mistral-small-latest"),
                ],
                value="mistral/mistral-medium-latest",
                label="🤖 AI Model",
                info="Choose the AI model for analysis",
                elem_classes=["model-selector-compact"],
                scale=1
            )
    
    # Main input section
    with gr.Row():
        with gr.Column(scale=3):
            gr.HTML('<div class="input-container">')
            user_input = gr.Textbox(
                label="🔍 Describe your hardware engineering query",
                placeholder="e.g., 'Design a thermal management system for a high-power LED array' or 'Analyze the stress distribution in a mechanical bracket'",
                lines=3,
                max_lines=5
            )
            gr.HTML('</div>')
    
    # Send button
    with gr.Row():
        send_button = gr.Button("🚀 Launch Analysis", variant="primary", elem_classes=["send-button"])
    
    # Processing indicator (hidden by default)
    processing_indicator = gr.HTML(
        """
        <div class="processing-indicator" style="display: none;">
            <div class="spinner"></div>
            <strong>DeepDraft is analyzing your request...</strong>
        </div>
        """,
        visible=False
    )
    
    # Log output section
    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML("""
                <div class="log-container">
                    <div class="log-header">
                        <span class="log-icon">📊</span>
                        <h3 class="log-title">Analysis Progress</h3>
                    </div>
                </div>
            """)
            log_output = gr.HTML(
                value="<div class='log-text'>Ready to analyze your hardware engineering query...</div>",
                elem_classes=["log-text"]
            )
    
    # Agent response section
    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML("""
                <div class="response-container">
                    <h3>🎯 Analysis Results</h3>
                </div>
            """)
            agent_output = gr.Markdown(
                value="Enter your query above to begin the analysis.",
                elem_classes=["response-container"]
            )
    
    # Event handlers
    def on_send_click(user_input, model_id):
        if not user_input.strip():
            return "", "", gr.HTML(visible=False)
        
        # Show processing indicator
        processing_html = """
        <div class="processing-indicator">
            <div class="spinner"></div>
            <strong>DeepDraft is analyzing your request...</strong>
        </div>
        """
        return "", "", gr.HTML(processing_html, visible=True)
    
    def on_generate_complete(agent_result, log_result):
        # Hide processing indicator when complete
        return agent_result, log_result, gr.HTML(visible=False)
    
    # Connect the button click
    send_button.click(
        fn=on_send_click,
        inputs=[user_input, model_selector],
        outputs=[agent_output, log_output, processing_indicator]
    ).then(
        fn=run_agent_with_ui,
        inputs=[user_input, model_selector],
        outputs=[agent_output, log_output],
        concurrency_limit=10
    ).then(
        fn=on_generate_complete,
        inputs=[agent_output, log_output],
        outputs=[agent_output, log_output, processing_indicator]
    )

if __name__ == "__main__":
    demo.launch(
        allowed_paths=[DATA_DIR],
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
