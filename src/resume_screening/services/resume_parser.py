from functools import lru_cache
from io import BytesIO

from docling.datamodel.base_models import DocumentStream, InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from resume_screening.config import get_settings


@lru_cache
def get_document_converter() -> DocumentConverter:
    settings = get_settings()

    pdf_options = PdfPipelineOptions(
        artifacts_path=settings.docling_artifacts_path,
    )

    return DocumentConverter(
        allowed_formats=[
            InputFormat.PDF,
            InputFormat.DOCX,
        ],
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pdf_options,
            ),
        },
    )


def parse_resume_to_markdown(
    filename: str,
    content: bytes,
) -> str:
    document_stream = DocumentStream(
        name=filename,
        stream=BytesIO(content),
    )

    result = get_document_converter().convert(document_stream)

    return result.document.export_to_markdown()
