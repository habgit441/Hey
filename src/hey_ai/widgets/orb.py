from PySide6.QtCore import QPoint, QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QMouseEvent,
    QPainter,
    QRadialGradient,
)
from PySide6.QtWidgets import QToolButton, QWidget


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
        else:
            self.setFixedSize(self.ORB_SIZE, self.ORB_SIZE)
            self.minimize_button.hide()
        self._update_orb_center()
        self.move(old_center - self._orb_center.toPoint())
        self.update()

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
