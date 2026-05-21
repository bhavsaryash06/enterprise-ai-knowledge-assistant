DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 150


def split_text_into_chunks(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[dict]:
    if not text or not text.strip():
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    chunks = []
    start_index = 0
    chunk_number = 1

    while start_index < len(text):
        end_index = min(start_index + chunk_size, len(text))
        chunk_text = text[start_index:end_index].strip()

        if chunk_text:
            chunks.append(
                {
                    "chunk_number": chunk_number,
                    "start_index": start_index,
                    "end_index": end_index,
                    "text": chunk_text,
                    "text_length": len(chunk_text),
                }
            )

        if end_index == len(text):
            break

        start_index = end_index - chunk_overlap
        chunk_number += 1

    return chunks