import json
import time
import threading
import vosk
import sounddevice as sd
import numpy as np
from pathlib import Path
from src.config import Config

_MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "models" / "vosk-model-small-en-us-0.15"


class WakeWordDetector:
    def __init__(self):
        if not _MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Vosk model not found at {_MODEL_PATH}.\n"
                "Download from: https://alphacephei.com/vosk/models\n"
                "Place in: models/vosk-model-small-en-us-0.15/"
            )
        self.model = vosk.Model(str(_MODEL_PATH))
        self.sample_rate = 16000
        self.rec = vosk.KaldiRecognizer(self.model, self.sample_rate, '["hey jarvis", "jarvis"]')
        self.rec.SetWords(True)
        self.available = True
        self._paused = threading.Event()
        self._cooldown_until = 0.0
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            blocksize=8000,
            device=Config.audio_input_device,
        )
        self._stream.start()

    def pause(self) -> None:
        self._paused.set()

    def resume(self) -> None:
        self._paused.clear()

    def listen(self, timeout: float | None = None) -> bool:
        if self._paused.is_set():
            self._paused.wait(timeout=0.2)
            return False

        start = time.time()
        while True:
            if self._paused.is_set():
                return False
            if timeout and (time.time() - start) > timeout:
                return False

            frame, _ = self._stream.read(4000)
            if self.rec.AcceptWaveform(frame.tobytes()):
                result = json.loads(self.rec.Result())
                text = result.get("text", "").lower()
                if "hey jarvis" in text or text.strip() == "jarvis":
                    if time.time() > self._cooldown_until:
                        self._cooldown_until = time.time() + 2.5
                        return True

    def cleanup(self) -> None:
        self._stream.stop()
        self._stream.close()
