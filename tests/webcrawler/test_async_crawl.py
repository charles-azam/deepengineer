import pytest
from deepengineer.common_path import DATA_DIR
from deepengineer.webcrawler.async_crawl import (
    crawl4ai_extract_markdown_of_url_async,
    download_pdf_async,
    download_pdf_or_arxiv_pdf_async,
)
from deepengineer.webcrawler.testing import ARXIV_URL, URL_PDF, URL_WIKIPEDIA


@pytest.mark.playwright
@pytest.mark.asyncio
async def test_crawl4ai_extract_markdown_of_url_async():
    markdown = await crawl4ai_extract_markdown_of_url_async(URL_WIKIPEDIA)
    assert isinstance(markdown, str)
    assert "Graphite-moderated reactor" in markdown

@pytest.mark.asyncio
async def test_download_pdf_async():
    output_path = DATA_DIR / "temp.pdf"
    output_path.unlink(missing_ok=True)
    pdf_path = await download_pdf_async(URL_PDF, output_path=output_path)
    assert pdf_path == output_path
    assert output_path.exists()


@pytest.mark.asyncio
async def test_arxiv_download_pdf_async():
    output_path = DATA_DIR / "temp.pdf"
    output_path.unlink(missing_ok=True)
    assert not output_path.exists()
    pdf_path = await download_pdf_or_arxiv_pdf_async(ARXIV_URL, output_path=output_path)
    assert pdf_path == output_path
    assert output_path.exists()
