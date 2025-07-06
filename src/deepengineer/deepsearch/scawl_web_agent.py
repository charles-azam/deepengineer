from smolagents import CodeAgent, Tool, LiteLLMModel
from deepengineer.webcrawler.async_search import (
    linkup_search_async, tavily_search_async, arxiv_search_async, 
    pubmed_search_async, scientific_search_async,
)
from deepengineer.webcrawler.async_crawl import (
    crawl4ai_extract_markdown_of_url_async, arxiv_download_pdf_async, download_pdf_async
)
from deepengineer.webcrawler.pdf_utils import get_table_of_contents_per_page_markdown, convert_ocr_response_to_markdown, get_markdown_by_page_numbers, find_in_markdown
from mistralai import OCRResponse
from enum import Enum
from pathlib import Path
import asyncio

class ToolNames(Enum):
    # Search tools
    TAVILY_SEARCH = "tavily_search"
    LINKUP_SEARCH = "linkup_search"
    ARXIV_SEARCH = "arxiv_search"
    PUBMED_SEARCH = "pubmed_search"
    SCIENCEDIRECT_SEARCH = "sciencedirect_search"
    SCIENTIFIC_SEARCH = "scientific_search"

    # Crawling tools
    CRAWL_URL = "crawl_url"
    DOWNLOAD_PDF = "download_pdf"
    ARXIV_DOWNLOAD_PDF = "arxiv_download_pdf"
    
    # PDF analysis tools (reusing from markdown agent)
    GET_TABLE_OF_CONTENTS = "get_table_of_contents"
    GET_MARKDOWN = "get_markdown"
    GET_PAGES_CONTENT = "get_pages_content"
    FIND_IN_MARKDOWN = "find_in_markdown"

class TavilySearchTool(Tool):
    name = ToolNames.TAVILY_SEARCH.value
    description = "Search the web using Tavily API. Good for general web searches with advanced features."
    inputs = {
        "search_query": {
            "type": "string",
            "description": "The search query to execute"
        },
    }
    output_type = "object"
    def forward(self, search_query: str) -> dict:
        result = asyncio.run(tavily_search_async(
            search_query=search_query,
        ))
        return result.model_dump()

class LinkupSearchTool(Tool):
    name = ToolNames.LINKUP_SEARCH.value
    description = "Search the web using Linkup API. Good for deep research with sourced answers."
    inputs = {
        "search_query": {
            "type": "string",
            "description": "The search query to execute"
        },
    }
    output_type = "object"
    
    def forward(self, search_query: str, depth: str = "standard", 
                output_type: str = "sourcedAnswer") -> dict:
        result = asyncio.run(linkup_search_async(
            search_query=search_query,
            depth=depth,
            output_type=output_type
        ))
        return result.model_dump()

class ArxivSearchTool(Tool):
    name = ToolNames.ARXIV_SEARCH.value
    description = "Search arXiv for academic papers and preprints."
    inputs = {
        "search_query": {
            "type": "string",
            "description": "The search query to execute on arXiv"
        }
    }
    output_type = "object"
    
    def forward(self, search_query: str) -> dict:
        result = asyncio.run(arxiv_search_async(search_query))
        return result.model_dump()

class PubmedSearchTool(Tool):
    name = ToolNames.PUBMED_SEARCH.value
    description = "Search PubMed for medical and scientific literature."
    inputs = {
        "search_query": {
            "type": "string",
            "description": "The search query to execute on PubMed"
        }
    }
    output_type = "object"
    
    def forward(self, search_query: str) -> dict:
        result = asyncio.run(pubmed_search_async(search_query))
        return result.model_dump()

class ScientificSearchTool(Tool):
    name = ToolNames.SCIENTIFIC_SEARCH.value
    description = "Search across multiple scientific domains: Wikipedia, arXiv, PubMed, and ScienceDirect."
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

class CrawlUrlTool(Tool):
    name = ToolNames.CRAWL_URL.value
    description = "Extract markdown content from a URL using crawl4ai."
    inputs = {
        "url": {
            "type": "string",
            "description": "The URL to crawl and extract markdown from"
        }
    }
    output_type = "string"
    
    def forward(self, url: str) -> str:
        return asyncio.run(crawl4ai_extract_markdown_of_url_async(url))

class DownloadPdfTool(Tool):
    name = ToolNames.DOWNLOAD_PDF.value
    description = "Download a PDF file from a URL and store it in the data directory."
    inputs = {
        "url": {
            "type": "string",
            "description": "The URL of the PDF to download"
        },
        "filename": {
            "type": "string",
            "description": "The filename to save the PDF as (without .pdf extension)"
        }
    }
    output_type = "string"
    
    def forward(self, url: str, filename: str) -> str:
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Create PDFs subdirectory
        pdfs_dir = data_dir / "pdfs"
        pdfs_dir.mkdir(exist_ok=True)
        
        output_path = pdfs_dir / f"{filename}.pdf"
        
        # Download the PDF
        result_path = asyncio.run(download_pdf_async(url, output_path))
        return f"PDF downloaded successfully to: {result_path}"

class ArxivDownloadPdfTool(Tool):
    name = ToolNames.ARXIV_DOWNLOAD_PDF.value
    description = "Download a PDF from arXiv by converting the abstract URL to PDF URL."
    inputs = {
        "url": {
            "type": "string",
            "description": "The arXiv abstract URL (e.g., https://arxiv.org/abs/1234.5678)"
        },
        "filename": {
            "type": "string",
            "description": "The filename to save the PDF as (without .pdf extension)"
        }
    }
    output_type = "string"
    
    def forward(self, url: str, filename: str) -> str:
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Create PDFs subdirectory
        pdfs_dir = data_dir / "pdfs"
        pdfs_dir.mkdir(exist_ok=True)
        
        output_path = pdfs_dir / f"{filename}.pdf"
        
        # Download the PDF
        result_path = asyncio.run(arxiv_download_pdf_async(url, output_path))
        return f"arXiv PDF downloaded successfully to: {result_path}"

# Reuse the markdown analysis tools from analyse_markdown_agent.py
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
    )
    
    web_search_agent.prompt_templates["managed_agent"]["task"] += """
    You can search the web using various APIs (Linkup, arXiv, PubMed, ScienceDirect).
    You can crawl URLs to extract markdown content.
    You can download PDFs from URLs or arXiv and store them in the data/pdfs directory.
    You can analyze the provided PDF document using the markdown analysis tools.
    """

    return web_search_agent
