import unittest
from unittest.mock import patch, MagicMock
from tools import read_pdf, look_for_pdf_files
import requests

class TestReadPdf(unittest.TestCase):

    @patch("tools.requests.get")
    @patch("tools.PdfReader")
    def test_read_pdf_success(self, mock_pdf_reader, mock_requests_get):
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"%PDF-1.4 fake pdf content"
        mock_requests_get.return_value = mock_response

        # Mock the PdfReader behavior
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [
            MagicMock(extract_text=lambda: "Page 1 text"),
            MagicMock(extract_text=lambda: "Page 2 text"),
        ]
        mock_pdf_reader.return_value = mock_reader_instance

        # Call the function
        pdf_url = "http://example.com/fake.pdf"
        result = read_pdf(pdf_url)

        # Assertions
        mock_requests_get.assert_called_once_with(pdf_url)
        mock_pdf_reader.assert_called_once()
        self.assertEqual(result, "Page 1 text\nPage 2 text\n")

    @patch("tools.requests.get")
    @patch("tools.PdfReader")
    def test_read_pdf_empty_pdf(self, mock_pdf_reader, mock_requests_get):
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"%PDF-1.4 fake pdf content"
        mock_requests_get.return_value = mock_response

        # Mock the PdfReader behavior with no text
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [
            MagicMock(extract_text=lambda: None),
            MagicMock(extract_text=lambda: None),
        ]
        mock_pdf_reader.return_value = mock_reader_instance

        # Call the function
        pdf_url = "http://example.com/empty.pdf"
        result = read_pdf(pdf_url)

        # Assertions
        mock_requests_get.assert_called_once_with(pdf_url)
        mock_pdf_reader.assert_called_once()
        self.assertEqual(result, "")

    @patch("tools.requests.get")
    def test_read_pdf_http_error(self, mock_requests_get):
        # Mock a failed HTTP response
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_requests_get.return_value = mock_response

        # Call the function and expect an exception
        pdf_url = "http://example.com/404.pdf"
        with self.assertRaises(requests.exceptions.HTTPError):
            read_pdf(pdf_url)

        # Assertions
        mock_requests_get.assert_called_once_with(pdf_url)

class TestLookForPdfFiles(unittest.TestCase):

    @patch("tools.requests.get")
    @patch("tools.BeautifulSoup")
    def test_look_for_pdf_files_success(self, mock_beautiful_soup, mock_requests_get):
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html>Mock HTML</html>"
        mock_requests_get.return_value = mock_response

        # Mock BeautifulSoup behavior
        mock_soup = MagicMock()
        mock_beautiful_soup.return_value = mock_soup
        mock_anchor = MagicMock()
        mock_anchor.get.side_effect = lambda attr: {
            'download': "ISTQB_CTFL_Syllabus_CZ.pdf",
            'href': "/files/ISTQB_CTFL_Syllabus_CZ.pdf"
        }.get(attr)
        mock_soup.find_all.return_value = [mock_anchor]

        # Call the function
        result = look_for_pdf_files()

        # Assertions
        mock_requests_get.assert_called_once_with("https://casqb.org/ke-stazeni")
        mock_beautiful_soup.assert_called_once_with(mock_response.text, 'html.parser')
        mock_soup.find_all.assert_called_once_with('a', download=True)
        self.assertEqual(result, "https://casqb.org/files/ISTQB_CTFL_Syllabus_CZ.pdf")

    @patch("tools.requests.get")
    @patch("tools.BeautifulSoup")
    def test_look_for_pdf_files_no_match(self, mock_beautiful_soup, mock_requests_get):
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html>Mock HTML</html>"
        mock_requests_get.return_value = mock_response

        # Mock BeautifulSoup behavior with no matching links
        mock_soup = MagicMock()
        mock_beautiful_soup.return_value = mock_soup
        mock_soup.find_all.return_value = []

        # Call the function and expect an exception
        with self.assertRaises(ValueError) as context:
            look_for_pdf_files()

        # Assertions
        mock_requests_get.assert_called_once_with("https://casqb.org/ke-stazeni")
        mock_beautiful_soup.assert_called_once_with(mock_response.text, 'html.parser')
        mock_soup.find_all.assert_called_once_with('a', download=True)
        self.assertEqual(str(context.exception), "No matching PDF file was found on the page.")

    @patch("tools.requests.get")
    def test_look_for_pdf_files_http_error(self, mock_requests_get):
        # Mock a failed HTTP response
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_requests_get.return_value = mock_response

        # Call the function and expect an exception
        with self.assertRaises(requests.exceptions.HTTPError):
            look_for_pdf_files()

        # Assertions
        mock_requests_get.assert_called_once_with("https://casqb.org/ke-stazeni")

if __name__ == "__main__":
    unittest.main()
