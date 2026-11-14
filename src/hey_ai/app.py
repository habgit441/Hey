import sys

from PySide6.QtWidgets import QApplication

from hey_ai.instance_guard import ensure_single_instance
from hey_ai.widgets.orb import OrbWindow


def main() -> int:
    if not ensure_single_instance("hey-ai"):
        return 0

    app = QApplication(sys.argv)
    app.setApplicationName("HEY AI")
    app.setOrganizationName("HEY AI")

    window = OrbWindow()
    window.show()
    return app.exec()
