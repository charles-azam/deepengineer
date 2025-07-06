"""
Simple agent to analyse a markdown, just to test some ideas.
"""

from smolagents import CodeAgent, tool, Tool, LiteLLMModel
from deepengineer.webcrawler.pdf_utils import get_markdown_by_page_numbers, get_table_of_contents_per_page_markdown, find_in_markdown, convert_ocr_response_to_markdown
from mistralai import OCRResponse
from enum import Enum

class ToolNames(Enum):
    GET_TABLE_OF_CONTENTS = "get_table_of_contents"
    GET_MARKDOWN = "get_markdown"
    GET_PAGES_CONTENT = "get_pages_content"
    FIND_IN_MARKDOWN = "find_in_markdown"

class GetTableOfContentsTool(Tool):
    name = ToolNames.GET_TABLE_OF_CONTENTS.value
    description = "Returns all of the titles in the document along with the page number they are on."
    inputs = {}
    output_type = "string"
    
    def __init__(self, markdown: OCRResponse):
        super().__init__()
        self.markdown: OCRResponse = markdown
        self.table_of_contents: str = get_table_of_contents_per_page_markdown(self.markdown)
        
    def forward(self) -> str:
        return self.table_of_contents
    
class GetMarkdownTool(Tool):
    name = ToolNames.GET_MARKDOWN.value
    description = f"Returns the markdown entire content of the document. Beware this might be too long to be useful, except for small documents, use {ToolNames.GET_PAGES_CONTENT.value} instead. You can use {ToolNames.GET_TABLE_OF_CONTENTS.value} to get the table of contents of the document including the number of pages."
    inputs = {}
    output_type = "string"
    
    def __init__(self, markdown: OCRResponse):
        super().__init__()
        self.markdown: OCRResponse = markdown
        self.markdown_content: str = convert_ocr_response_to_markdown(self.markdown)
        
    def forward(self) -> str:
        return self.markdown_content
    
    
class GetPagesContentTool(Tool):
    name = ToolNames.GET_PAGES_CONTENT.value
    description = f"Returns the content of the pages. You can use {ToolNames.GET_TABLE_OF_CONTENTS.value} to get the table of contents of the document including the number of pages. Expects a list of page numbers as integers as input."
    inputs = {
        "page_numbers": {
            "type": "array",
            "description": "The page numbers to get the content of."
        },
    }
    output_type = "string"
    
    def __init__(self, markdown: OCRResponse):
        super().__init__()
        self.markdown: OCRResponse = markdown

    def forward(self, page_numbers: list[int]) -> str:
        return get_markdown_by_page_numbers(self.markdown, page_numbers)
    
class FindInMarkdownTool(Tool):
    name = ToolNames.FIND_IN_MARKDOWN.value
    description = f"Finds the page numbers of the document that contain the search queries. If you are looking for a specific information, you can use this tool to find the page numbers of the document that contain the information and then use {ToolNames.GET_PAGES_CONTENT.value} to get the content of the pages."
    inputs = {
        "search_queries": {
            "type": "array",
            "description": "The search queries to find in the document. List of strings."
        }
    }
    output_type = "array"
    
    def __init__(self, markdown: OCRResponse):
        super().__init__()
        self.markdown: OCRResponse = markdown
    
    def forward(self, search_queries: list[str]) -> list[int]:
        return find_in_markdown(self.markdown, search_queries)


        
def create_agent(markdown: OCRResponse, model_id="deepseek/deepseek-chat"):
    
    """This agent is just a test and will not be used as is by the main agent."""

    model = LiteLLMModel(model_id=model_id)

    MARKDOWN_TOOLS = [
        GetTableOfContentsTool(markdown),
        GetMarkdownTool(markdown),
        GetPagesContentTool(markdown),
        FindInMarkdownTool(markdown),
    ]
    markdown_agent = CodeAgent(
        model=model,
        tools=MARKDOWN_TOOLS,
        max_steps=20,
        verbosity_level=2,
        planning_interval=4,
        name="markdown_agent",
        description="""A team member that can analyse a markdown.""",
    )
    markdown_agent.prompt_templates["managed_agent"]["task"] += """You can navigate to .txt online files."""

    return markdown_agent