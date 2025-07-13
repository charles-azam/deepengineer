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


def _create_output_image_path():
    random_name_images = random.randint(1000000, 9999999)
    output_image_path = Path(DATA_DIR) / f"images_{random_name_images}"
    output_image_path.mkdir(parents=True, exist_ok=True)
    return output_image_path


def create_main_deep_search_agent(
    main_model_id="deepseek/deepseek-reasoner",
    web_search_model_id="deepseek/deepseek-reasoner",
) -> tuple[CodeAgent, Path]:
    """
    Deepsearch agent use multiple agents to answer the question.
    """
    main_model = LiteLLMModel(model_id=main_model_id)

    database = DataBase()
    web_search_agent = create_web_search_agent(
        model_id=web_search_model_id, database=database
    )

    output_image_path = _create_output_image_path()

    manager_agent = CodeAgent(
        model=main_model,
        tools=[SaveMatplotlibFigTool(output_dir=output_image_path)],
        max_steps=12,
        verbosity_level=2,
        additional_authorized_imports=[
            "matplotlib.*",
            "numpy.*",
            "pandas.*",
            "seaborn.*",
            "scipy.*",
            "sympy.*",
        ],
        planning_interval=4,
        managed_agents=[web_search_agent],
    )

    return manager_agent, output_image_path


def main_deep_search(task: str):

    MAIN_PROMPT = """
You are DeepDraft, an advanced research and analysis agent specialized in deep technical research, data visualization, and comprehensive information synthesis. You have access to powerful tools for web search, document analysis, and data visualization.

You will be given a task to complete. This task is related to engineering, science, and technology. I want you to answer the question with a very detailed answer. The output should be written in markdown and include sources and images.

## Your Capabilities

### **Python and scientific reasoning**
You will have to answer the question as an engineer. Make hypothesis, test them, and draw conclusions. When in doubt, go back to the basic equations and laws of physics. Make simple models that you can test using python.
You are a coding agent so you can use python to test your hypothesis.
You have access to these libraries: matplotlib, numpy, pandas, seaborn, scipy, sympy.
You do not have access to any other library.

### Managed Agent: **web_search_agent**
This agent can search the web using Linkup API for comprehensive research with sourced answers. It can also search arXiv, PubMed, and ScienceDirect, download the documents and extract the relevant information.
When calling this agent, you should provide a detailed task, he is extremely powerful.


### **Data Visualization Tools**
- You can always use the tool `SaveMatplotlibFigTool` to save a figure at the end of a matplotlib code block. You can then include the figure in your final answer.

You have one question to answer. It is paramount that you provide a correct answer.
Give it all you can: I know for a fact that you have access to all the relevant tools to solve it and find the correct answer (the answer does exist).
Failure or 'I cannot answer' or 'None found' will not be tolerated, success will be rewarded.
Run verification steps if that's needed, you must make sure you find the correct answer! Here is the task:
{task}
"""
    agent, output_image_path = create_main_deep_search_agent()

    answer = agent.run(MAIN_PROMPT.format(task=task))

    print(answer)


def create_main_search_agent(
    model_id="deepseek/deepseek-reasoner", database: DataBase | None = None
):
    """
    Simple agent that can search the web and answer the question. This is much faster and better for simple questions that do not require deep research.
    """

    model = LiteLLMModel(model_id=model_id)
    if database is None:
        database = DataBase()

    output_image_path = _create_output_image_path()

    # Web search and crawling tools
    WEB_SEARCH_TOOLS = [
        SearchTool(),
        ArxivSearchTool(),
        PubmedSearchTool(),
        ScientificSearchTool(),
        GetTableOfContentsTool(database),
        GetMarkdownTool(database),
        GetPagesContentTool(database),
        FindInMarkdownTool(database),
        SaveMatplotlibFigTool(output_dir=output_image_path),
    ]

    search_agent = CodeAgent(
        model=model,
        tools=WEB_SEARCH_TOOLS,
        max_steps=20,
        verbosity_level=2,
    )
    return search_agent


def main_search(task: str):
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

You have one question to answer. It is paramount that you provide a correct answer.
Give it all you can: I know for a fact that you have access to all the relevant tools to solve it and find the correct answer (the answer does exist).
Failure or 'I cannot answer' or 'None found' will not be tolerated, success will be rewarded.
Run verification steps if that's needed, you must make sure you find the correct answer! Here is the task:
{task}
"""
    agent = create_main_search_agent()
    answer = agent.run(MAIN_PROMPT.format(task=task))
    print(answer)


if __name__ == "__main__":
    main_search(
        """
    Search a paper called "High Energy Physics Opportunities Using Reactor Antineutrinos" on arXiv, download it and extract the table of contents
    """
    )
