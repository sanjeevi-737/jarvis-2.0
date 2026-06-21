import asyncio
from src.audio.tts import speak


class InboundNotifier:
    def __init__(self):
        self.on_notification = None

    def notify_email(self, count: int) -> None:
        msg = f"Sir, you have {count} new email message{'s' if count > 1 else ''}."
        asyncio.create_task(speak(msg))
        if self.on_notification:
            self.on_notification(msg)

    def notify_sms(self, count: int) -> None:
        msg = f"Sir, you have {count} new text message{'s' if count > 1 else ''}."
        asyncio.create_task(speak(msg))
        if self.on_notification:
            self.on_notification(msg)
