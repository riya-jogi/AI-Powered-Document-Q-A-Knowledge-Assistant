"""
Document text extraction, cleaning, and chunking service
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path

import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PageContent:
    page_number: int
    text: str


@dataclass
class TextChunk:
    content: str
    page_number: int | None
    chunk_index: int
    token_count: int
    metadata: dict


class DocumentProcessor:
    """Extract, clean, and chunk document content."""

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def process_file(self, file_path: str, file_type: str) -> tuple[list[TextChunk], int]:
        """
        Process a document file and return chunks plus page count.

        Returns:
            Tuple of (chunks, total_pages)
        """
        file_type = file_type.lower()
        if file_type == "pdf":
            pages = self._extract_pdf(file_path)
        elif file_type == "txt":
            pages = self._extract_txt(file_path)
        elif file_type == "docx":
            pages = self._extract_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        chunks = self._chunk_pages(pages)
        total_pages = len(pages) if file_type == "pdf" else 1
        return chunks, total_pages

    def _extract_pdf(self, file_path: str) -> list[PageContent]:
        """Extract text from PDF with page numbers using PyMuPDF."""
        pages: list[PageContent] = []
        try:
            with fitz.open(file_path) as doc:
                for page_num, page in enumerate(doc, start=1):
                    text = page.get_text("text")
                    cleaned = self._clean_text(text)
                    if cleaned.strip():
                        pages.append(PageContent(page_number=page_num, text=cleaned))
        except Exception as e:
            logger.error(f"Failed to extract PDF {file_path}: {e}")
            raise ValueError(f"Failed to extract text from PDF: {e}") from e

        if not pages:
            raise ValueError("No text content found in PDF")

        return pages

    def _extract_txt(self, file_path: str) -> list[PageContent]:
        """Extract text from a plain text file."""
        try:
            content = Path(file_path).read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            raise ValueError(f"Failed to read text file: {e}") from e

        cleaned = self._clean_text(content)
        if not cleaned.strip():
            raise ValueError("Text file is empty")

        return [PageContent(page_number=1, text=cleaned)]

    def _extract_docx(self, file_path: str) -> list[PageContent]:
        """Extract text from DOCX file."""
        try:
            from docx import Document as DocxDocument

            doc = DocxDocument(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            content = "\n\n".join(paragraphs)
        except ImportError as e:
            raise ValueError("DOCX support requires python-docx package") from e
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {e}") from e

        cleaned = self._clean_text(content)
        if not cleaned.strip():
            raise ValueError("No text content found in DOCX")

        return [PageContent(page_number=1, text=cleaned)]

    def _clean_text(self, text: str) -> str:
        """Clean extracted text while preserving meaningful structure."""
        text = text.replace("\x00", "")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _chunk_pages(self, pages: list[PageContent]) -> list[TextChunk]:
        """Split page content into overlapping chunks with metadata."""
        chunks: list[TextChunk] = []
        chunk_index = 0

        for page in pages:
            page_chunks = self.splitter.split_text(page.text)
            for chunk_text in page_chunks:
                if not chunk_text.strip():
                    continue
                chunks.append(
                    TextChunk(
                        content=chunk_text,
                        page_number=page.page_number,
                        chunk_index=chunk_index,
                        token_count=len(chunk_text.split()),
                        metadata={"page_number": page.page_number},
                    )
                )
                chunk_index += 1

        return chunks


document_processor = DocumentProcessor()
