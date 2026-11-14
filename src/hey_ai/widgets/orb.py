from PySide6.QtCore import QPoint, QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QMouseEvent,
    QPainter,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from hey_ai.assistant import TaskAssistant


class OrbWindow(QWidget):
    """Frameless, always-on-top window containing the HEY AI orb."""

    ORB_SIZE = 96
    EXPANDED_SIZE = (340, 230)

    def __init__(self) -> None:
        super().__init__()
        self._expanded = False
        self._drag_offset: QPoint | None = None
        self._press_position: QPoint | None = None
        self._dragged = False
        self._press_on_orb = False
        self._orb_center = QPointF()
        self.assistant = TaskAssistant()

        self.setWindowTitle("HEY AI")
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self.ORB_SIZE, self.ORB_SIZE)

        self.minimize_button = QToolButton(self)
        self.minimize_button.setText("−")
        self.minimize_button.setToolTip("Minimize HEY AI")
        self.minimize_button.setAccessibleName("Minimize HEY AI")
        self.minimize_button.setFixedSize(32, 32)
        self.minimize_button.setStyleSheet(
            """
            QToolButton {
                color: #b7d8ff;
                background: rgba(36, 82, 137, 150);
                border: 1px solid rgba(111, 183, 255, 130);
                border-radius: 16px;
                font-size: 22px;
                padding-bottom: 4px;
            }
            QToolButton:hover {
                background: rgba(55, 119, 190, 210);
            }
            """
        )
        self.minimize_button.clicked.connect(self.collapse)
        self.minimize_button.hide()

        self.content_panel = QWidget(self)
        self.content_panel.setGeometry(12, 42, self.width() - 24, self.height() - 52)
        self.content_panel.setStyleSheet(
            """
            QWidget {
                background: rgba(15, 28, 52, 190);
                border: 1px solid rgba(103, 178, 255, 125);
                border-radius: 22px;
            }
            QLabel {
                color: #edf6ff;
                font-size: 12px;
            }
            QLineEdit {
                background: rgba(10, 24, 43, 180);
                color: #edf6ff;
                border: 1px solid rgba(116, 186, 255, 120);
                border-radius: 12px;
                padding: 7px 10px;
            }
            QPushButton {
                background: rgba(32, 118, 255, 180);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background: rgba(52, 146, 255, 220);
            }
            """
        )
        self.content_panel.hide()

        self.content_layout = QVBoxLayout(self.content_panel)
        self.content_layout.setContentsMargins(14, 14, 14, 14)

        self.status_label = QLabel("HEY AI is ready to listen")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Tell me what you need")
        self.command_input.returnPressed.connect(self.handle_command)

        self.action_row = QWidget(self.content_panel)
        action_layout = QVBoxLayout(self.action_row)
        action_layout.setContentsMargins(0, 0, 0, 0)

        self.listen_button = QPushButton("Listen")
        self.listen_button.clicked.connect(self.handle_voice_input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.handle_command)

        action_layout.addWidget(self.listen_button)
        action_layout.addWidget(self.send_button)

        self.response_label = QLabel("I’ll ask for more details whenever a task needs clarification.")
        self.response_label.setWordWrap(True)
        self.response_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.content_layout.addWidget(self.status_label)
        self.content_layout.addWidget(self.command_input)
        self.content_layout.addWidget(self.action_row)
        self.content_layout.addWidget(self.response_label)

        self._update_orb_center()
        self._place_near_screen_corner()

    @property
    def is_expanded(self) -> bool:
        return self._expanded

    def expand(self) -> None:
        if self._expanded:
            return
        self._set_expanded(True)

    def collapse(self) -> None:
        if not self._expanded:
            return
        self._set_expanded(False)

    def _set_expanded(self, expanded: bool) -> None:
        old_center = self.geometry().topLeft() + self._orb_center.toPoint()
        self._expanded = expanded
        if expanded:
            self.setFixedSize(*self.EXPANDED_SIZE)
            self.minimize_button.show()
            self.content_panel.show()
            self.content_panel.setGeometry(12, 42, self.width() - 24, self.height() - 52)
        else:
            self.setFixedSize(self.ORB_SIZE, self.ORB_SIZE)
            self.minimize_button.hide()
            self.content_panel.hide()
        self._update_orb_center()
        self.move(old_center - self._orb_center.toPoint())
        self.update()

    def handle_voice_input(self) -> None:
        phrase = self.assistant.listen_for_voice()
        if not phrase:
            self.response_label.setText(
                "I can’t hear you yet. Please allow microphone access in Windows Privacy settings, make sure a microphone is connected, and click Listen again."
            )
            self.status_label.setText("Microphone unavailable")
            return

        self.command_input.setText(phrase)
        self.handle_command(phrase)

    def handle_command(self, command: str | None = None) -> None:
        text = (command if command is not None else self.command_input.text()).strip()
        if not text:
            self.response_label.setText("I’m ready—tell me what you want me to do.")
            return

        self.status_label.setText("Processing your request")
        response = self.assistant.handle_message(text)
        self.response_label.setText(response)
        self.command_input.clear()
        self.status_label.setText("Listening for your next task")

    def _update_orb_center(self) -> None:
        if self._expanded:
            self._orb_center = QPointF(self.width() / 2, 55)
            self.minimize_button.move(self.width() - 48, 48)
        else:
            self._orb_center = QPointF(self.width() / 2, self.height() / 2)

    def _place_near_screen_corner(self) -> None:
        screen = self.screen()
        if screen is None:
            return
        available = screen.availableGeometry()
        self.move(available.right() - self.width() - 28, available.top() + 72)

    def resizeEvent(self, event) -> None:
        self._update_orb_center()
        super().resizeEvent(event)

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._expanded:
            panel = QRectF(8, 38, self.width() - 16, self.height() - 46)
            painter.setPen(QColor(71, 151, 238, 120))
            painter.setBrush(QColor(7, 18, 42, 238))
            painter.drawRoundedRect(panel, 25, 25)

        self._draw_orb(painter, self._orb_center)

        if self._expanded:
            painter.setPen(QColor("#eaf5ff"))
            painter.drawText(
                QRectF(24, 112, self.width() - 48, 30),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                "HEY AI",
            )
            painter.setPen(QColor("#91afd0"))
            painter.drawText(
                QRectF(24, 145, self.width() - 48, 28),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                "Your assistant is ready",
            )

        painter.end()

    def _draw_orb(self, painter: QPainter, center: QPointF) -> None:
        radius = 37 if self._expanded else 39
        bounds = QRectF(
            center.x() - radius,
            center.y() - radius,
            radius * 2,
            radius * 2,
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(24, 141, 255, 28))
        painter.drawEllipse(bounds.adjusted(-11, -11, 11, 11))

        glow = QRadialGradient(
            QPointF(center.x() - radius * 0.28, center.y() - radius * 0.36),
            radius * 1.65,
        )
        glow.setColorAt(0, QColor("#e4fbff"))
        glow.setColorAt(0.18, QColor("#75e8ff"))
        glow.setColorAt(0.52, QColor("#248cff"))
        glow.setColorAt(0.82, QColor("#1552c8"))
        glow.setColorAt(1, QColor("#071947"))
        painter.setBrush(glow)
        painter.setPen(QColor(123, 221, 255, 210))
        painter.drawEllipse(bounds)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QColor(159, 235, 255, 180))
        painter.drawEllipse(bounds.adjusted(5, 5, -5, -5))
        painter.setPen(QColor(207, 247, 255, 230))
        painter.drawEllipse(
            QRectF(center.x() - 8, center.y() - 17, 7, 4)
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            event.ignore()
            return
        self._press_position = event.globalPosition().toPoint()
        self._drag_offset = self._press_position - self.frameGeometry().topLeft()
        self._dragged = False
        self._press_on_orb = self._orb_rect().contains(event.position())
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_offset is None or not event.buttons() & Qt.MouseButton.LeftButton:
            return
        if (
            self._press_position is not None
            and (
                event.globalPosition().toPoint() - self._press_position
            ).manhattanLength()
            > 5
        ):
            self._dragged = True
        if self._dragged:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if self._press_on_orb and not self._dragged:
                self.expand()
            self._drag_offset = None
            self._press_position = None
            self._press_on_orb = False
            event.accept()

    def _orb_rect(self) -> QRectF:
        radius = 39 if not self._expanded else 37
        return QRectF(
            self._orb_center.x() - radius,
            self._orb_center.y() - radius,
            radius * 2,
            radius * 2,
        )
