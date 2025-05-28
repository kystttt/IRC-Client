import unittest
from unittest.mock import patch, MagicMock
from source import main as main_module


class TestMain(unittest.TestCase):

    @patch("source.main.IRCWindow")
    @patch("source.main.QApplication")
    @patch("source.main.sys")
    def test_main_creates_and_shows_window(
            self, mock_sys, mock_qapp, mock_window_class):
        mock_app_instance = MagicMock()
        mock_qapp.return_value = mock_app_instance
        mock_window_instance = MagicMock()
        mock_window_class.return_value = mock_window_instance
        main_module.main()
        mock_qapp.assert_called_with(mock_sys.argv)
        mock_window_class.assert_called_once()
        mock_window_instance.show.assert_called_once()
        mock_app_instance.exec.assert_called_once()

    @patch("source.main.QApplication")
    @patch("source.main.IRCWindow")
    @patch("source.main.sys.exit")
    @patch("source.main.sys")
    def test_main_keyboard_interrupt(
            self, mock_sys, mock_exit, mock_window_class, mock_qapp):
        mock_qapp.return_value.exec.side_effect = KeyboardInterrupt
        main_module.main()
        mock_exit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
