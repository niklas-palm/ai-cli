import os
import click
import requests
from urllib.parse import urlparse
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup


def is_local_filepath(input: str) -> bool:
    """Chek if input is a local filepath

    Parameters:
        input (str): input to check

    Returns:
        True | False
    """
    if os.path.exists(input):
        return True  # It's a local file path

    return False


def is_url(input: str) -> bool:
    """Chek if input is a url

    Parameters:
        input (str): input to check

    Returns:
        True | False
    """
    # Parse the input argument as a URL
    parsed_url = urlparse(input)

    if parsed_url.scheme and parsed_url.scheme.startswith("http"):
        return True

    return False


def fetch_pdf(path: str) -> str:
    """Reads the provided PDF and return the text

    Parameters:
        path (str): path of pdf

    Returns:
        pdf_text (str)
    """

    def is_pdf_file(path):
        # Check if the file path exists
        if not os.path.exists(path):
            return False

        # Get the file extension and check if it's '.pdf'
        file_extension = os.path.splitext(path)[1]
        return file_extension.lower() == ".pdf"

    if not is_pdf_file(path):
        raise Exception("Not a PDF file. What are you tying to do!?")

    # Read PDF
    reader = PdfReader(path)

    # Extract all text from reader object
    pdf_text = "\n".join([x.extract_text() for x in reader.pages])

    return pdf_text


def fetch_url(url: str) -> str:
    """Fecthes the provided url, parses the HTML and returns the text

    Parameters:
        url (str): URL to fetch

    Returns:
        pdf_text (str)
    """
    try:
        # Send an HTTP GET request to the specified URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Print the content of the website
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract and print the text content (excluding HTML tags)
            text_content = soup.get_text()
            click.echo(text_content)
    except requests.exceptions.RequestException as e:
        raise e
