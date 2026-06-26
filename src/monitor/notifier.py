import asyncio
from src.audio.tts import speak


class InboundNotifier:
    def __init__(self):
        self.on_notification = None

    def _safe_speak(self, msg: str) -> None:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(speak(msg))
        except RuntimeError:
            pass

    def notify_email(self, count: int) -> None:
        msg = f"Sir, you have {count} new email message{'s' if count > 1 else ''}."
        self._safe_speak(msg)
        if self.on_notification:
            self.on_notification(msg)

    def notify_sms(self, count: int) -> None:
        msg = f"Sir, you have {count} new text message{'s' if count > 1 else ''}."
        self._safe_speak(msg)
        if self.on_notification:
            self.on_notification(msg)
