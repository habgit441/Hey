import os
import tempfile
from typing import Optional

if os.name == "nt":
    import msvcrt
else:
    import fcntl


class SingleInstanceLock:
    """Cross-platform single-instance guard using a lock file."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._lock_path = os.path.join(tempfile.gettempdir(), f"{name}.lock")
        self._file = None

    def acquire(self) -> bool:
        try:
            self._file = open(self._lock_path, "w+", encoding="utf-8")
        except OSError:
            return False

        if os.name == "nt":
            try:
                msvcrt.locking(self._file.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                self._file.close()
                self._file = None
                return False
        else:
            try:
                fcntl.flock(self._file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                self._file.close()
                self._file = None
                return False

        return True

    def release(self) -> None:
        if self._file is not None:
            try:
                if os.name == "nt":
                    msvcrt.locking(self._file.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(self._file.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
            finally:
                self._file.close()
                self._file = None


def ensure_single_instance(name: str = "hey-ai") -> bool:
    lock = SingleInstanceLock(name)
    return lock.acquire()
