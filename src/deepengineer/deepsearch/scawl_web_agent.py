from smolagents import CodeAgent, Tool, LiteLLMModel, tool
from deepengineer.webcrawler.async_search import (
    linkup_search_async, arxiv_search_async, 
    pubmed_search_async, scientific_search_async,
)
from deepengineer.webcrawler.pdf_utils import get_table_of_contents_per_page_markdown, convert_ocr_response_to_markdown, get_markdown_by_page_numbers, find_in_markdown
from mistralai import OCRResponse
from enum import Enum
import asyncio
from deepengineer.webcrawler.async_search import SearchResponse


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
    
    def __init__(self, markdown: OCRResponse):
        super().__init__()
        self.markdown: OCRResponse = markdown
        self.table_of_contents: str = get_table_of_contents_per_page_markdown(self.markdown)
        
    def forward(self, url: str) -> str:
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

def create_web_search_agent(model_id="deepseek/deepseek-chat"):
    """Create a web search agent with search, crawling, and PDF analysis capabilities."""
    
    model = LiteLLMModel(model_id=model_id)

    # Web search and crawling tools
    WEB_SEARCH_TOOLS = [
        TavilySearchTool(),
        LinkupSearchTool(),
        ArxivSearchTool(),
        PubmedSearchTool(),
        ScientificSearchTool(),
        CrawlUrlTool(),
        DownloadPdfTool(),
        ArxivDownloadPdfTool(),
    ]
    
    web_search_agent = CodeAgent(
        model=model,
        tools=WEB_SEARCH_TOOLS,
        max_steps=20,
        verbosity_level=2,
        planning_interval=4,
        name="web_search_agent",
        description="""A team member that can search the web, crawl URLs, download PDFs, and analyze documents.""",
    )
    
    web_search_agent.prompt_templates["managed_agent"]["task"] += """
    You can search the web using various APIs (Tavily, Linkup, arXiv, PubMed, ScienceDirect).
    You can crawl URLs to extract markdown content.
    You can download PDFs from URLs or arXiv and store them in the data/pdfs directory.
    For PDF analysis, you'll need to first download the PDF and then use the markdown analysis tools.
    """

    return web_search_agent

def create_web_search_agent_with_pdf_analysis(markdown: OCRResponse, model_id="deepseek/deepseek-chat"):
    """Create a web search agent that also includes PDF analysis capabilities."""
    
    model = LiteLLMModel(model_id=model_id)

    # Web search and crawling tools
    WEB_SEARCH_TOOLS = [
        TavilySearchTool(),
        LinkupSearchTool(),
        ArxivSearchTool(),
        PubmedSearchTool(),
        ScientificSearchTool(),
        CrawlUrlTool(),
        DownloadPdfTool(),
        ArxivDownloadPdfTool(),
    ]
    
    # PDF analysis tools (if markdown is provided)
    PDF_ANALYSIS_TOOLS = [
        GetTableOfContentsTool(markdown),
        GetMarkdownTool(markdown),
        GetPagesContentTool(markdown),
        FindInMarkdownTool(markdown),
    ]
    
    all_tools = WEB_SEARCH_TOOLS + PDF_ANALYSIS_TOOLS
    
    web_search_agent = CodeAgent(
        model=model,
        tools=all_tools,
        max_steps=20,
        verbosity_level=2,
        planning_interval=4,
        name="web_search_agent_with_pdf_analysis",
        description="""A team member that can search the web, crawl URLs, download PDFs, and analyze the provided PDF document.""",
        additional_authorized_imports=["numpy", "matplotlib", "scipy", "sympy", "pandas", ],
    )
    
    web_search_agent.prompt_templates["managed_agent"]["task"] += """
    You can search the web using various APIs (Linkup, arXiv, PubMed, ScienceDirect).
    You can crawl URLs to extract markdown content.
    You can download PDFs from URLs or arXiv and store them in the data/pdfs directory.
    You can analyze the provided PDF document using the markdown analysis tools.
    """

    return web_search_agent
