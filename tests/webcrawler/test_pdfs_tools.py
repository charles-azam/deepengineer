from deepengineer.webcrawler.pdf_tools import convert_pdf_to_markdown_async
from mistralai import OCRResponse
from deepengineer.common_path import DATA_DIR
import pytest


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
