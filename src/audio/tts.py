import asyncio
import threading
import pyttsx3

_lock = threading.Lock()
_engine: pyttsx3.Engine | None = None


def _get_engine() -> pyttsx3.Engine:
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        _engine.setProperty("rate", 185)
        _engine.setProperty("volume", 0.95)
        try:
            voices = _engine.getProperty("voices")
            for v in voices:
                if "zira" in v.name.lower() or "david" in v.name.lower():
                    _engine.setProperty("voice", v.id)
                    break
        except Exception:
            pass
    return _engine


def _speak_sync(text: str) -> None:
    try:
        engine = _get_engine()
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass


async def speak(text: str) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _speak_sync, text)
