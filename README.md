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

## Environment Variables

Copy `.env.example` to `.env` and configure:
- `LLM_PROVIDER` — `ollama` or `gemini`
- `OLLAMA_BASE_URL` — Ollama server URL (default: http://localhost:11434)
- `OLLAMA_MODEL` — Model name (e.g., llama3.1)
- `GEMINI_API_KEY` — Google Gemini API key
- `GEMINI_MODEL` — Gemini model name

## License

Private
