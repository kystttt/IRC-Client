import socket
import threading
from source.replace_emotions import replace_emotions
from source.irc_parser import parse_irc_line
from PyQt6.QtCore import QObject, pyqtSignal


class IRCClient(QObject):
    """
    IRC-клиент с поддержкой подключения к IRC-серверу,
    получения списка каналов,
    присоединения к каналу, обмена сообщениями и отслеживания пользователей.

    """
    message_received = pyqtSignal(str)
    channels_received = pyqtSignal(list)
    users_updated = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.sock = None
        self.nick = None
        self.connected = False
        self.read_thread = None
        self.current_channel = None
        self.users = []

    def connect(self, server, port, nick):
        """
        Подключается к заданному IRC-серверу, слушает входные
        сообщения.
        :param server: Адрес сервера
        :param port: порт подключения(6667)
        :param nick: ник под которым подключаемся
        """
        self.nick = nick
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((server, port))
        self.connected = True

        self.send_raw(f"NICK {nick}")
        self.send_raw(f"USER {nick} 0 * :{nick}")

        self.read_thread = threading.Thread(target=self.listen, daemon=True)
        self.read_thread.start()

    def send_raw(self, data):
        """
        Отправляет командный текст серверу
        :param data:
        :return:
        """
        if self.connected:
            self.sock.send((data + "\r\n").encode("utf-8"))

    def listen(self):
        """
        Слушает сообщения от сервера, обрабатывает строки
        IRC и вызывает соответствующие сигналы.
        :return:
        """
        buffer = ""
        while self.connected:
            try:
                data = self.sock.recv(4096).decode("utf-8", errors="ignore")
                if not data:
                    break
                buffer += data
                while "\r\n" in buffer:
                    line, buffer = buffer.split("\r\n", 1)
                    self.handle_line(line)
            except Exception as e:
                self.message_received.emit(f"Ошибка: {e}")
                self.connected = False
                break

    def handle_line(self, line):
        parse_irc_line(line, self)

    def list_channels(self):
        """
        Запрашивает список каналов на сервере
        """
        self.send_raw("LIST")

    def join_channel(self, channel):
        """
        Отправляет команду входа в указанный канал
        :param channel:
        :return:
        """
        self.send_raw(f"JOIN {channel}")
        self.current_channel = channel

    def send_message(self, target, message):
        """
        Отправляет сообщения в указанный канал или
        пользователю. Длинные сообщения разбиваются
        на части.
        :param target: Имя канала или пользователя
        :param message: само сообщение
        """
        max_len = 400
        parts = [message[i:i + max_len] for i in range(0,
                                                       len(message), max_len)]
        for part in parts:
            part_with_emojis = replace_emotions(part)
            self.send_raw(f"PRIVMSG {target} :{part_with_emojis}")
            self.message_received.emit(f"[{target}] <{self.nick}>: "
                                       f"{part_with_emojis}")
