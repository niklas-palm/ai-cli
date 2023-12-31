import os
import requests
from urllib.parse import urlparse
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup


def is_local_filepath(file_path: str) -> bool:
    """
    Check if the given input is a local file path.

    Parameters:
        file_path (str): The input file path to check.

    Returns:
        bool: True if the input is a local file path, False otherwise.
    """
    return os.path.exists(file_path)


def is_url(input: str) -> bool:
    """
    Check if the given input is a URL.

    Parameters:
        input (str): The input URL to check.

    Returns:
        bool: True if the input is a URL, False otherwise.
    """
    parsed_url = urlparse(input)
    return bool(parsed_url.scheme and parsed_url.scheme.startswith("http"))


def get_local_file_text(path: str) -> str:
    """
    Read the provided file and return the text.

    Parameters:
        path (str): The path of the local file.

    Returns:
        str: The extracted text.

    Raises:
        FileNotFoundError: If the file path does not exist.
        ValueError: If the file type is not supported.
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f"No file found at {path}")

    file_extension = os.path.splitext(path)[1]

    if file_extension.lower() == ".pdf":
        return fetch_pdf(path)

    if file_extension.lower() == ".txt":
        return fetch_txt(path)

    raise ValueError(f"File format '{file_extension}' is not supported")


def fetch_txt(path: str) -> str:
    """
    Read the provided tcxt file and return the text.

    Parameters:
        path (str): The path of the txt file.

    Returns:
        str: The extracted text from the txt.

    Raises:
        ValueError: If the file is not a txt.
    """

    file_extension = os.path.splitext(path)[1]
    if file_extension.lower() != ".txt":
        raise ValueError("File is not a TXT")

    with open(path, "r") as file:
        text = file.read()

    return text


def fetch_pdf(path: str) -> str:
    """
    Read the provided PDF and return the text.

    Parameters:
        path (str): The path of the PDF.

    Returns:
        str: The extracted text from the PDF.

    Raises:
        ValueError: If the file is not a PDF.
    """

    file_extension = os.path.splitext(path)[1]
    if file_extension.lower() != ".pdf":
        raise ValueError("File is not a PDF")

    reader = PdfReader(path)
    return "\n".join(page.extract_text() for page in reader.pages)


def fetch_url(url: str) -> str:
    """
    Fetch the provided URL, parse the HTML, and return the text.

    Parameters:
        url (str): The URL to fetch.

    Returns:
        str: The text content of the URL.

    Raises:
        requests.exceptions.RequestException: If there is a problem with the
        request.
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise requests.exceptions.RequestException(
            f"Request to {url} returned status code {response.status_code}"
        )

    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text()
