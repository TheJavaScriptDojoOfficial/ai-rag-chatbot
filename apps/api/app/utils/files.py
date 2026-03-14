"""
Safe file scanning for document ingestion. Filters by extension, size, and hidden/system files.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

# Common hidden/system prefixes and names to skip
SKIP_PREFIXES = (".", "__")
SKIP_NAMES = frozenset({"thumbs.db", ".ds_store"})


@dataclass
class ScannedFile:
    """Structured info for one scanned file."""

    file_path: str
    file_name: str
    extension: str
    size_bytes: int
    size_mb: float


def _is_safe_path(root: Path, full_path: Path) -> bool:
    """Ensure path is under root (no traversal escape)."""
    try:
        full_path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def scan_docs_folder(
    base_path: str,
    allowed_extensions: List[str],
    max_file_size_mb: float,
    recursive: bool = True,
) -> List[ScannedFile]:
    """
    Scan folder for supported documents. Returns list of ScannedFile.
    Skips hidden/system files and oversized files. Paths are normalized and
    kept under base_path.
    """
    root = Path(base_path).resolve()
    if not root.is_dir():
        return []

    allowed = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in allowed_extensions}
    max_bytes = int(max_file_size_mb * 1024 * 1024)
    results: List[ScannedFile] = []

    for path in root.rglob("*") if recursive else root.iterdir():
        if not path.is_file():
            continue
        if not _is_safe_path(root, path):
            continue

        name = path.name.lower()
        if name.startswith(SKIP_PREFIXES) or name in SKIP_NAMES:
            continue

        ext = path.suffix.lower()
        if ext not in allowed:
            continue

        try:
            size_bytes = path.stat().st_size
        except OSError:
            continue

        if size_bytes > max_bytes:
            continue

        results.append(
            ScannedFile(
                file_path=str(path),
                file_name=path.name,
                extension=ext,
                size_bytes=size_bytes,
                size_mb=round(size_bytes / (1024 * 1024), 2),
            )
        )

    return sorted(results, key=lambda f: f.file_path)
