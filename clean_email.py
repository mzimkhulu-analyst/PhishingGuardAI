import bs4
print(bs4.__version__)

from bs4 import BeautifulSoup
import re

def clean_email(text):
    # Parse HTML content
    soup = BeautifulSoup(text, "html.parser")
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    # Get text and decode HTML entities
    text = soup.get_text(separator=" ")
    # Remove URLs
    text = re.sub(r"http[s]?://\S+", "", text)
    # Normalize whitespace
    text = " ".join(text.split())
    return text