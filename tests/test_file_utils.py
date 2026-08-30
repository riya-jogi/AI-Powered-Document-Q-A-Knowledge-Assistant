"""Tests for file validation utilities"""

from app.core.file_utils import (
    validate_file_type,
    validate_file_size,
    validate_filename,
    get_mime_type,
)


def test_validate_file_type_pdf():
    valid, error = validate_file_type("document.pdf")
    assert valid is True
    assert error is None


def test_validate_file_type_invalid():
    valid, error = validate_file_type("malware.exe")
    assert valid is False
    assert "not allowed" in error


def test_validate_file_size():
    valid, _ = validate_file_size(1024)
    assert valid is True

    valid, error = validate_file_size(0)
    assert valid is False


def test_validate_filename_path_traversal():
    valid, error = validate_filename("../etc/passwd")
    assert valid is False


def test_get_mime_type():
    assert get_mime_type("test.pdf") == "application/pdf"
    assert get_mime_type("notes.txt") == "text/plain"
