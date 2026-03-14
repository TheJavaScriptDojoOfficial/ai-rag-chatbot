"""
Conservative text normalization for ingestion: whitespace, blank lines, trim.
Does not change meaning.
"""
import re


def normalize_text(text: str) -> str:
    """
    Normalize whitespace and clean formatting. Conservative:
    - collapse multiple spaces/tabs to single space
    - collapse 3+ newlines to double newline
    - strip leading/trailing whitespace per line and overall
    - remove repeated empty-looking fragments
    """
    if not text or not text.strip():
        return ""

    # Per-line: strip and collapse internal spaces
    lines = [re.sub(r"[ \t]+", " ", line.strip()) for line in text.splitlines()]
    # Drop fully empty lines but preserve paragraph breaks
    filtered = []
    prev_empty = False
    for line in lines:
        is_empty = not line
        if is_empty and prev_empty:
            continue
        filtered.append(line)
        prev_empty = is_empty

    # Join with single newline; collapse many newlines into double
    joined = "\n".join(filtered)
    joined = re.sub(r"\n{3,}", "\n\n", joined)
    return joined.strip()
