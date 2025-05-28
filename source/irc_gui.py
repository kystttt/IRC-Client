from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QListWidget, QLineEdit, QLabel, QTabWidget, QMessageBox
)
from irc_client import IRCClient


class IRCWindow(QWidget):
    def __init__(self):
        super().__init__()
        """
        Инициализирует окно приложения
        """
        try:
            self.setWindowTitle("IRClient")
            self.setGeometry(100, 100, 700, 500)

            self.irc = IRCClient()
            self.irc.message_received.connect(self.on_message)
            self.irc.channels_received.connect(self.on_channels)
            self.irc.users_updated.connect(self.on_users)

            self.nick = None
            self.server = None
            self.port = 6667

            self.init_ui()
        except Exception as e:
            QMessageBox.critical(self, "Initialization Error", str(e))

    def init_ui(self):
        """
        Создает все приколюхи интерфейса
        """
        try:
            layout = QVBoxLayout()

            top_layout = QHBoxLayout()
            self.server_input = QLineEdit("irc.libera.chat")
            self.port_input = QLineEdit("6667")
            self.nick_input = QLineEdit("kyst")
            self.connect_btn = QPushButton("Connect")
            self.connect_btn.clicked.connect(self.connect_server)
            top_layout.addWidget(QLabel("Server:"))
            top_layout.addWidget(self.server_input)
            top_layout.addWidget(QLabel("Port:"))
            top_layout.addWidget(self.port_input)
            top_layout.addWidget(QLabel("Nick:"))
            top_layout.addWidget(self.nick_input)
            top_layout.addWidget(self.connect_btn)
            layout.addLayout(top_layout)

            self.tabs = QTabWidget()

            self.channels_list = QListWidget()
            self.channels_list.itemDoubleClicked.connect(self.join_channel)
            channel_tab = QWidget()
            channel_layout = QVBoxLayout()
            channel_layout.addWidget(QLabel("Available channels:"))
            channel_layout.addWidget(self.channels_list)
            channel_tab.setLayout(channel_layout)
            self.tabs.addTab(channel_tab, "Channels")

            chat_tab = QWidget()
            chat_layout = QVBoxLayout()
            self.chat_display = QTextEdit()
            self.chat_display.setReadOnly(True)
            from PyQt6.QtGui import QFont
            emoji_font = QFont("Segoe UI Emoji")
            self.chat_display.setFont(emoji_font)
            chat_layout.addWidget(self.chat_display)

            self.users_list = QListWidget()
            self.users_list.setMaximumWidth(150)

            chat_main_layout = QHBoxLayout()
            chat_main_layout.addWidget(self.chat_display, stretch=4)
            chat_main_layout.addWidget(self.users_list, stretch=1)
            chat_layout.insertLayout(0, chat_main_layout)

            msg_layout = QHBoxLayout()
            self.msg_input = QLineEdit()
            self.send_btn = QPushButton("Send")
            self.send_btn.clicked.connect(self.send_message)
            msg_layout.addWidget(self.msg_input)
            msg_layout.addWidget(self.send_btn)

            chat_layout.addLayout(msg_layout)
            chat_tab.setLayout(chat_layout)
            self.tabs.addTab(chat_tab, "Chat")

            layout.addWidget(self.tabs)
            self.setLayout(layout)

        except Exception as e:
            QMessageBox.critical(self, "UI Error", str(e))

    def connect_server(self):
        """
        Обрабатывает подключения к серверу.
        Выполняет валидацию входа.
        :return:
        """
        try:
            self.server = self.server_input.text()
            self.port = int(self.port_input.text())
            self.nick = self.nick_input.text()

            if not self.server or not self.nick:
                QMessageBox.warning(
                    self, "Error", "Enter Server Name and Nickname")
                return

            self.irc.connect(self.server, self.port, self.nick)
            self.chat_display.append(f"Connected to {self.
                                     server}:{self.port} as {self.nick}")
        except Exception as e:
            QMessageBox.critical(self, "Connection error", str(e))

    def on_message(self, msg):
        """
        Добавляет полученное сообщение в чат
        :param msg: текст сообщения
        """
        try:
            self.chat_display.append(msg)
        except Exception as e:
            print(f"[on_message] Error: {e}")

    def on_channels(self, channels):
        """
        Добавляет полученные каналы в список
        """
        try:
            for ch in channels:
                if not any(self.channels_list.item(i).text() == ch
                           for i in range(self.channels_list.count())):
                    self.channels_list.addItem(ch)
        except Exception as e:
            print(f"[on_channels] Error: {e}")

    def join_channel(self, item):
        """
        Обрабатывает двойной клик по каналу из списка
        каналов, переключает вкладку на чат
        :param item:
        """
        try:
            channel = item.text()
            self.irc.join_channel(channel)
            self.chat_display.append(f"Connecting to {channel}...")
            self.tabs.setCurrentIndex(1)
        except Exception as e:
            print(f"[join_channel] Error: {e}")

    def on_users(self, users):
        """
        Добавляет пользователей
        :param users:
        """
        try:
            users_sorted = sorted(users, key=lambda u: (
                not u.startswith("@"), u.lower()))
            self.users_list.clear()
            for user in users_sorted:
                self.users_list.addItem(user)
        except Exception as e:
            print(f"[on_users] Error: {e}")

    def send_message(self):
        """
        Отправляет сообщение в текущий канал.
        Разбивает длинные сообщения.
        """
        try:
            text = self.msg_input.text().strip()
            if not text or not self.irc.current_channel:
                return
            self.irc.send_message(self.irc.current_channel, text)
            self.msg_input.clear()
        except Exception as e:
            print(f"[send_message] Error: {e}")
