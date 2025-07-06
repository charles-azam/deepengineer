from deepengineer.webcrawler.async_search import linkup_search_async, tavily_search_async, arxiv_search_async, pubmed_search_async, sciencedirect_search_async, scientific_search_async
from deepengineer.webcrawler.async_crawl import crawl4ai_extract_markdown_of_url_async, arxiv_download_pdf_async, download_pdf_async
from deepengineer.webcrawler.pdf_utils import get_table_of_contents_per_page_pdf
from typing import Callable
from smolagents.tools import get_json_schema

def print_function_signature_smolagents(tool_function: Callable):
    tool_json_schema = get_json_schema(tool_function)["function"]


    # Set the class attributes
    print("name: ", tool_json_schema["name"])
    print("description: ", tool_json_schema["description"])
    print("inputs: ", tool_json_schema["parameters"]["properties"])
    print("output_type: ", tool_json_schema["return"]["type"])

print_function_signature_smolagents(get_table_of_contents_per_page_pdf)