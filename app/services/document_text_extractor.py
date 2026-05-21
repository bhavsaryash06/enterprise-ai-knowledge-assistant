from pathlib import Path

from pypdf import PdfReader


def extract_text_from_txt(file_path: str) -> str:
    path = Path(file_path)

    with open(path, "r", encoding="utf-8") as file:
        text = file.read()

    return text


def extract_text_from_pdf(file_path: str) -> str:
    path = Path(file_path)
    reader = PdfReader(str(path))

    extracted_text_parts: list[str] = []

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            extracted_text_parts.append(page_text)

    return "\n".join(extracted_text_parts)


def extract_text_from_document(file_path: str) -> str:
    path = Path(file_path)
    file_extension = path.suffix.lower()

    if file_extension == ".txt":
        return extract_text_from_txt(file_path)

    if file_extension == ".pdf":
        return extract_text_from_pdf(file_path)

    raise ValueError(
        f"Unsupported file type: {file_extension}. Only .txt and .pdf files are supported."
    )