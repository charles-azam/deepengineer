from deepengineer.webcrawler.utils import sanitize_filename
from deepengineer.common_path import DATA_DIR
from deepengineer.webcrawler.async_search import SearchResult, SearchResponse
import asyncio
from mistralai import OCRResponse
from deepengineer.webcrawler.async_crawl import download_pdf_or_arxiv_pdf_async, crawl4ai_extract_markdown_of_url_async
from deepengineer.webcrawler.pdf_utils import convert_raw_markdown_to_ocr_response
from deepengineer.webcrawler.pdf_utils import convert_pdf_to_markdown_async
 
class DataBase():
    def __init__(self):
        self.urls_to_markdown: dict[str, OCRResponse] = {}
    
    @staticmethod
    def preprocess_url(url: str) -> str:
        """Preprocess the url to make it a valid url."""
        if "arxiv.org/abs/" in url:
            return url.replace("arxiv.org/abs/", "arxiv.org/pdf/")
        else:
            return url
        
    def crawl_url(self, url: str) -> str:
        """Crawl the url, if the url is a pdf, download the pdf and save and return the markdown."""
        url = self.preprocess_url(url)
        if "pdf" in url:
            output_path = (DATA_DIR / sanitize_filename(url)).with_suffix(".pdf")
            pdf_path = asyncio.run(download_pdf_or_arxiv_pdf_async(url, output_path=output_path))
            ocr_response = asyncio.run(convert_pdf_to_markdown_async(pdf_path))
        else:
            markdown = asyncio.run(crawl4ai_extract_markdown_of_url_async(url))
            ocr_response = convert_raw_markdown_to_ocr_response(markdown)
        self.urls_to_markdown[url] = ocr_response
        return ocr_response
        
    
    def get_markdown_of_url(self, url: str) -> OCRResponse:
        url = self.preprocess_url(url)
        if url in self.urls_to_markdown:
            return self.urls_to_markdown[url]
        else:
            return self.crawl_url(url)
    