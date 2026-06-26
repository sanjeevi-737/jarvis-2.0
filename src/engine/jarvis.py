import asyncio
import json
import os               # FIX: import at module level, not inside a finally block
import threading
from queue import Queue
from src.audio.recorder import AudioRecorder
from src.audio.stt import transcribe
from src.audio.tts import speak
from src.ai.llm import chat
from src.ai.memory import ConversationMemory
from src.engine.wake_word import WakeWordDetector
from src.engine.hotkey import HotkeyListener
from src.tools.registry import get_tool_definitions, execute_tool, load_tools
from src.monitor.notifier import InboundNotifier
from src.monitor.poller import InboundPoller
from src.ui.cli import CLI


class Jarvis:
    def __init__(self):
        self.recorder = AudioRecorder()
        self.memory = ConversationMemory()
        self.notifier = InboundNotifier()
        self.poller = InboundPoller(self.notifier)
        self.cli = CLI()
        self._active = threading.Event()
        self._running = True
        self._activation_queue: Queue = Queue()

    async def start(self) -> None:
        self.cli.banner()
        self.cli.status("Say 'Hey Jarvis' or press Ctrl+Space.")

        self.notifier.on_notification = self.cli.notification

        load_tools()

        poller_task = asyncio.create_task(self.poller.start())

        self.wake_word = WakeWordDetector()
        hotkey = HotkeyListener()

        wake_thread = threading.Thread(
            target=self._wake_loop, args=(self.wake_word,), daemon=True
        )
        wake_thread.start()

        hotkey.on_activate(self._manual_activate)

        try:
            while self._running:
                while not self._activation_queue.empty():
                    source = self._activation_queue.get_nowait()
                    await self._handle_activation(source)
                await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self._running = False
            self.poller.stop()
            poller_task.cancel()
            self.wake_word.cleanup()
            hotkey.stop()

    def _wake_loop(self, detector: WakeWordDetector) -> None:
        while self._running:
            if detector.listen():
                if not self._active.is_set():
                    self._active.set()
                    self._activation_queue.put("wake word")

    def _manual_activate(self) -> None:
        if not self._active.is_set():
            self._active.set()
            self._activation_queue.put("hotkey")

    async def _handle_activation(self, source: str) -> None:
        self.cli.status(f"Activated via {source}")
        self.wake_word.pause()
        self.cli.listening()

        try:
            audio = self.recorder.record_until_silence()
        except Exception:
            audio = None

        if audio is None or len(audio) < 1600:
            self.cli.status("No speech detected.")
            self._reset()
            return

        audio_path = AudioRecorder.save_temp(audio)
        self.cli.status("Transcribing...")

        # FIX: os imported at top — temp file always deleted, even if transcribe() throws
        try:
            text = transcribe(audio_path)
        finally:
            try:
                os.unlink(audio_path)
            except OSError:
                pass

        if not text:
            self.cli.status("Could not transcribe audio.")
            self._reset()
            return

        self.cli.user_input(text)

        self.memory.add_user(text)
        tools = get_tool_definitions()

        try:
            self.cli.start_thinking()
            message = chat(self.memory.get_messages(), tools)
        except Exception as e:
            self.cli.error(f"LLM error: {e}")
            self._reset()
            return
        finally:
            self.cli.stop_thinking()

        try:
            if message.tool_calls:
                self.memory.add_tool_calls(message)
                for tc in message.tool_calls:
                    self.cli.status(f"Using tool: {tc.function.name}")
                    args = json.loads(tc.function.arguments)
                    result = await execute_tool(tc.function.name, args)
                    self.memory.add_tool_result(tc.id, result)

                self.cli.start_thinking()
                try:
                    follow_up = chat(self.memory.get_messages())
                finally:
                    self.cli.stop_thinking()
                response_text = follow_up.content or ""
            else:
                response_text = message.content or ""

            if not response_text:
                response_text = "I'm sorry, Sir. I didn't get a response."

            self.cli.assistant(response_text)
            await speak(response_text)
        except Exception as e:
            self.cli.error(f"Response error: {e}")

        self._reset()

    def _reset(self) -> None:
        self._active.clear()
        self.cli.status("Standing by.")
        self.wake_word.resume()
