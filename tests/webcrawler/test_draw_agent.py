import pytest
from deepengineer.deepsearch.draw_agent import (
    draw_image_agent,
    multiple_steps_draw_image_agent,
    SaveMatplotlibFigTool,
)
from deepengineer.common_path import DATA_DIR
from pathlib import Path
from smolagents import CodeAgent, LiteLLMModel


@pytest.mark.expensive
def test_draw_image_agent():
    prompt = """Propose moi un schéma très détaillé d'un réacteur nucléaire hélium graphite."""
    output_path = Path(DATA_DIR) / "figure.png"
    output_path.unlink(missing_ok=True)
    output_path = draw_image_agent(prompt, output_path, multiple_steps=False)
    assert output_path.exists()


def test_save_matplotlib_fig_tool():
    model = LiteLLMModel(model_id="mistral/mistral-medium-latest")
    agent = CodeAgent(
        tools=[SaveMatplotlibFigTool(output_dir=Path(DATA_DIR))],
        model=model,
        additional_authorized_imports=[
            "matplotlib.*",
            "numpy.*",
            "pandas.*",
            "seaborn.*",
        ],
        max_steps=20,
        verbosity_level=2,
    )
    agent.run(
        """
              Propose moi un schéma très détaillé d'un réacteur nucléaire hélium graphite.
              Save the figure as figure.png. Return a markdown string where you explain what you did and then include the image.
              """
    )
    assert (Path(DATA_DIR) / "figure.png").exists()


test_save_matplotlib_fig_tool()


@pytest.mark.skip(reason="This function is not working yet")
def test_run_agent_step_by_step():
    prompt = """Propose moi un schéma très détaillé d'un réacteur nucléaire hélium graphite."""
    output_path = Path(DATA_DIR) / "figure.png"
    output_path.unlink(missing_ok=True)
    output_path = multiple_steps_draw_image_agent(prompt, output_path)
    assert output_path.exists()
