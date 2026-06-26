import asyncio
from src.monitor.notifier import InboundNotifier
from src.tools.atxp_bridge import _run_npx
from src.config import Config


class InboundPoller:
    def __init__(self, notifier: InboundNotifier):
        self.notifier = notifier
        self._running = False
        self._last_email_count = 0
        self._last_sms_count = 0

    async def start(self) -> None:
        if not Config.use_atxp or not Config.atxp_connection:
            return
        self._running = True
        while self._running:
            try:
                await self._check_email()
                await self._check_sms()
            except Exception:
                pass
            await asyncio.sleep(Config.poll_interval)

    def stop(self) -> None:
        self._running = False

    async def _check_email(self) -> None:
        result = await _run_npx(["email", "inbox"])
        lower_result = result.lower()
        count = lower_result.count("\nunread") if "unread" in lower_result else 0
        if count > self._last_email_count:
            self.notifier.notify_email(count - self._last_email_count)
        self._last_email_count = count

    async def _check_sms(self) -> None:
        result = await _run_npx(["phone", "sms", "--unread-only"])
        lines = [l for l in result.split("\n") if l.strip()]
        count = len(lines)
        if count > self._last_sms_count:
            self.notifier.notify_sms(count - self._last_sms_count)
        self._last_sms_count = count
