"""
File validation utilities for document uploads
"""

import os
import re
from typing import Optional, Tuple

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Allowed file types and their MIME types
ALLOWED_FILE_TYPES = {
    'pdf': 'application/pdf',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'txt': 'text/plain',
}

# Maximum file size in bytes from settings
MAX_FILE_SIZE = settings.MAX_FILE_SIZE


def validate_file_type(filename: str) -> Tuple[bool, Optional[str]]:
    """
    Validate file type based on extension.

    Args:
        filename: Name of the file to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename:
        return False, "No filename provided"

    # Ensure filename is a string
    if not isinstance(filename, str):
        filename = str(filename)

    # Get file extension
    parts = filename.rsplit('.', 1) if '.' in filename else [filename]
    file_extension = parts[1].lower() if len(parts) > 1 else ''

    if not file_extension:
        return False, "File has no extension"

    # Check if file type is allowed
    if file_extension not in ALLOWED_FILE_TYPES:
        allowed_types = ', '.join(ALLOWED_FILE_TYPES.keys())
        return False, f"File type '{file_extension}' not allowed. Allowed types: {allowed_types}"

    return True, None


def validate_file_size(file_size: int) -> Tuple[bool, Optional[str]]:
    """
    Validate file size against maximum allowed size.

    Args:
        file_size: Size of the file in bytes

    Returns:
        Tuple of (is_valid, error_message)
    """
    if file_size > MAX_FILE_SIZE:
        max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
        return False, f"File size exceeds maximum allowed size of {max_size_mb:.1f}MB"

    if file_size == 0:
        return False, "File is empty"

    return True, None


def validate_filename(filename: str) -> Tuple[bool, Optional[str]]:
    """
    Validate filename for security and compatibility.

    Args:
        filename: Name of the file to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename:
        return False, "No filename provided"

    # Ensure filename is a string
    if not isinstance(filename, str):
        filename = str(filename)

    # Reject obvious path traversal, absolute paths, and Windows drive letters.
    if filename in {'.', '..'}:
        return False, "Invalid filename: reserved name"
    if '..' in filename or '/' in filename or '\\' in filename:
        return False, "Invalid filename: path traversal detected"
    if re.match(r"^[A-Za-z]:", filename):
        return False, "Invalid filename: absolute path not allowed"
    if filename.startswith(os.sep) or filename.startswith('/') or filename.startswith('\\'):
        return False, "Invalid filename: absolute path not allowed"

    # Check for null bytes
    if '\x00' in filename:
        return False, "Invalid filename: null character detected"

    # Check length
    if len(filename) > 255:
        return False, "Filename too long (max 255 characters)"

    return True, None


def get_mime_type(filename: str) -> str:
    """
    Get MIME type for a given filename.

    Args:
        filename: Name of the file

    Returns:
        MIME type string
    """
    # Ensure filename is a string
    if not isinstance(filename, str):
        filename = str(filename)

    # Get file extension
    parts = filename.rsplit('.', 1) if '.' in filename else [filename]
    file_extension = parts[1].lower() if len(parts) > 1 else ''

    return ALLOWED_FILE_TYPES.get(file_extension, 'application/octet-stream')


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    if not filename:
        return ""

    # Remove path components while keeping extension and basename
    filename = os.path.basename(filename)

    # Replace spaces and unsafe characters with underscores.
    filename = filename.replace(' ', '_')
    filename = re.sub(r'[^A-Za-z0-9._-]', '_', filename)
    filename = re.sub(r'_+', '_', filename).strip('_')

    if not filename:
        return "document"

    return filename