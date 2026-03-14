"""
Load text from PDF, Markdown, and TXT files. Returns structured document with metadata.
"""
import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pypdf import PdfReader

logger = logging.getLogger(__name__)


@dataclass
class LoadedDocument:
    """Structured document after loading."""

    source_id: str
    file_name: str
    file_path: str
    extension: str
    text: str
    page_count: Optional[int]
    loader_type: str


def _source_id(file_path: str) -> str:
    """Stable id from path."""
    return hashlib.sha256(file_path.encode("utf-8")).hexdigest()[:16]


def load_pdf(path: str) -> Optional[LoadedDocument]:
    """Extract text from PDF page by page. Returns None on parse failure."""
    p = Path(path)
    try:
        reader = PdfReader(path)
        page_count = len(reader.pages)
        parts = []
        for page in reader.pages:
            try:
                t = page.extract_text()
                if t:
                    parts.append(t)
            except Exception as e:
                logger.warning("PDF page extract failed for %s: %s", path, e)
        text = "\n\n".join(parts) if parts else ""
        return LoadedDocument(
            source_id=_source_id(path),
            file_name=p.name,
            file_path=path,
            extension=p.suffix.lower(),
            text=text,
            page_count=page_count,
            loader_type="pdf",
        )
    except Exception as e:
        logger.warning("PDF load failed for %s: %s", path, e)
        return None


def load_text_file(path: str, loader_type: str) -> Optional[LoadedDocument]:
    """Load raw text from .md or .txt. Returns None on read failure."""
    p = Path(path)
    try:
        raw = p.read_text(encoding="utf-8", errors="replace")
        return LoadedDocument(
            source_id=_source_id(path),
            file_name=p.name,
            file_path=path,
            extension=p.suffix.lower(),
            text=raw,
            page_count=None,
            loader_type=loader_type,
        )
    except Exception as e:
        logger.warning("Text file load failed for %s: %s", path, e)
        return None


def load_document(file_path: str, extension: str) -> Optional[LoadedDocument]:
    """
    Load one document by path and extension. Returns LoadedDocument or None
    if unsupported or parse fails.
    """
    ext = extension.lower() if extension.startswith(".") else f".{extension.lower()}"
    if ext == ".pdf":
        return load_pdf(file_path)
    if ext in (".md", ".markdown"):
        return load_text_file(file_path, "markdown")
    if ext == ".txt":
        return load_text_file(file_path, "txt")
    return None
