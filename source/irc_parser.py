import re


def parse_irc_line(line, client):
    """
    Обрабатывает строку IRC-протокола и вызывает
    методы клиента
    :param line: строка от сервера IRC
    :param client: IRCClient
    """
    try:
        client.message_received.emit(f"<< {line}")

        if line.startswith("PING"):
            client.send_raw("PONG " + line.split()[1])

        if " 001 " in line:
            client.send_raw("LIST")

        if " 322 " in line:
            parts = line.split()
            channel = parts[3]
            client.channels_received.emit([channel])

        if "JOIN :" in line and client.nick in line:
            channel = line.split("JOIN :")[1]
            client.current_channel = channel
            client.send_raw(f"NAMES {channel}")

        if " 353 " in line:
            users_part = line.split(":", 2)[2]
            users = users_part.strip().split()
            client.users = users
            client.users_updated.emit(users)

        if "PRIVMSG" in line:
            match = re.match(r":([^!]+)!.* PRIVMSG (\S+) :(.+)", line)
            if match:
                sender, target, msg = match.groups()
                client.message_received.emit(f"[{target}] <{sender}>: {msg}")
    except Exception as e:
        client.message_received.emit(f"Error: {e}")
