"""
Character-based chunking with configurable size and overlap. Preserves order and metadata.
"""
from dataclasses import dataclass
from typing import List


@dataclass
class Chunk:
    """One text chunk with metadata."""

    chunk_id: str
    chunk_index: int
    text: str
    start_char: int
    end_char: int
    source_id: str
    file_name: str


def _chunk_id(source_id: str, index: int) -> str:
    return f"{source_id}_{index}"


def chunk_text(
    text: str,
    source_id: str,
    file_name: str,
    chunk_size: int,
    overlap: int,
) -> List[Chunk]:
    """
    Split text into overlapping chunks by character count. Trims each chunk.
    Overlap must be < chunk_size; otherwise overlap is ignored.
    Caller should normalize text before chunking.
    """
    if not text or not text.strip():
        return []

    if overlap >= chunk_size:
        overlap = 0
    if chunk_size <= 0:
        chunk_size = 500

    chunks: List[Chunk] = []
    start = 0
    index = 0

    while start < len(text):
        end = start + chunk_size
        piece = text[start:end]
        # Prefer breaking at a newline or space near end
        if end < len(text):
            last_newline = piece.rfind("\n")
            if last_newline > chunk_size // 2:
                piece = piece[: last_newline + 1]
                end = start + last_newline + 1
            else:
                last_space = piece.rfind(" ")
                if last_space > chunk_size // 2:
                    piece = piece[: last_space + 1]
                    end = start + last_space + 1
        chunk_text_trimmed = piece.strip()
        if chunk_text_trimmed:
            chunks.append(
                Chunk(
                    chunk_id=_chunk_id(source_id, index),
                    chunk_index=index,
                    text=chunk_text_trimmed,
                    start_char=start,
                    end_char=end,
                    source_id=source_id,
                    file_name=file_name,
                )
            )
            index += 1
        start = end - overlap if overlap > 0 else end

    return chunks
