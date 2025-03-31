import unittest
from unittest.mock import patch, Mock
from bs4 import BeautifulSoup
import requests
from src.AgentTools import read_web_page  # replace with the actual module name

class TestReadWebPage(unittest.TestCase):
    @patch('requests.get')
    def test_successful_retrieval(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body>Hello World!</body></html>'
        mock_get.return_value = mock_response

        result = read_web_page('https://example.com')
        self.assertEqual(result, 'Hello World!')

    @patch('requests.get')
    def test_invalid_url(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = read_web_page('https://invalid-url.com')
        self.assertEqual(result, '抓取失败: 404')

    @patch('requests.get')
    def test_timeout(self, mock_get):
        mock_get.side_effect = requests.Timeout()

        result = read_web_page('https://example.com')
        self.assertEqual(result, '抓取失败: Timeout')

    @patch('requests.get')
    def test_html_parsing_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body>Hello World!</body></html>'
        mock_get.return_value = mock_response

        with patch('bs4.BeautifulSoup') as mock_bs:
            mock_bs.side_effect = Exception('HTML parsing error')

            result = read_web_page('https://example.com')
            self.assertEqual(result, '抓取失败: HTML parsing error')

    @patch('requests.get')
    def test_text_extraction_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body>Hello World!</body></html>'
        mock_get.return_value = mock_response

        with patch('bs4.BeautifulSoup.get_text') as mock_get_text:
            mock_get_text.side_effect = Exception('Text extraction error')

            result = read_web_page('https://example.com')
            self.assertEqual(result, '抓取失败: Text extraction error')

    @patch('requests.get')
    def test_unknown_exception(self, mock_get):
        mock_get.side_effect = Exception('Unknown error')

        result = read_web_page('https://example.com')
        self.assertEqual(result, '抓取失败: Unknown error')

if __name__ == '__main__':
    unittest.main()