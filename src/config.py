import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

_ATXP_CONFIG = Path.home() / ".atxp" / "config"


class Config:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    atxp_connection: str = ""
    if _ATXP_CONFIG.exists():
        try:
            raw = _ATXP_CONFIG.read_text().strip()
            parts = raw.split("=", 1)
            atxp_connection = parts[1].strip() if len(parts) == 2 else raw
        except Exception:
            pass

    use_atxp: bool = os.getenv("USE_ATXP", "1") == "1"
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "")

    audio_input_device: int | None = (
        int(v) if (v := os.getenv("AUDIO_INPUT_DEVICE")) else None
    )
    tts_voice: str = os.getenv("TTS_VOICE", "en-US-AriaNeural")
    poll_interval: int = int(os.getenv("POLL_INTERVAL", "30"))
    model: str = os.getenv("OPENAI_MODEL", os.getenv("JARVIS_MODEL", "gpt-4o-mini"))
    recordings_dir: Path = ROOT_DIR / "recordings"

    @classmethod
    def validate(cls) -> list[str]:
        errors = []
        if not cls.openai_api_key and not cls.atxp_connection:
            errors.append("Neither OPENAI_API_KEY nor ATXP connection found")
        return errors
