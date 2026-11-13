import sys

from PySide6.QtWidgets import QApplication

from hey_ai.widgets.orb import OrbWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("HEY AI")
    app.setOrganizationName("HEY AI")

    window = OrbWindow()
    window.show()
    return app.exec()
