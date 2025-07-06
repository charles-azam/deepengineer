from deepengineer.webcrawler.pdf_utils import convert_pdf_to_markdown_async, convert_ocr_response_to_markdown, find_in_pdf, get_table_of_contents_per_page_pdf, get_markdown_by_page_numbers
from mistralai import OCRResponse
from deepengineer.common_path import DATA_DIR
import pytest

def load_mock_ocr_response() -> OCRResponse:
    with open(DATA_DIR / "report_thermal_neutron.json", "r") as f:
        return OCRResponse.model_validate_json(f.read())


@pytest.mark.expensive
@pytest.mark.asyncio
async def test_convert_pdf_to_markdown_async():
    pdf_path = DATA_DIR / "report_thermal_neutron.pdf"
    assert pdf_path.exists()
    ocr_response = await convert_pdf_to_markdown_async(pdf_path)
    markdown = convert_ocr_response_to_markdown(ocr_response)
    assert isinstance(ocr_response, OCRResponse)
    assert len(ocr_response.pages) == 16
    assert "where each cylinder represent" in markdown
    

def test_table_of_contents_per_page_pdf():
    ocr_response = load_mock_ocr_response()
    table_of_contents = get_table_of_contents_per_page_pdf(ocr_response)
    assert "References - Page 15" in table_of_contents

def test_find_in_pdf():
    ocr_response = load_mock_ocr_response()
    page_numbers = find_in_pdf(ocr_response, "where each cylinder represent")
    assert page_numbers == [7]

def test_get_markdown_by_page_numbers():
    ocr_response = load_mock_ocr_response()
    page_numbers = [7, 15]
    markdown = get_markdown_by_page_numbers(ocr_response, page_numbers)
    assert "Page 7" in markdown
    assert "Page 15" in markdown
    assert "References" in markdown
    assert "where each cylinder represent" in markdown