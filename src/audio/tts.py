import asyncio
import threading
import pyttsx3

_lock = threading.Lock()


def _speak_sync(text: str) -> None:
    with _lock:
        engine = pyttsx3.init()
        try:
            engine.setProperty("rate", 185)
            engine.setProperty("volume", 0.95)
            voices = engine.getProperty("voices")
            for v in voices:
                if "zira" in v.name.lower() or "david" in v.name.lower():
                    engine.setProperty("voice", v.id)
                    break
            engine.say(text)
            engine.runAndWait()
        finally:
            try:
                engine.stop()
            except Exception:
                pass


async def speak(text: str) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _speak_sync, text)
