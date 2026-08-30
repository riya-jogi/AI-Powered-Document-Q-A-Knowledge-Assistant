"""Tests for document text processing"""

from app.services.document_processor import DocumentProcessor


def test_clean_text():
    processor = DocumentProcessor()
    result = processor._clean_text("Hello   world\n\n\n\nTest")
    assert "Hello world" in result
    assert "\n\n\n" not in result


def test_chunk_pages():
    from app.services.document_processor import PageContent

    processor = DocumentProcessor()
    pages = [PageContent(page_number=1, text="This is a test document. " * 50)]
    chunks = processor._chunk_pages(pages)
    assert len(chunks) >= 1
    assert chunks[0].page_number == 1
