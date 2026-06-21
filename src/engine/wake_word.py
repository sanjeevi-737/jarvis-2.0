import json
import vosk
import sounddevice as sd
import numpy as np
from pathlib import Path
from src.config import Config

MODEL_PATH = str(Path(__file__).resolve().parent.parent.parent / "models" / "vosk-model-small-en-us-0.15")


class WakeWordDetector:
    def __init__(self):
        self.model = vosk.Model(MODEL_PATH)
        self.sample_rate = 16000
        self.rec = vosk.KaldiRecognizer(self.model, self.sample_rate, '["hey jarvis", "jarvis"]')
        self.rec.SetWords(True)
        self.available = True

    def listen(self, timeout: float | None = None) -> bool:
        audio_stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            blocksize=8000,
            device=Config.audio_input_device,
        )
        with audio_stream:
            while True:
                frame, _ = audio_stream.read(4000)
                if self.rec.AcceptWaveform(frame.tobytes()):
                    result = json.loads(self.rec.Result())
                    text = result.get("text", "").lower()
                    if "hey jarvis" in text or "jarvis" in text:
                        return True
                else:
                    partial = json.loads(self.rec.PartialResult())
                    text = partial.get("partial", "").lower()
                    if "hey jarvis" in text or "jarvis" in text:
                        return True

    def cleanup(self) -> None:
        pass
