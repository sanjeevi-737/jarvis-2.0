import faster_whisper
import numpy as np
import wave

_model: faster_whisper.WhisperModel | None = None


def _get_model() -> faster_whisper.WhisperModel:
    global _model
    if _model is None:
        _model = faster_whisper.WhisperModel(
            "small.en", device="cpu", compute_type="int8"
        )
    return _model


def _read_wav(path: str) -> tuple[np.ndarray, int]:
    with wave.open(path, "rb") as wf:
        frames = wf.readframes(wf.getnframes())
        dtype = np.int16 if wf.getsampwidth() == 2 else np.int32
        audio = np.frombuffer(frames, dtype=dtype).astype(np.float32) / 32768.0
        return audio, wf.getframerate()


def _normalize(audio: np.ndarray) -> np.ndarray:
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.95
    return audio


def _remove_silence(audio: np.ndarray, sr: int, threshold: float = 0.02) -> np.ndarray:
    mask = np.abs(audio) > threshold
    if not np.any(mask):
        return audio
    start = np.argmax(mask)
    end = len(mask) - np.argmax(mask[::-1])
    return audio[start:end]


def transcribe(audio_path: str) -> str:
    try:
        model = _get_model()
        audio, sr = _read_wav(audio_path)
        audio = _normalize(audio)
        audio = _remove_silence(audio, sr)
        segments, info = model.transcribe(
            audio,
            language="en",
            beam_size=5,
            best_of=5,
            vad_filter=True,
            vad_parameters=dict(
                threshold=0.5,
                min_speech_duration_ms=250,
                min_silence_duration_ms=100,
            ),
        )
        return " ".join(seg.text for seg in segments).strip()
    except Exception:
        return ""
