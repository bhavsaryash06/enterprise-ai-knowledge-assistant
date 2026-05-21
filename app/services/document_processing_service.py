from app.services.document_text_extractor import extract_text_from_document
from app.services.text_cleaner import clean_text


def process_document_text(file_path: str) -> dict:
    raw_text = extract_text_from_document(file_path)
    cleaned_text = clean_text(raw_text)

    return {
        "file_path": file_path,
        "raw_text_length": len(raw_text),
        "cleaned_text_length": len(cleaned_text),
        "text": cleaned_text,
    }