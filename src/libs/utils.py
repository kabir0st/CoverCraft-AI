import re


def clear_text(text: str) -> str:
    # Remove markdown-style bold/italic
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)  # **bold** or __bold__
    text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)  # *italic* or _italic_

    text = re.sub(r'\[\d+\]', '', text)

    # Remove URLs
    text = re.sub(
        r'\b(?:https?://|www\.)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?\b', '',
        text)

    # Remove common types of quotation marks
    text = re.sub(r'[\"\'“”‘’]', '', text)

    text = re.sub(r'\([^)]*\)', '', text)

    # Remove ISBN mentions
    text = re.sub(r'\bISBN[:\s]*\d+[-\d]*', '', text, flags=re.IGNORECASE)

    # Remove extra non-alphabetic characters except periods, commas
    text = re.sub(r'[^a-zA-Z0-9.,\s]', '', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text
