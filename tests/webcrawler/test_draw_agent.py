import pytest
from deepengineer.deepsearch.draw_agent import (
    draw_image_agent,
    multiple_steps_draw_image_agent,
)
from deepengineer.common_path import DATA_DIR
from pathlib import Path


@pytest.mark.expensive
def test_draw_image_agent():
    prompt = """Propose moi un schéma très détaillé d'un réacteur nucléaire hélium graphite."""
    output_path = Path(DATA_DIR) / "figure.png"
    output_path.unlink(missing_ok=True)
    output_path = draw_image_agent(prompt, output_path, multiple_steps=False)
    assert output_path.exists()


@pytest.mark.skip(reason="This function is not working yet")
def test_run_agent_step_by_step():
    prompt = """Propose moi un schéma très détaillé d'un réacteur nucléaire hélium graphite."""
    output_path = Path(DATA_DIR) / "figure.png"
    output_path.unlink(missing_ok=True)
    output_path = multiple_steps_draw_image_agent(prompt, output_path)
    assert output_path.exists()
