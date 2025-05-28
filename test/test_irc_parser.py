import unittest
from source.irc_parser import parse_irc_line


class MockClient:
    def __init__(self):
        self.sent_raw = []
        self.received_msgs = []
        self.channels = []
        self.users_list = []
        self.nick = "tester"
        self.current_channel = None

        self.message_received = self._make_signal(self.received_msgs)
        self.channels_received = self._make_signal(self.channels)
        self.users_updated = self._make_signal(self.users_list)

    class Signal:
        def __init__(self, store):
            self.store = store

        def emit(self, *args):
            if len(args) == 1 and isinstance(args[0], list):
                self.store.extend(args[0])
            else:
                self.store.append(args[0] if len(args) == 1 else args)

    def _make_signal(self, store):
        return self.Signal(store)

    def send_raw(self, data):
        self.sent_raw.append(data)


class TestIRCParser(unittest.TestCase):

    def setUp(self):
        self.client = MockClient()

    def test_ping_line_triggers_pong(self):
        parse_irc_line("PING :server", self.client)
        self.assertIn("PONG :server", self.client.sent_raw)
        self.assertIn("<< PING :server", self.client.received_msgs)

    def test_welcome_triggers_list(self):
        parse_irc_line(":server 001 tester :Welcome", self.client)
        self.assertIn("LIST", self.client.sent_raw)

    def test_list_channel_emits_channel(self):
        parse_irc_line(":server 322 tester #channel 10 :desc", self.client)
        self.assertEqual(self.client.channels, ["#channel"])

    def test_join_updates_channel_and_sends_names(self):
        parse_irc_line(":tester!user@host JOIN :#testchan", self.client)
        self.assertEqual(self.client.current_channel, "#testchan")
        self.assertIn("NAMES #testchan", self.client.sent_raw)

    def test_users_list_parsing(self):
        line = ":server 353 tester = #chan :alice bob charlie"
        parse_irc_line(line, self.client)
        self.assertEqual(self.client.users_list, ["alice",
                                                  "bob", "charlie"])

    def test_privmsg_parsing(self):
        line = ":alice!user@host PRIVMSG #chan :hello everyone"
        parse_irc_line(line, self.client)
        self.assertIn("[#chan] <alice>: hello everyone",
                      self.client.received_msgs)

    def test_error_handling(self):
        parse_irc_line(None, self.client)
        self.assertTrue(any("Error" in msg for msg in
                            self.client.received_msgs))


if __name__ == "__main__":
    unittest.main()
