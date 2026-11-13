from unittest.mock import MagicMock

from resume_screening.services import resume_parser


def test_parse_resume_to_markdown_returns_exported_markdown(
    monkeypatch,
) -> None:
    document = MagicMock()
    document.export_to_markdown.return_value = (
        "# Jane Doe\n\n## Experience\n\nML Engineer"
    )

    result = MagicMock()
    result.document = document

    converter = MagicMock()
    converter.convert.return_value = result

    monkeypatch.setattr(
        resume_parser,
        "get_document_converter",
        lambda: converter,
    )

    markdown = resume_parser.parse_resume_to_markdown(
        "resume.pdf",
        b"fake pdf content",
    )

    converter.convert.assert_called_once()
    document.export_to_markdown.assert_called_once_with()

    assert markdown == "# Jane Doe\n\n## Experience\n\nML Engineer"
