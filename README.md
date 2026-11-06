# AI Calling Agent

AI-powered calling agent with provider-agnostic LLM architecture supporting Ollama and Google Gemini.

## Architecture

```
Customer → Telephony → STT → ConversationManager → LLM Provider (Ollama/Gemini) → TTS → Telephony → Customer
```

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env   # Edit with your config
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Multilingual TTS (optional)
VEXYL-TTS provides self-hosted speech for Indian languages. Run it separately
from this project, then set `VEXYL_TTS_URL=http://localhost:8092` in `.env`:

```bash
git clone https://github.com/vexyl-ai/vexyl-tts.git
cd vexyl-tts
./setup.sh
VEXYL_TTS_SAMPLE_RATE=8000 ./run.sh
```

The Mock Call page sends the selected language and voice style through the
backend proxy. If VEXYL-TTS is unavailable or not configured, it falls back to
browser speech.

## Environment Variables

Copy `.env.example` to `.env` and configure:
- `LLM_PROVIDER` — `ollama` or `gemini`
- `OLLAMA_BASE_URL` — Ollama server URL (default: http://localhost:11434)
- `OLLAMA_MODEL` — Model name (e.g., llama3.1)
- `GEMINI_API_KEY` — Google Gemini API key
- `GEMINI_MODEL` — Gemini model name
- `VEXYL_TTS_URL` — VEXYL-TTS server URL
- `VEXYL_TTS_API_KEY` — optional shared API key
- `VEXYL_TTS_TIMEOUT_SECONDS` — synthesis timeout

## License

Private
