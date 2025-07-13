from __future__ import annotations

from pathlib import Path
from io import BytesIO
from time import sleep

import matplotlib

matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt
from PIL import Image

from smolagents import CodeAgent, LiteLLMModel
from smolagents.agents import ActionStep
from smolagents import tool, Tool
from deepengineer.webcrawler.crawl_database import DataBase


def _find_and_save_matplotlib_figure(image_path: Path = Path("figure.png")) -> str:
    """Save the current matplotlib figure to *path*.
    Save fig takes no arguments. The output path is hardcoded to "figure.png".
    """
    if not plt.get_fignums():
        raise RuntimeError(
            "No active figure to save; create one before calling save_fig()."
        )
    plt.savefig(image_path, bbox_inches="tight")
    return f"Figure saved to {image_path}."


class SaveMatplotlibFigTool(Tool):
    name = "save_matplotlib_fig"
    description = """Save the current matplotlib figure to the current directory. Then plt.close() is called to clear the figure. The image is returned as a markdown string, use this markdown inside the final answer to include the image.
    """
    inputs = {
        "image_name": {
            "type": "string",
            "description": "The name of the image to save.",
        },
    }
    output_type = "string"

    def __init__(self, output_dir: Path):
        super().__init__()
        self.output_dir: Path = output_dir

    def forward(self, image_name: str) -> str:
        if not image_name.endswith(".png"):
            image_name = image_name + ".png"
        output_path = self.output_dir / image_name
        output_path.unlink(missing_ok=True)
        _find_and_save_matplotlib_figure(output_path)
        if output_path.exists():
            return f"![]({image_name})"
        else:
            return f"Error: The image {image_name} was not saved."


def _capture_snapshot(
    memory_step: ActionStep, agent: CodeAgent, image_path: Path = Path("figure.png")
) -> None:
    _find_and_save_matplotlib_figure(image_path)
    if not plt.get_fignums():
        return

    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img = Image.open(buf)

    for prev in agent.memory.steps:
        if (
            isinstance(prev, ActionStep)
            and prev.step_number <= memory_step.step_number - 2
        ):
            prev.observations_images = None

    memory_step.observations_images = [img.copy()]
    buf.close()

    hint = "[snapshot: matplotlib figure captured]"
    memory_step.observations = (
        hint
        if memory_step.observations is None
        else memory_step.observations + "\n" + hint
    )


matplotlib_instructions_multiple_steps = r"""
You may use the entire **matplotlib** and **numpy** and **pandas** and **seaborn** API. Do not worry about saving the image, it is done automatically and you can't access the os library.

Between each step, the image is provided in memory. From step 2, you can use it to pass additional instructions to the model to improve the image.

Workflow
--------
1. Construct your figure with ordinary matplotlib calls.
2. Wait another iteration, watch the image. If the image is correct call `final_answer() directly`. Otherwise, just do it again.
3. Do **not** call `plt.show()`; a callback captures a PNG automatically.
4. Keep code blocks concise and avoid GUI back‑end imports (TkAgg, Qt, etc.).

User instructions:
{user_instructions}
"""

matplotlib_instructions_single_step = r"""
You may use the entire **matplotlib** and **numpy** and **pandas** and **seaborn** API. Do not worry about saving the image, it is done automatically and you can't access the os library.

Workflow
--------
1. Construct your figure with ordinary matplotlib calls.
2. If the task is easy and you are confident that the image is correct, call `final_answer() directly`. Otherwise, wait another iteration to watch the image.
3. Do **not** call `plt.show()`; a callback captures a PNG automatically.
4. Keep code blocks concise and avoid GUI back‑end imports (TkAgg, Qt, etc.).  

User instructions:
{user_instructions}
"""


def draw_matplotlib_image_from_prompt(
    prompt: str,
    image_path: str = Path("figure.png"),
    model_id: str = "mistral/mistral-medium-latest",
    multiple_steps: bool = False,
) -> Path:
    model = LiteLLMModel(model_id=model_id)
    agent = CodeAgent(
        tools=[],
        model=model,
        additional_authorized_imports=[
            "matplotlib.*",
            "numpy.*",
            "pandas.*",
            "seaborn.*",
        ],
        step_callbacks=[
            lambda memory_step, agent: _capture_snapshot(memory_step, agent, image_path)
        ],
        max_steps=20,
        verbosity_level=2,
    )
    if multiple_steps:
        agent.run(
            matplotlib_instructions_multiple_steps.format(user_instructions=prompt)
        )
    else:
        agent.run(matplotlib_instructions_single_step.format(user_instructions=prompt))
    return image_path


class DrawImageTool(Tool):
    name = "draw_image"
    description = f"Draw an image based on a prompt. The image is saved in the current directory. The image is returned as a markdown image, use this markdown inside the final answer to include the image. You must be very specific in your prompt."
    inputs = {
        "prompt": {
            "type": "string",
            "description": """
    Draw an image based on a prompt. The image is saved in the current directory. The image is returned as a markdown image, use this markdown inside the final answer to include the image. 
    
    You must be very specific in your prompt. This tool has access to matplotlib, numpy, pandas, seaborn.
                   
                   """,
        },
        "image_name": {
            "type": "string",
            "description": "The name of the image to save.",
        },
    }
    output_type = "string"

    def __init__(self, output_dir: Path):
        super().__init__()
        self.output_dir: Path = output_dir

    def forward(self, prompt: str, image_name: str) -> str:
        if not image_name.endswith(".png"):
            image_name = image_name + ".png"
        output_path = draw_matplotlib_image_from_prompt(
            prompt, self.output_dir / image_name
        )
        if output_path.exists():
            return f"![]({image_name})"
        else:
            return f"Error: The image {image_name} was not saved."


def multiple_steps_draw_image_agent(
    prompt: str,
    image_path: str = Path("figure.png"),
    model_id: str = "mistral/mistral-medium-latest",
) -> Path:
    """
    The idea behind this function is to give to a multimodal agent the code and the image of the previous step to adapt it.
    """
    from smolagents import CodeAgent, ActionStep, TaskStep, Timing
    import time

    model = LiteLLMModel(model_id=model_id)
    agent = CodeAgent(
        tools=[],
        model=model,
        additional_authorized_imports=["matplotlib.*", "numpy.*"],
        step_callbacks=[
            lambda memory_step, agent: _capture_snapshot(memory_step, agent, image_path)
        ],
        max_steps=20,
        verbosity_level=2,
    )

    # Send the tools to the agent (no tools here)
    agent.python_executor.send_tools({**agent.tools})

    # Print the system prompt
    print(agent.memory.system_prompt)

    # Set the task
    task = prompt

    # You could modify the memory as needed here by inputting the memory of another agent.
    # agent.memory.steps = previous_agent.memory.steps

    # Let's start a new task!
    agent.memory.steps.append(TaskStep(task=task, task_images=[]))

    final_answer = None
    step_number = 1
    while final_answer is None and step_number <= 10:
        memory_step = ActionStep(
            step_number=step_number,
            observations_images=[],
            timing=Timing(start_time=time.time(), end_time=time.time()),
        )
        # Run one step.
        final_answer = agent.step(memory_step)
        agent.memory.steps.append(memory_step)
        step_number += 1
        _capture_snapshot(memory_step, agent, image_path)
        pass
        # Change the memory as you please!
        # For instance to update the latest step:
        # agent.memory.steps[-1] = ...

    print("The final answer is:", final_answer)

    return image_path
