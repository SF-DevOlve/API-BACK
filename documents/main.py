import re
from langchain_community.document_loaders import PyPDFLoader


def extract_emails_and_urls(text):
    # Regular expression pattern for emails
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    # Regular expression pattern for URLs
    url_pattern = r'https?://\S+|www\.\S+'

    # Extracting emails
    emails = re.findall(email_pattern, text)
    # Extracting URLs
    urls = re.findall(url_pattern, text)

    return urls, emails


def get_emails_urls_from_pages_contents_from(resume_pdf_path: str):
    with open(resume_pdf_path, 'rb') as file:
        reader = PyPDFLoader(file)
        page_contents = ""
        for page_num in range(reader.num_pages):
            page = reader.getPage(page_num)
            page_text = page.extract_text()
            page_contents += page_text + "\n"
    
    # Regular expressions to find URLs and emails
    url_pattern = r'(https?://\S+)'
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    # Find URLs and emails in the page_contents
    urls = re.findall(url_pattern, page_contents)
    emails = re.findall(email_pattern, page_contents)

    return urls, emails
