import sys
from PyQt6.QtWidgets import QApplication
from irc_gui import IRCWindow


def main():
    try:
        app = QApplication(sys.argv)
        window = IRCWindow()
        window.show()
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
