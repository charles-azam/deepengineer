from smolagents import CodeAgent, Tool, LiteLLMModel, tool, ToolCallingAgent
from deepengineer.webcrawler.async_search import (
    linkup_search_async, arxiv_search_async, 
    pubmed_search_async, scientific_search_async,
)
from deepengineer.webcrawler.pdf_utils import get_table_of_contents_per_page_markdown, convert_ocr_response_to_markdown, get_markdown_by_page_numbers, find_in_markdown
from mistralai import OCRResponse
from enum import Enum
import asyncio
from deepengineer.webcrawler.async_search import SearchResponse
from deepengineer.webcrawler.crawl_database import DataBase

class ToolNames(Enum):
    # Search tools
    SEARCH_TOOL = "web search tool"
    ARXIV_SEARCH = "arxiv_search"
    PUBMED_SEARCH = "pubmed_search"
    SCIENCEDIRECT_SEARCH = "sciencedirect_search"
    SCIENTIFIC_SEARCH = "scientific_search"
    
    # Exploring link tools
    GET_TABLE_OF_CONTENTS = "get_table_of_contents_of_url"
    GET_MARKDOWN = "get_markdown_of_url"
    GET_PAGES_CONTENT = "get_pages_content"
    FIND_IN_MARKDOWN = "find_in_markdown"

def filter_search_results(search_response: SearchResponse, max_nb_results: int = 10) -> SearchResponse:
    search_response.search_results = search_response.search_results[:max_nb_results]
    return search_response


class SearchTool(Tool):
    name = ToolNames.SEARCH_TOOL.value
    description = f"""Search the web using Linkup API. Good for deep research with sourced answers.
    Linkup also provides an answer. This answer is not always correct, so you might want to check the sources.
    """
    inputs = {
        "search_query": {
            "type": "string",
            "description": "The search query to execute"
        },
    }
    output_type = "object"
    max_nb_results = 10
    
    def forward(self, search_query: str) -> SearchResponse:
        result = asyncio.run(linkup_search_async(
            search_query=search_query,
        ))
        return filter_search_results(result, SearchTool.max_nb_results)

class ArxivSearchTool(Tool):
    name = ToolNames.ARXIV_SEARCH.value
    description = """Search arXiv for academic papers and preprints with Linkup API.
    Linkup also provides an answer. This answer is not always correct, so you might want to check the sources.
    """
    inputs = {
        "search_query": {
            "type": "string",
            "description": "The search query to execute on arXiv"
        }
    }
    output_type = "object"
    
    def forward(self, search_query: str) -> SearchResponse:
        result = asyncio.run(arxiv_search_async(search_query))
        return filter_search_results(result, ArxivSearchTool.max_nb_results)

class PubmedSearchTool(Tool):
    name = ToolNames.PUBMED_SEARCH.value
    description = """Search PubMed for medical and scientific literature with Linkup API.
    Linkup also provides an answer. This answer is not always correct, so you might want to check the sources.
    """
    inputs = {
        "search_query": {
            "type": "string",
            "description": "The search query to execute on PubMed"
        }
    }
    output_type = "object"
    
    def forward(self, search_query: str) -> SearchResponse:
        result = asyncio.run(pubmed_search_async(search_query))
        return filter_search_results(result, PubmedSearchTool.max_nb_results)

class ScientificSearchTool(Tool):
    name = ToolNames.SCIENTIFIC_SEARCH.value
    description = """Search across multiple scientific domains: Wikipedia, arXiv, PubMed, and ScienceDirect.
    Linkup also provides an answer. This answer is not always correct, so you might want to check the sources.
    """
    inputs = {
        "search_query": {
            "type": "string",
            "description": "The search query to execute across scientific domains"
        }
    }
    output_type = "object"
    
    def forward(self, search_query: str) -> dict:
        result = asyncio.run(scientific_search_async(search_query))
        return result.model_dump()

URL_EXPLAINATION = """The URL can be be converted to a markdown. If the URL points to a PDF, the pdf is converted to markdown, otherwise the URL is crawled and the markdown is extracted. This markdown is split into pages that are numbered. You can use the page numbers to get the content of the pages."""

