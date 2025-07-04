import aiofiles
import httpx
import crawl4ai
import os
from pathlib import Path

async def crawl4ai_extract_markdown_of_url_async(url: str) -> str:
    """Extract markdown content from a URL using crawl4ai."""
    async with crawl4ai.AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        return result.markdown
    
async def download_pdf_async(url: str, output_path: Path) -> str:
    """Download a PDF file from a URL."""
    timeout = httpx.Timeout(30.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
    async with aiofiles.open(output_path, "wb") as f:
        await f.write(response.content)
    return output_path

async def arxiv_download_pdf_async(url: str, output_path: Path) -> str:
    """Download a PDF from arXiv by converting the abstract URL to PDF URL."""
    # Extract the arXiv ID from the URL
    if "/abs/" in url:
        arxiv_id = url.split("/abs/")[1].rstrip("/")
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    else:
        # If it's already a PDF URL, use it as is
        pdf_url = url
    
    return await download_pdf_async(pdf_url, output_path)
