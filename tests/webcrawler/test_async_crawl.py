import pytest
from deepengineer.webcrawler.async_crawl import (
    crawl4ai_extract_markdown_of_url_async,
    download_pdf_async,
    arxiv_download_pdf_async,
)
from mistralai import OCRResponse
from deepengineer.webcrawler.pdf_tools import convert_pdf_to_markdown_async
from deepengineer.webcrawler.testing import URL_WIKIPEDIA, URL_PDF, ARXIV_URL
from deepengineer.common_path import DATA_DIR

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
    pdf_path = await arxiv_download_pdf_async(ARXIV_URL, output_path=output_path)
    assert pdf_path == output_path
    assert output_path.exists()

@pytest.mark.expensive
@pytest.mark.asyncio
async def test_convert_pdf_to_markdown_async():
    pdf_path = DATA_DIR / "report_thermal_neutron.pdf"
    assert pdf_path.exists()
    markdown, ocr_response = await convert_pdf_to_markdown_async(pdf_path)
    assert isinstance(ocr_response, OCRResponse)
    assert len(ocr_response.pages) == 16
    assert isinstance(markdown, str)
    assert "where each cylinder represent" in markdown
