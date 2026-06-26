import sounddevice as sd
import numpy as np
import wave
import tempfile
from pathlib import Path
from src.config import Config

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "int16"


class AudioRecorder:
    def __init__(self):
        self.device = Config.audio_input_device

    def record_until_silence(
        self, max_duration: float = 30.0, silence_threshold: float = 200.0
    ) -> np.ndarray:
        chunks = []
        chunk_duration = 0.15
        silence_chunks = 0
        max_silence_chunks = 8
        min_audio_chunks = 3
        has_spoken = False

        for _ in range(int(max_duration / chunk_duration)):
            chunk = sd.rec(
                int(chunk_duration * SAMPLE_RATE),
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype=DTYPE,
                device=self.device,
            )
            sd.wait()
            chunk = chunk.flatten()
            peak = np.max(np.abs(chunk))
            if peak >= silence_threshold:
                has_spoken = True
                silence_chunks = 0
            else:
                silence_chunks += 1

            if has_spoken or peak >= silence_threshold:
                chunks.append(chunk)

            if has_spoken and silence_chunks >= max_silence_chunks:
                break

        if not has_spoken and len(chunks) >= min_audio_chunks:
            pass

        return np.concatenate(chunks) if chunks else np.array([], dtype=DTYPE)

    @staticmethod
    def save_temp(audio: np.ndarray) -> str:
        temp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        with wave.open(temp.name, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio.tobytes())
        return temp.name
