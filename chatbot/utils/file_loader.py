import pdfplumber
import pytesseract
from bs4 import BeautifulSoup
import markdown
import logging

# Centralized logging configuration
logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path, enable_ocr=False, ocr_threshold=0.1):
    text = ""
    links = []

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text

                # Decide whether to use OCR based on text density
                if enable_ocr and len(page_text.strip()) / (page.width * page.height) < ocr_threshold:
                    image = page.to_image(resolution=300).original
                    ocr_text = pytesseract.image_to_string(image)
                    text += ocr_text

                # Extract hyperlinks from annotations
                if hasattr(page, 'annotations') and page.annotations:
                    for annot in page.annotations:
                        if annot.get("Subtype") == "/Link":
                            uri = annot.get("URI")
                            if uri:
                                links.append(uri)

    except Exception as e:
        logger.error(f"Error extracting text from PDF {file_path}: {e}")

    return text, links

def extract_text_from_markdown(file_path):
    text = ""
    links = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            html_content = markdown.markdown(content)
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text()

            # Extract hyperlinks
            for a_tag in soup.find_all('a', href=True):
                link_text = a_tag.get_text(strip=True)
                href = a_tag['href']
                links.append({'text': link_text, 'url': href})

    except Exception as e:
        logger.error(f"Error processing markdown {file_path}: {e}")

    return text, links
