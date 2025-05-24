import unittest
from unittest.mock import patch
from main import ChatbotScreen

class TestChatbotScreen(unittest.TestCase):
    def setUp(self):
        self.screen = ChatbotScreen()

    @patch('webbrowser.open')
    def test_open_chatbot_opens_correct_url(self, mock_open):
        # Simula presionar el botón de abrir chatbot
        self.screen.open_chatbot(None)
        mock_open.assert_called_once_with("https://widget.kommunicate.io/chat?appId=2020521d2025ab5eaa00a302db60492de")

    def test_go_back_changes_screen(self):
        # Simula un ScreenManager
        class DummyManager:
            current = ""
        self.screen.manager = DummyManager()
        self.screen.go_back(None)
        self.assertEqual(self.screen.manager.current, 'products')

if __name__ == '__main__':
    unittest.main()