import keyboard
import threading


class HotkeyListener:
    def __init__(self, hotkey: str = "ctrl+space"):
        self.hotkey = hotkey
        self._callback: callable | None = None
        self._thread: threading.Thread | None = None

    def on_activate(self, callback: callable) -> None:
        self._callback = callback
        keyboard.add_hotkey(self.hotkey, self._trigger)

    def _trigger(self) -> None:
        if self._callback:
            self._callback()

    def stop(self) -> None:
        keyboard.unhook_all()
