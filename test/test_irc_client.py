import unittest
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QCoreApplication
from source.irc_client import IRCClient


class SignalCatcher:
    def __init__(self):
        self.calls = []

    def __call__(self, *args):
        self.calls.append(args)

    def received(self):
        return len(self.calls) > 0

    def count(self):
        return len(self.calls)

    def last(self):
        return self.calls[-1] if self.calls else None


class TestIRCClient(unittest.TestCase):
    def setUp(self):
        self.app = QCoreApplication.instance()
        if self.app is None:
            self.app = QCoreApplication([])

        self.client = IRCClient()
        self.client.sock = MagicMock()
        self.client.connected = True
        self.client.nick = "tester"

    def test_send_message_emits_signal(self):
        catcher = SignalCatcher()
        self.client.message_received.connect(catcher)

        self.client.send_message("#test", "Hello :)")

        self.assertTrue(catcher.received())
        self.assertEqual(catcher.count(), 1)
        last_msg = catcher.last()[0]
        self.assertIn("[#test] <tester>:", last_msg)
        self.assertIn("Hello", last_msg)

    def test_send_long_message_splits(self):
        catcher = SignalCatcher()
        self.client.message_received.connect(catcher)

        long_text = "A" * 950
        self.client.send_message("#test", long_text)

        self.assertEqual(catcher.count(), 3)
        for msg in catcher.calls:
            self.assertTrue(msg[0].startswith("[#test] <tester>:"))
            self.assertTrue(len(msg[0]) < 500)

    def test_join_channel_sets_current_and_sends_command(self):
        self.client.send_raw = MagicMock()
        self.client.join_channel("#newchannel")

        self.assertEqual(self.client.current_channel, "#newchannel")
        self.client.send_raw.assert_called_with("JOIN #newchannel")

    def test_list_channels_sends_command(self):
        self.client.send_raw = MagicMock()
        self.client.list_channels()
        self.client.send_raw.assert_called_with("LIST")

    def test_send_raw_not_connected_does_nothing(self):
        self.client.connected = False
        self.client.sock.send = MagicMock()

        self.client.send_raw("PING test")
        self.client.sock.send.assert_not_called()

    @patch("source.irc_client.parse_irc_line")
    def test_handle_line_calls_parser(self, mock_parser):
        line = ":nick!user@host PRIVMSG #chan :Hello"
        self.client.handle_line(line)
        mock_parser.assert_called_once_with(line, self.client)

    def test_send_raw_sends_data_when_connected(self):
        self.client.connected = True
        self.client.sock.send = MagicMock()
        data = "TEST MESSAGE"
        self.client.send_raw(data)
        self.client.sock.send.assert_called_once_with(
            (data + "\r\n").encode("utf-8"))

    def test_listen_handles_empty_data_and_stops(self):
        self.client.sock.recv = MagicMock(side_effect=[""])
        self.client.connected = True
        self.client.listen()
        self.assertFalse(self.client.connected)

    def test_send_message_splits_and_emits_multiple_signals(self):
        catcher = SignalCatcher()
        self.client.message_received.connect(catcher)
        self.client.send_raw = MagicMock()
        message = "B" * 810
        self.client.send_message("#channel", message)
        self.assertEqual(catcher.count(), 3)
        self.assertEqual(self.client.send_raw.call_count, 3)
        for i, call_arg in enumerate(self.client.send_raw.call_args_list):
            sent_str = call_arg.args[0]
            self.assertTrue(sent_str.startswith("PRIVMSG #channel :"))
            self.assertLessEqual(len(sent_str), 420)

    def test_listen_handles_exception_and_emits_error(self):
        def raise_exc(*args, **kwargs):
            raise RuntimeError("Test error")

        self.client.sock.recv = MagicMock(side_effect=raise_exc)
        catcher = SignalCatcher()
        self.client.message_received.connect(catcher)

        self.client.connected = True
        self.client.listen()
        self.assertFalse(self.client.connected)
        self.assertTrue(any("Ошибка" in call[0] or "error" in
                            call[0].lower() for call in catcher.calls))

    def test_send_message_emits_multiple_signals_for_multiple_parts(self):
        catcher = SignalCatcher()
        self.client.message_received.connect(catcher)
        self.client.send_raw = MagicMock()
        long_message = "X" * 850
        self.client.send_message("#chan", long_message)

        self.assertEqual(catcher.count(), 3)
        self.assertEqual(self.client.send_raw.call_count, 3)
        for idx, call in enumerate(self.client.send_raw.call_args_list):
            sent = call.args[0]
            self.assertTrue(sent.startswith("PRIVMSG #chan :"))
            self.assertLessEqual(len(sent), 420)
        for call in catcher.calls:
            self.assertTrue(call[0].startswith("[#chan] <tester>:"))


if __name__ == '__main__':
    unittest.main()
