import os
from pathlib import Path
from pypdf import PdfReader, PdfWriter
import io
from pathlib import Path
from mistralai import Mistral
import os
from litellm import completion

from mistralai.models import OCRResponse, OCRPageObject
import yaml
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError
from litellm.exceptions import BadRequestError

# Define the size limit in bytes
MAX_SIZE_BYTES = 49 * 1024 * 1024


async def convert_pdf_to_markdown_async(
    pdf_path: Path,
    with_image_description: bool = False,
) -> OCRResponse:
    
    mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

    uploaded_pdf = await mistral_client.files.upload_async(
        file={
            "file_name": "uploaded_file.pdf",
            "content": open(pdf_path, "rb"),
        },
        purpose="ocr",
    )

    signed_url = await mistral_client.files.get_signed_url_async(file_id=uploaded_pdf.id)

    ocr_response = await mistral_client.ocr.process_async(
        model="mistral-ocr-latest",
        document={"type": "document_url", "document_url": signed_url.url},
        include_image_base64=True,
    )
    print(f"Processing PDF: {pdf_path.name}")
    return ocr_response


def convert_ocr_response_to_markdown(
    ocr_response: OCRResponse
) -> str:
    markdowns: list[str] = []
    for page in ocr_response.pages:
        page_description = page.markdown
        markdowns.append(page_description)
        
    return "\n\n".join(markdowns)

def get_markdown_by_page_numbers(markdown: OCRResponse, page_numbers: list[int], get_full_content: bool = False) -> str:
    markdowns: list[str] = []
    page_numbers_to_get = set(page_numbers)
    if get_full_content:
        page_numbers_to_get = set(range(len(markdown.pages)))

    for page_number in page_numbers_to_get:
        markdowns.append(f"*Page {page_number}*\n{markdown.pages[page_number].markdown}")
    return "\n\n".join(markdowns)

def find_in_markdown(markdown: OCRResponse, search_queries: list[str] | str) -> list[int]:
    """
    Find the page numbers of the pdf that contain the search query.

    Args:
        markdown (OCRResponse): The markdown of the pdf.
        search_queries (list[str]): The search queries.

    Returns:
        list[int]: The page numbers of the pdf that contain the search query.
    """
    if isinstance(search_queries, str):
        search_queries = [search_queries]
    page_numbers: list[int] = []
    for page_number, page in enumerate(markdown.pages):
        for search_query in search_queries:
            if search_query.lower() in page.markdown.lower():
                page_numbers.append(page_number)
    return page_numbers

def get_table_of_contents_per_page_markdown(markdown: OCRResponse) -> str:
    """
    Get the table of contents of the pdf.
    
    Finds all the titles of the pdf to reconstruct the table of contents.
    
    Args:
        markdown (OCRResponse): The markdown of the pdf.

    Returns:
        str: The table of contents of the pdf.
    """
    title_to_page_number: dict[str, int] = {}
    for page_number, page in enumerate(markdown.pages):
        lines = page.markdown.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                title_to_page_number[line] = page_number

    table_of_contents = "\n".join([f"{title} - Page {page_number}" for title, page_number in title_to_page_number.items()])
    return table_of_contents

def convert_raw_markdown_to_ocr_response(raw_markdown: str) -> OCRResponse:
    # split by big title starting with # and then a space
    pages = raw_markdown.split("\n# ")
    return OCRResponse(pages=[OCRPageObject(markdown="# " + page, page_number=i) for i, page in enumerate(pages)])



def get_images_from_pdf(pdf_path: Path, image_ids: list[str]) -> list[str]:
    raise NotImplementedError("Not implemented")

    def get_image_description_using_llm(
        base_64_str: str, model: str = "mistral/mistral-small-latest"
    ) -> str | None:
        assert base_64_str.startswith("data:image/jpeg;base64")

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in detail:"},
                    {"type": "image_url", "image_url": {"url": base_64_str}},
                ],
            }
        ]
        try:
            response = completion(
                model=model,  # LiteLLM naming convention
                messages=messages,
                temperature=0.0,
                stream=False,
            )
            output = dict(response)["choices"][0].message.content
        except BadRequestError:
            output = ""
        return output

