"""
drawing_agent.py (rev 3)
A smolagents‑powered CodeAgent that grants the model **full matplotlib.pyplot**
control *plus* a single high‑level `save_fig` tool. The tool must be called at
the end of each drawing sequence to persist the artwork, while a callback still
captures a snapshot for chat‑time previews.
"""

from __future__ import annotations

from io import BytesIO
from time import sleep

import matplotlib

matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt
from PIL import Image

from smolagents import CodeAgent, LiteLLMModel, tool
from smolagents.agents import ActionStep

# ---------------------------------------------------------------------------
# Drawing tool (the *only* one): save_fig
# ---------------------------------------------------------------------------


@tool
def save_fig() -> str:
    """Save the current matplotlib figure to *path*.
    Save fig takes no arguments. The output path is hardcoded to "figure.png".
    """
    path = "figure.png"
    if not plt.get_fignums():
        raise RuntimeError(
            "No active figure to save; create one before calling save_fig()."
        )
    plt.savefig(path, bbox_inches="tight")
    return f"Figure saved to {path}."


# ---------------------------------------------------------------------------
# Callback: snapshot the figure after each executed step
# ---------------------------------------------------------------------------


def _capture_snapshot(memory_step: ActionStep, agent: CodeAgent) -> None:
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


# ---------------------------------------------------------------------------
# Agent initialisation
# ---------------------------------------------------------------------------

model_id = "deepseek/deepseek-chat"
model = LiteLLMModel(model_id=model_id)

agent = CodeAgent(
    tools=[save_fig],  # only one explicit tool
    model=model,
    additional_authorized_imports=["*"],
    step_callbacks=[_capture_snapshot],
    max_steps=20,
    verbosity_level=2,
)

# ---------------------------------------------------------------------------
# System prompt injected before every user request
# ---------------------------------------------------------------------------

matplotlib_instructions = r"""
You may use the entire **matplotlib** API.
Workflow
--------
1. Construct your figure with ordinary matplotlib calls.
2. **Once the figure is complete, call `save_fig()` and `final_answer()`.** This is the
   *only* external tool you have and must be invoked exactly once per final
   graphic.
3. Do **not** call `plt.show()`; a callback captures a PNG automatically.
4. Keep code blocks concise and avoid GUI back‑end imports (TkAgg, Qt, etc.).
"""

# ---------------------------------------------------------------------------
# Example CLI usage
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import numpy as np

    prompt = "Propose moi un schéma simplifié d'un réacteur nucléaire à eau pressurisée (PWR) avec un schéma de l'installation."
    result = agent.run(prompt + matplotlib_instructions)
    print("Final output:\n", result)
