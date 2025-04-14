from agents import Agent, Runner, WebSearchTool, FileSearchTool, function_tool
from PyPDF2 import PdfReader
import io
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin




@function_tool
def read_pdf(pdf_url: str):
    """
    Downloads a PDF from the provided URL in memory,
    reads it using PyPDF2, and extracts the text.
    """
    response = requests.get(pdf_url)
    response.raise_for_status()  # Validate download
    pdf_bytes = io.BytesIO(response.content)
    reader = PdfReader(pdf_bytes)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


@function_tool
def look_for_pdf_files():
    """
    Goes to the specified URL, parses the page for PDF download links,
    and returns the full URL of the syllabus PDF.
    """
    base_url = "https://casqb.org/ke-stazeni"
    response = requests.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    pdf_link = None
    # Loop through all anchor tags that have a download attribute
    for a in soup.find_all('a', download=True):
        download_attr = a.get('download')
        # Check if the download attribute ends with .pdf and contains the syllabus identifier
        if download_attr and download_attr.lower().endswith('.pdf') and "ISTQB_CTFL_Syllabus_CZ" in download_attr:
            href = a.get('href')
            pdf_link = urljoin(base_url, href)  # Ensure the link is absolute
            break

    if not pdf_link:
        raise ValueError("No matching PDF file was found on the page.")
    return pdf_link
