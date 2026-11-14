import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest

from hey_ai.assistant import TaskAssistant
from hey_ai.instance_guard import SingleInstanceLock
from hey_ai.widgets.orb import OrbWindow


class OrbWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.window = OrbWindow()
        self.window.show()
        self.app.processEvents()

    def tearDown(self) -> None:
        self.window.close()

    def test_starts_collapsed_and_always_on_top(self) -> None:
        self.assertFalse(self.window.is_expanded)
        self.assertTrue(
            self.window.windowFlags()
            & Qt.WindowType.WindowStaysOnTopHint
        )
        self.assertFalse(self.window.minimize_button.isVisible())

    def test_clicking_orb_expands_and_minimize_button_collapses(self) -> None:
        QTest.mouseClick(
            self.window,
            Qt.MouseButton.LeftButton,
            pos=QPoint(self.window.width() // 2, self.window.height() // 2),
        )
        self.app.processEvents()

        self.assertTrue(self.window.is_expanded)
        self.assertTrue(self.window.minimize_button.isVisible())
        self.assertEqual(
            (self.window.width(), self.window.height()),
            OrbWindow.EXPANDED_SIZE,
        )

        QTest.mouseClick(self.window.minimize_button, Qt.MouseButton.LeftButton)
        self.app.processEvents()

        self.assertFalse(self.window.is_expanded)
        self.assertFalse(self.window.minimize_button.isVisible())
        self.assertEqual(
            (self.window.width(), self.window.height()),
            (OrbWindow.ORB_SIZE, OrbWindow.ORB_SIZE),
        )


class TaskAssistantTests(unittest.TestCase):
    def test_requests_clarification_for_vague_request(self) -> None:
        assistant = TaskAssistant()

        response = assistant.handle_message("do my task")

        self.assertIn("need a little more detail", response.lower())

    def test_handles_clear_task_without_asking_for_more(self) -> None:
        assistant = TaskAssistant()

        response = assistant.handle_message(
            "Please remind me to call Sam tomorrow at 3 PM"
        )

        self.assertIn("call sam", response.lower())
        self.assertNotIn("need a little more detail", response.lower())


class SingleInstanceTests(unittest.TestCase):
    def test_only_allows_one_active_instance(self) -> None:
        first = SingleInstanceLock("hey-ai-single-instance-test")
        second = SingleInstanceLock("hey-ai-single-instance-test")

        self.assertTrue(first.acquire())
        try:
            self.assertFalse(second.acquire())
        finally:
            first.release()
            second.release()