class GetTableOfContentsTool(Tool):
    name = ToolNames.GET_TABLE_OF_CONTENTS.value
    description = f"""Returns all of the titles in the document along with the page number they are on.
    {URL_EXPLAINATION}
    """
    inputs = {
        "url": {
            "type": "string",
            "description": "The URL to get the table of contents of."
        }
    }
    output_type = "string"
    
    def __init__(self, database: DataBase):
        super().__init__()
        self.database: DataBase = database
        
    def forward(self, url: str) -> str:
        markdown = self.database.get_markdown_of_url(url)
        table_of_contents: str = get_table_of_contents_per_page_markdown(markdown)
        return table_of_contents

class GetMarkdownTool(Tool):
    name = ToolNames.GET_MARKDOWN.value
    description = f"Returns in markdown entire content of the url. Beware this might be too long to be useful, except for small documents, use {ToolNames.GET_PAGES_CONTENT.value} instead. You can also use {ToolNames.GET_TABLE_OF_CONTENTS.value} first to get the table of contents of the document including the number of pages."
    inputs = {
        "url": {
            "type": "string",
            "description": "The URL to get the markdown of."
        }
    }
    output_type = "string"
    
    def __init__(self, database: DataBase):
        super().__init__()
        self.database: DataBase = database
        
    def forward(self, url: str) -> str:
        markdown = self.database.get_markdown_of_url(url)
        markdown_content: str = convert_ocr_response_to_markdown(markdown)
        return markdown_content

class GetPagesContentTool(Tool):
    name = ToolNames.GET_PAGES_CONTENT.value
    description = f"Returns the content of the pages. You can use {ToolNames.GET_TABLE_OF_CONTENTS.value} to get the table of contents of the url including the number of pages. Expects a list of page numbers as integers as input. {URL_EXPLAINATION}"
    inputs = {
        "url": {
            "type": "string",
            "description": "The URL to get the content of."
        },
        "page_numbers": {
            "type": "array",
            "description": "The page numbers to get the content of."
        },
    }
    output_type = "string"
    
    def __init__(self, database: DataBase):
        super().__init__()
        self.database: DataBase = database

    def forward(self, url: str, page_numbers: list[int]) -> str:
        markdown = self.database.get_markdown_of_url(url)
        return get_markdown_by_page_numbers(markdown, page_numbers)

class FindInMarkdownTool(Tool):
    name = ToolNames.FIND_IN_MARKDOWN.value
    description = f"Finds the page numbers of the url that contain the search queries. If you are looking for a specific information, you can use this tool to find the page numbers of the url that contain the information and then use {ToolNames.GET_PAGES_CONTENT.value} to get the content of the pages. {URL_EXPLAINATION}"
    inputs = {
        "url": {
            "type": "string",
            "description": "The URL to find in."
        },
        "search_queries": {
            "type": "array",
            "description": "The search queries to find in the url. List of strings."
        }
    }
    output_type = "array"
    
    def __init__(self, database: DataBase):
        super().__init__()
        self.database: DataBase = database
    
    def forward(self, url: str, search_queries: list[str]) -> list[int]:
        markdown = self.database.get_markdown_of_url(url)
        return find_in_markdown(markdown, search_queries)

def create_web_search_agent(model_id="deepseek/deepseek-chat"):
    """Create a web search agent with search, crawling, and PDF analysis capabilities."""
    
    model = LiteLLMModel(model_id=model_id)

    # Web search and crawling tools
    WEB_SEARCH_TOOLS = [
        SearchTool(),
        ArxivSearchTool(),
        PubmedSearchTool(),
        ScientificSearchTool(),
        GetTableOfContentsTool(),
        GetMarkdownTool(),
        GetPagesContentTool(),
        FindInMarkdownTool(),
    ]
    
    web_search_agent = ToolCallingAgent(
        model=model,
        tools=WEB_SEARCH_TOOLS,
        max_steps=20,
        verbosity_level=2,
        planning_interval=4,
        name="web_search_agent",
        description="""A team member that can search the web, crawl URLs, download PDFs, and analyze documents.""",
    )
    
    return web_search_agent
