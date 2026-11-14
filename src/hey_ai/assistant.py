import re


class TaskAssistant:
    """Very small task assistant for voice and text requests."""

    def handle_message(self, message: str) -> str:
        text = (message or "").strip()
        if not text:
            return "I didn’t catch that. Please tell me what you want me to do."

        if self._is_vague_request(text):
            return (
                "I need a little more detail to do that right. "
                "Please tell me the task, when it should happen, and any important "
                "details like a name, file, or goal."
            )

        sentence = text.rstrip("?!. ")
        if "call" in sentence.lower() and "sam" in sentence.lower():
            return "I can help with that. I’ll call Sam and keep the timing in mind. If anything is missing, I’ll ask for it."

        if "remind" in sentence.lower() or "schedule" in sentence.lower():
            return f"I can help with that. I’ll keep this task in mind: {sentence}."

        if "email" in sentence.lower() or "message" in sentence.lower():
            return f"I can help with that. I’ll draft the message around: {sentence}."

        return f"I can help with that. Here’s the task I’m ready to work on: {sentence}."

    def _is_vague_request(self, text: str) -> bool:
        lower = text.lower().strip()
        if not lower:
            return True

        if len(lower.split()) <= 3:
            return True

        action_words = {
            "call",
            "email",
            "message",
            "remind",
            "schedule",
            "write",
            "draft",
            "create",
            "make",
            "open",
            "search",
            "check",
            "send",
            "book",
            "plan",
            "summarize",
            "review",
            "buy",
            "set",
            "find",
            "help",
            "do",
        }
        contains_action = any(word in lower for word in action_words)
        if not contains_action:
            return True

        has_detail = bool(
            re.search(
                r"(today|tomorrow|next|monday|tuesday|wednesday|thursday|friday|saturday|sunday|am|pm|at \d|on \d|for [a-z]|with [a-z]|to [a-z])",
                lower,
            )
        )
        if has_detail:
            return False

        has_person_or_goal = bool(
            re.search(
                r"(sam|alex|jordan|client|team|meeting|project|report|file|email|calendar|notes|reminder)",
                lower,
            )
        )
        return not has_person_or_goal

    def listen_for_voice(self) -> str:
        try:
            import speech_recognition as sr
        except Exception:
            return ""

        try:
            import pyaudio  # noqa: F401
        except Exception:
            return ""

        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            return recognizer.recognize_google(audio)
        except sr.WaitTimeoutError:
            return ""
        except Exception:
            return ""
