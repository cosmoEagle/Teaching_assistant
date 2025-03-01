import re

from bs4 import BeautifulSoup


def extract_text_from_html(html_content: str) -> str:
    """
    Extract text from HTML content, handling various elements and cleaning.

    Args:
        html_content (str): The HTML content to extract text from.

    Returns:
        str: The text content extracted from the HTML, cleaned up.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    parts = []
    for element in soup.recursiveChildGenerator():
        if isinstance(element, str):
            parts.append(element.strip())
        elif element.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']:
            parts.append(element.get_text(separator=" ", strip=True))
        elif element.name == 'code': # Handle <code> tags specifically
            parts.append(f"```{element.get_text(strip=True)}```")  # Use markdown-like fences

    text = "\n".join(filter(None, parts))  # Join with newlines, removing empty strings
    text = re.sub(r'\n{3,}', '\n\n', text) # Reduce multiple newlines to two
    text = re.sub(r' +', ' ', text)     # Reduce multiple spaces to single space

    return text.strip()