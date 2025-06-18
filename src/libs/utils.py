import re


def clear_text(text: str) -> str:
    cleaned_text = re.sub(r'\[\d+\]', '', text)
    url_pattern = (
        r'\b(?:https?://|www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?\b')
    cleaned_text = re.sub(url_pattern, '', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text
