# J.A.R.V.I.S. — AI Assistant Platform

A modular, multi-modal AI assistant inspired by Tony Stark's J.A.R.V.I.S. Features voice interaction, web search, email/calendar management, system automation, smart home control, persistent memory, and a plugin system.

## Features

- **Multi-modal Interaction**: CLI, Web UI (FastAPI + WebSocket), Voice (clap-activated)
- **LLM Providers**: Gemini (primary), Ollama (local fallback), OpenRouter (cloud fallback)
- **Voice Stack**: STT (faster-whisper), TTS (edge-tts/kokoro), VAD, Wake Word, Clap Detection
- **Tools**: Web search, Calculator, Calendar, Email, News, Reminders, Screenshot, Smart Home, System, Weather
- **Memory**: Short-term (in-memory), Long-term (ChromaDB + SQLite), User Profile
- **Knowledge Base**: Document ingestion + RAG pipeline
- **Plugin System**: Extensible tool registration

## Quick Start

```bash
# Install dependencies
pip install -e .[dev]  # includes test/dev tools

# Or minimal install
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run
python main.py              # Hybrid mode (Web + CLI)
python main.py --cli        # CLI only
python main.py --server     # Server only
python main.py --voice      # Voice mode
```

## Configuration

Copy `.env.example` to `.env` and configure:

```env
# LLM Providers
GEMINI_API_KEY=your_key
OPENAI_API_KEY=your_key
OPENROUTER_API_KEY=your_key
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Voice
STT_MODEL_SIZE=base
TTS_PROVIDER=edge
TTS_VOICE=en-GB-SoniaNeural

# Database
CHROMA_DB_PATH=./chroma_db
SQLITE_DB_PATH=jarvis_data.sqlite
```

## Architecture

```
main.py (entry) → Orchestrator → IntentRouter/Planner/Executor/Validator/Synthesizer
                    ↓
              LLM Fallback Chain (Gemini → Ollama → OpenRouter)
                    ↓
              Tools Registry (11 built-in tools)
                    ↓
              Memory (Short-term + Long-term ChromaDB + SQLite)
```

## Project Structure

```
jarvis/
├── api/           # FastAPI server, WebSocket, REST routes
├── config/        # Settings, constants
├── core/          # Orchestrator, IntentRouter, Planner, Executor, Validator, Synthesizer
├── database/      # SQLite manager, models
├── knowledge/     # RAG, Vector Store, Documents
├── llm/           # Providers: Gemini, Ollama, OpenAI, FallbackChain
├── memory/        # ShortTerm, LongTerm, UserProfile
├── plugins/       # Plugin base, loader, examples
├── tools/         # 11 built-in tools + registry
├── ui/            # CLI, Web (templates), Desktop stubs
├── utils/         # Logger, helpers
└── voice/         # STT, TTS, VAD, WakeWord, ClapDetector, AudioStream
```

## Development

```bash
# Run tests
pytest

# Lint
ruff check .

# Type check
mypy .
```

## License

MIT