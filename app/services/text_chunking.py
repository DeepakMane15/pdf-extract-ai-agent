"""Clean extracted text and split into fixed-size overlapping character chunks."""

import re


def strip_null_bytes(text: str) -> str:
    """Remove ASCII NUL (0x00). PostgreSQL TEXT columns reject this byte."""
    return text.replace('\x00', '')


def clean_text(text: str) -> str:
    """Normalize whitespace, strip control chars, collapse excessive newlines."""
    text = strip_null_bytes(text)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.splitlines()]
    text = '\n'.join(line for line in lines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def chunk_fixed_overlap(
    text: str,
    chunk_size: int,
    overlap: int,
) -> list[tuple[str, int, int]]:
    """
    Split `text` into segments of at most `chunk_size` characters, advancing by
    (chunk_size - overlap) between chunks. Returns (content, start_char, end_char) per chunk.
    """
    if chunk_size <= 0:
        return []
    if overlap < 0:
        overlap = 0
    if overlap >= chunk_size:
        overlap = max(0, chunk_size // 4)

    n = len(text)
    if n == 0:
        return []

    step = chunk_size - overlap
    if step <= 0:
        step = chunk_size

    out: list[tuple[str, int, int]] = []
    start = 0
    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end]
        out.append((chunk, start, end))
        if end >= n:
            break
        start += step

    return out
