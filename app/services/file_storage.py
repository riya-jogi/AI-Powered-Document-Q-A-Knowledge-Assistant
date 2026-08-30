"""
File storage service for handling document uploads
"""

import uuid
from pathlib import Path
from typing import Optional, Tuple

from fastapi import HTTPException, UploadFile

from app.core.config import settings
from app.core.file_utils import (
    get_mime_type,
    sanitize_filename,
    validate_file_size,
    validate_file_type,
    validate_filename,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class FileStorageService:
    """Service for handling file storage operations."""

    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self._ensure_upload_directory()

    def _ensure_upload_directory(self):
        """Ensure upload directory exists."""
        try:
            self.upload_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Upload directory: {self.upload_dir}")
        except Exception as e:
            logger.error(f"Failed to create upload directory: {e}")
            raise

    def _get_user_upload_dir(self, user_id: Optional[int]) -> Path:
        """Return the directory associated with a user, if provided."""
        if user_id is None:
            return self.upload_dir
        user_dir = self.upload_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def _generate_unique_filename(self, original_filename: str) -> str:
        """
        Generate a unique filename to prevent conflicts.

        Args:
            original_filename: Original filename from upload

        Returns:
            Unique filename
        """
        safe_name = sanitize_filename(original_filename)
        file_extension = Path(safe_name).suffix.lower()
        stem = Path(safe_name).stem or "document"
        unique_id = str(uuid.uuid4())
        return f"{stem}-{unique_id}{file_extension}"

    async def save_uploaded_file(
        self,
        file: UploadFile,
        user_id: Optional[int] = None,
    ) -> Tuple[str, str, int]:
        """
        Save uploaded file to disk with validation.

        Args:
            file: FastAPI UploadFile object
            user_id: Optional user ID for user-specific storage

        Returns:
            Tuple of (saved_filename, file_path, file_size)

        Raises:
            HTTPException: If file validation fails
        """
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        # Validate filename
        is_valid, error_msg = validate_filename(file.filename)
        if not is_valid:
            logger.warning(f"Invalid filename: {file.filename} - {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)

        # Validate file type
        is_valid, error_msg = validate_file_type(file.filename)
        if not is_valid:
            logger.warning(f"Invalid file type: {file.filename} - {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)

        # Read file content to get size
        file_content = await file.read()
        file_size = len(file_content)

        # Validate file size
        is_valid, error_msg = validate_file_size(file_size)
        if not is_valid:
            logger.warning(f"Invalid file size: {file.filename} - {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)

        # Generate unique filename and store in a user-scoped directory.
        saved_filename = self._generate_unique_filename(file.filename)
        target_dir = self._get_user_upload_dir(user_id)
        file_path = target_dir / saved_filename

        # Save file
        try:
            with open(file_path, "wb") as handle:
                handle.write(file_content)

            logger.info(f"File saved successfully: {saved_filename} ({file_size} bytes)")
            return saved_filename, str(file_path), file_size

        except Exception as e:
            logger.error(f"Failed to save file {saved_filename}: {e}")
            raise HTTPException(status_code=500, detail="Failed to save file")

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage.

        Args:
            file_path: Path to the file to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                path.unlink()
                logger.info(f"File deleted: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False

    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Get information about a stored file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information or None if file doesn't exist
        """
        try:
            path = Path(file_path)
            if not path.exists() or not path.is_file():
                return None

            stat = path.stat()
            return {
                "filename": path.name,
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "exists": True,
            }
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            return None


# Global file storage service instance
file_storage = FileStorageService()