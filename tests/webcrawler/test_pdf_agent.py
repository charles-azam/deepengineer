from deepengineer.deepsearch.analyse_markdown_agent import create_agent, GetTableOfContentsTool, GetMarkdownTool, GetPagesContentTool, FindInPdfTool
from mistralai import OCRResponse
from deepengineer.common_path import DATA_DIR

def load_mock_ocr_response() -> OCRResponse:
    with open(DATA_DIR / "report_thermal_neutron.json", "r") as f:
        return OCRResponse.model_validate_json(f.read())


def test_pdf_agent():
    ocr_response = load_mock_ocr_response()
    pdf_agent = create_agent(ocr_response)
    assert pdf_agent is not None
    assert pdf_agent.name == "pdf_agent"
    assert pdf_agent.tools is not None
    assert len(pdf_agent.tools) == 4 + 1 # +1 for the final answer
    
    
    GetTableOfContentsTool(ocr_response).forward()
    GetMarkdownTool(ocr_response).forward()
    GetPagesContentTool(ocr_response).forward([1,2,3])
    FindInPdfTool(ocr_response).forward(["thermal neutron", "neutron"])
    pdf_agent.run("Give me a summary of the document.")

test_pdf_agent()

