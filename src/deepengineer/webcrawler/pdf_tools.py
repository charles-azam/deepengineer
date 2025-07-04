import os
from pathlib import Path
from pypdf import PdfReader, PdfWriter
import io
from pathlib import Path
from mistralai import Mistral
import os
from litellm import completion

from mistralai.models import OCRResponse
import yaml
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError
from litellm.exceptions import BadRequestError

# Define the size limit in bytes
MAX_SIZE_BYTES = 49 * 1024 * 1024


async def convert_pdf_to_markdown_async(
    pdf_path: Path,
    with_image_description: bool = False,
) -> tuple[str, OCRResponse]:
    
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
    return (
        _get_combined_markdown(
            ocr_response=ocr_response, with_image_description=with_image_description
        ),
        ocr_response,
    )


def _get_image_description_using_llm(
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


def _replace_images_in_markdown(markdown_str: str, images_dict: dict) -> str:
    """
    Replace image placeholders in markdown with base64-encoded images.

    Args:
        markdown_str: Markdown text containing image placeholders
        images_dict: Dictionary mapping image IDs to base64 strings

    Returns:
        Markdown text with images replaced by base64 data
    """
    for img_name, base64_str in images_dict.items():
        print(f"Processing image: {img_name}")
        try:
            image_description = _get_image_description_using_llm(base_64_str=base64_str)
        except RetryError:
            image_description = "Image not found"
        formatted_description = f"""> [Image {img_name} Replaced with Description Below]
> {image_description.replace('\n', '\n> ')}
"""
        markdown_str = markdown_str.replace(
            f"![{img_name}]({img_name})", formatted_description
        )
    return markdown_str


def _get_combined_markdown(
    ocr_response: OCRResponse, with_image_description: bool
) -> str:
    """
    Combine OCR text and images into a single markdown document.

    Args:
        ocr_response: Response from OCR processing containing text and images

    Returns:
        Combined markdown string with embedded images
    """

    markdowns: list[str] = []
    # Extract images from page
    for page in ocr_response.pages:
        # Replace image placeholders with actual images
        if with_image_description:
            image_data = {}
            for img in page.images:
                image_data[img.id] = img.image_base64
            page_description = _replace_images_in_markdown(page.markdown, image_data)
        else:
            page_description = page.markdown
        markdowns.append(page_description)

    return "\n\n".join(markdowns)

