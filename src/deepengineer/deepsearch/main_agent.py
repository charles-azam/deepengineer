from deepengineer.deepsearch.scawl_web_agent import (
    create_web_search_agent,
    SearchTool,
    ArxivSearchTool,
    PubmedSearchTool,
    ScientificSearchTool,
    GetTableOfContentsTool,
    GetMarkdownTool,
    GetPagesContentTool,
    FindInMarkdownTool,
)
from deepengineer.deepsearch.draw_agent import SaveMatplotlibFigTool
from deepengineer.webcrawler.crawl_database import DataBase
from deepengineer.common_path import DATA_DIR
from smolagents import CodeAgent, LiteLLMModel
import random
from pathlib import Path
import queue


def create_output_image_path(random_name_images: int | None = None):
    random_name_images = random_name_images or random.randint(1000000, 9999999)
    output_image_path = Path(DATA_DIR) / f"images_{random_name_images}"
    output_image_path.mkdir(parents=True, exist_ok=True)
    return output_image_path


def create_main_search_agent(
    model_id="deepseek/deepseek-reasoner",
    database: DataBase | None = None,
    log_queue: queue.Queue | None = None,
    output_image_path: Path | None = None,
):
    """
    Simple agent that can search the web and answer the question. This is much faster and better for simple questions that do not require deep research.
    """

    model = LiteLLMModel(model_id=model_id)
    if database is None:
        database = DataBase()

    output_image_path = output_image_path or DATA_DIR / "images"
    output_image_path.mkdir(parents=True, exist_ok=True)

    # Web search and crawling tools
    WEB_SEARCH_TOOLS = [
        SearchTool(
            log_queue=log_queue,
        ),
        ArxivSearchTool(
            log_queue=log_queue,
        ),
        ScientificSearchTool(
            log_queue=log_queue,
        ),
        GetTableOfContentsTool(log_queue=log_queue, database=database),
        GetMarkdownTool(log_queue=log_queue, database=database),
        GetPagesContentTool(log_queue=log_queue, database=database),
        FindInMarkdownTool(log_queue=log_queue, database=database),
        SaveMatplotlibFigTool(log_queue=log_queue, output_dir=output_image_path),
    ]

    search_agent = CodeAgent(
        model=model,
        tools=WEB_SEARCH_TOOLS,
        max_steps=20,
        verbosity_level=2,
        additional_authorized_imports=[
            "matplotlib.*",
            "numpy.*",
            "pandas.*",
            "seaborn.*",
            "scipy.*",
            "sympy.*",
        ],
    )
    return search_agent


def main_search(task: str, log_queue: queue.Queue | None = None, model_id: str = "mistral/mistral-medium-latest") -> tuple[str, Path]:
    print(f"Using model: {model_id}")
    output_image_path = create_output_image_path()
    MAIN_PROMPT = """
You are DeepDraft, an advanced research and analysis agent specialized in deep technical research, data visualization, and comprehensive information synthesis. You have access to powerful tools for web search, document analysis, and data visualization.

You will be given a task to complete. This task is related to engineering, science, and technology. I want you to answer the question with a very detailed answer. The output should be written in markdown and include sources and images.

## Your Capabilities

### **Python and scientific reasoning**
You will have to answer the question as an engineer. Make hypothesis, test them, and draw conclusions. When in doubt, go back to the basic equations and laws of physics. Make simple models that you can test using python.
You are a coding agent so you can use python to test your hypothesis.
You have access to these libraries: matplotlib, numpy, pandas, seaborn, scipy, sympy.
You do not have access to any other library.

### Web searching:
You have the tools to search the web using Linkup API for comprehensive research with sourced answers. You can also search arXiv, PubMed, and ScienceDirect, download the documents and extract the relevant information.

### **Data Visualization Tools**
- You can always use the tool `SaveMatplotlibFigTool` to save a figure at the end of a matplotlib code block. You can then include the figure in your final answer.

## Answer format
You must answer the question in markdown format. Remember, you are a coding agent and you can pass the answer only by using the `final_answer("your markdown answer")` tool.
Also, if you want to include images in your answer, you MUST include the image in the markdown like this: ![title](image_name.png).

You have one question to answer. It is paramount that you provide a correct answer.
Give it all you can: I know for a fact that you have access to all the relevant tools to solve it and find the correct answer (the answer does exist).
Failure or 'I cannot answer' or 'None found' will not be tolerated, success will be rewarded.
Run verification steps if that's needed, you must make sure you find the correct answer! Here is the task:
{task}
"""
    agent = create_main_search_agent(
        model_id=model_id,
        log_queue=log_queue,
        output_image_path=output_image_path,
    )
    answer = agent.run(MAIN_PROMPT.format(task=task))

    return answer, output_image_path


if __name__ == "__main__":
    main_search(
        """
    Search a paper called "High Energy Physics Opportunities Using Reactor Antineutrinos" on arXiv, download it and extract the table of contents
    """
    )
