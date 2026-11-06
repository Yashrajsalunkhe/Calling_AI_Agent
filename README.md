# AI Calling Agent

A provider-agnostic, full-stack AI calling agent. It pairs a **FastAPI** backend with a **React + Vite** control room so you can configure LLM providers, build agents, and test real voice conversations in the browser — all through the same conversation engine a production telephony pipeline would use.

The conversation layer never imports a specific model SDK. It talks to an abstract `LLMProvider` interface, which means you can switch between **local Ollama models** and **Google Gemini** at runtime without touching the calling logic.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [LLM Provider Setup](#llm-provider-setup)
- [Multilingual TTS (Optional)](#multilingual-tts-optional)
- [Using the App](#using-the-app)
- [API Reference](#api-reference)
- [Data Models](#data-models)
- [Security](#security)
- [Testing](#testing)
- [Production Build](#production-build)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Overview

AI Calling Agent separates **what the agent says** from **which model generates it**:

- **Conversation engine** — `ConversationManager` keeps session state and history, and calls the LLM through a factory.
- **Provider layer** — `OllamaProvider` and `GeminiProvider` implement the same `LLMProvider` interface and return a standardized `LLMResponse`.
- **Control plane** — a React dashboard to switch providers, manage agents, inspect provider health, and run mock calls.
- **Voice layer** — browser speech recognition for input, and an optional self-hosted VEXYL-TTS service (with browser speech synthesis fallback) for output.

The Mock Call page exercises the exact `ConversationManager → LLM Factory → Provider` path, so testing there reflects how real calls behave.

## Features

- 🔁 **Runtime provider switching** — switch between Ollama and Gemini from the UI; no restart required.
- 🧩 **Per-agent LLM overrides** — each agent can pin its own provider and model, or inherit the global config.
- 🛡️ **Encrypted API keys** — Gemini credentials are encrypted at rest with Fernet and only ever returned masked.
- 🔄 **Optional automatic fallback** — if the primary provider fails and fallback is enabled, the request retries against a second provider (failures are always logged).
- 🎙️ **Browser voice conversations** — speak via the microphone (Web Speech API) and hear replies spoken back.
- 🗣️ **Multilingual TTS** — 24 Indian/English language codes and three voice styles through VEXYL-TTS, with graceful browser fallback.
- 📊 **Observability** — every response includes provider, model, token usage, latency, intent, and call-state signals.
- 🤖 **Agent management** — full CRUD for agents: prompts, language, voice, model, and active status.
- 💾 **Usage tracking** — token usage and latency are persisted per LLM request for future analytics/cost work.
- ✅ **Tested core** — pytest coverage for the provider factory, response shaping, security, and Gemini health checks.

## Architecture

### High-level call flow

```
Customer
   │  voice
   ▼
Telephony / Browser Mic
   │  audio → text
   ▼
STT (browser Web Speech API)
   │  transcript
   ▼
ConversationManager  ─── session state + history ───┐
   │                                               │
   ▼                                               │
LLM Provider Factory                               │
   ├── OllamaProvider  ──► local Ollama server      │
   └── GeminiProvider  ──► Google Gemini API        │
   │                                               │
   ▼  standardized LLMResponse                      │
TTS (VEXYL-TTS or browser speechSynthesis) ◄───────┘
   │  audio
   ▼
Customer
```

### Component layout

```
┌─────────────────────────────┐        ┌────────────────────────────────────┐
│  React + Vite (port 5173)   │  /api  │  FastAPI (port 8000)               │
│  Landing / Dashboard        │ ─────► │  Routers: settings, providers,     │
│  LLM Settings / Agents      │  proxy │  agents, conversation, tts         │
│  Mock Call                  │ ◄───── │                                    │
└─────────────────────────────┘        │  Services: ConversationManager     │
                                       │  LLM Factory → Ollama / Gemini     │
                                       │  SQLAlchemy async → SQLite         │
                                       └────────────────────────────────────┘
```

### Design principles

1. **Interface-first providers** — all providers extend `LLMProvider` (`generate()` + `health_check()`) and return `LLMResponse`.
2. **No provider imports in the engine** — `ConversationManager` only knows the factory.
3. **Standardized output** — raw provider text is normalized; structured JSON (`intent`, `should_end_call`, `should_transfer`, `collected_information`) is extracted when present.
4. **Secrets stay server-side** — the frontend never receives raw API keys.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend framework | FastAPI 0.115, Uvicorn |
| ORM / DB | SQLAlchemy 2.0 (async), aiosqlite, SQLite |
| Settings | pydantic-settings |
| LLM SDKs | `ollama` 0.4, `google-genai` 1.14 |
| Security | `cryptography` (Fernet) |
| HTTP client | httpx |
| Testing | pytest, pytest-asyncio |
| Frontend | React 19, React Router 7, Vite 8 |
| Linting | Oxlint |
| TTS (optional) | VEXYL-TTS (external service) |

## Project Structure

```
Calling_AI_Agent/
├── .env.example                  # Environment template
├── README.md
├── backend/
│   ├── requirements.txt
│   ├── calling_agent.db          # Local SQLite DB (gitignored, created at runtime)
│   ├── app/
│   │   ├── main.py               # FastAPI app, CORS, lifespan, routers
│   │   ├── config.py             # pydantic-settings configuration
│   │   ├── database.py           # Async engine, session factory, init_db()
│   │   ├── security.py           # Fernet encryption + key masking
│   │   ├── routers/
│   │   │   ├── settings.py       # Global LLM settings (GET/PUT)
│   │   │   ├── providers.py      # Provider status + connection tests
│   │   │   ├── agents.py         # Agent CRUD
│   │   │   ├── conversation.py   # Mock call session endpoints
│   │   │   └── tts.py            # VEXYL-TTS proxy
│   │   ├── models/
│   │   │   ├── llm_config.py     # Singleton global LLM config
│   │   │   ├── agent.py          # Agent definition
│   │   │   └── llm_usage.py      # Per-request usage record
│   │   ├── schemas/              # Pydantic request/response models
│   │   └── services/
│   │       └── ai/
│   │           ├── conversation.py   # ConversationManager + sessions
│   │           └── llm/
│   │               ├── base.py       # LLMProvider ABC, LLMResponse
│   │               ├── factory.py    # Provider registry + fallback
│   │               ├── ollama.py     # Ollama implementation
│   │               └── gemini.py     # Gemini implementation
│   └── tests/
│       ├── test_factory.py       # Factory, response, Gemini health tests
│       └── test_security.py      # Encrypt/decrypt/mask tests
└── frontend/
    ├── package.json
    ├── vite.config.js            # Dev server + /api proxy to :8000
    └── src/
        ├── App.jsx               # Shell, sidebar, routing
        ├── api/client.js         # Centralized API wrapper
        └── pages/
            ├── Landing.jsx
            ├── Dashboard.jsx
            ├── Settings.jsx
            ├── Agents.jsx
            └── MockCall.jsx
```

## Prerequisites

- **Python 3.11+** (tested with modern CPython; the code uses `str | None` syntax)
- **Node.js 18+** and npm
- **Ollama** installed and running (for the local provider), or a **Google Gemini API key**
- A modern browser with Web Speech API support for voice input (Chrome/Edge recommended)
- *(Optional)* A running **VEXYL-TTS** service for multilingual speech

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/Yashrajsalunkhe/Calling_AI_Agent.git
cd Calling_AI_Agent
cp .env.example .env
# Edit .env with your provider settings
```

> ⚠️ Never commit `.env`. It is already listed in `.gitignore`.

### 2. Start the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# The .env file is loaded from the repository root (../.env),
# so run uvicorn from the backend/ directory.
uvicorn app.main:app --reload
```

Database tables are created automatically on startup via `init_db()`; there is **no separate migration step**. The SQLite file defaults to `backend/calling_agent.db`.

- API: <http://localhost:8000>
- Interactive docs (Swagger): <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. Vite proxies `/api` requests to the backend on port `8000`, so no CORS tweaking is needed during development.

### 4. Verify

1. Open the dashboard — the active provider and provider health cards should load.
2. Go to **LLM Settings** and confirm the provider/model.
3. Create an agent under **Agents** (or use the default).
4. Open **Mock Call**, start a call, and speak or type a message.

## Configuration

Copy `.env.example` to `.env` at the repository root. The backend resolves it as `../.env` relative to the `backend/` working directory.

| Variable | Default | Description |
| --- | --- | --- |
| `LLM_PROVIDER` | `ollama` | Active provider: `ollama` or `gemini`. |
| `LLM_FALLBACK_PROVIDER` | *(empty)* | Secondary provider used when the primary fails. |
| `LLM_FALLBACK_ENABLED` | `false` | Enable automatic fallback retries. |
| `LLM_TIMEOUT_SECONDS` | `30` | Provider request timeout. |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL. |
| `OLLAMA_MODEL` | `llama3.1` | Ollama model name. |
| `GEMINI_API_KEY` | *(empty)* | Google Gemini API key. |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model name. |
| `VEXYL_TTS_URL` | *(empty)* | VEXYL-TTS base URL; leave empty to disable. |
| `VEXYL_TTS_API_KEY` | *(empty)* | Optional shared key sent as `X-API-Key`. |
| `VEXYL_TTS_TIMEOUT_SECONDS` | `30` | Synthesis timeout. |
| `APP_SECRET_KEY` | `change-this-...` | Secret used to derive the encryption key. **Change in production.** |
| `DATABASE_URL` | `sqlite+aiosqlite:///./calling_agent.db` | Async SQLAlchemy URL. |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed origins. |

> **Note:** Some settings can also be edited at runtime through **LLM Settings** in the UI and are persisted in the `llm_config` table. Environment values provide the initial defaults used by the factory.

## LLM Provider Setup

### Ollama (local / self-hosted)

```bash
# Install Ollama from https://ollama.com, then:
ollama pull llama3.1
ollama serve            # usually starts automatically
```

Set in `.env`:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

The dashboard's Ollama status card calls `/api/tags` to confirm reachability.

### Google Gemini

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-2.0-flash
```

Alternatively, enter the key in the **LLM Settings** page. The backend encrypts it before storing and only returns a masked form (`AIza...cdef`) to the browser. To use a different provider per agent, set `llm_provider` / `llm_model` on that agent; leaving them empty inherits the global config.

### Fallback behavior

To enable automatic failover:

```env
LLM_FALLBACK_ENABLED=true
LLM_FALLBACK_PROVIDER=gemini   # or ollama
```

`get_llm_provider_with_fallback()` tries the primary; only if it raises and fallback is enabled/configured will it retry. All failures are logged, and the response identifies which provider actually served it.

## Multilingual TTS (Optional)

VEXYL-TTS provides self-hosted speech for Indian languages. It runs as a separate service — this project only proxies requests to it.

```bash
git clone https://github.com/vexyl-ai/vexyl-tts.git
cd vexyl-tts
./setup.sh
VEXYL_TTS_SAMPLE_RATE=8000 ./run.sh
```

Then configure:

```env
VEXYL_TTS_URL=http://localhost:8092
VEXYL_TTS_API_KEY=            # optional
VEXYL_TTS_TIMEOUT_SECONDS=30
```

The Mock Call page sends the selected language and voice style through `POST /api/tts/synthesize`. Supported language codes include `en-IN`, `en-US`, `en-GB`, `hi-IN`, `ml-IN`, `ta-IN`, `te-IN`, `kn-IN`, `bn-IN`, `gu-IN`, `mr-IN`, `pa-IN`, `or-IN`, `as-IN`, `ur-IN`, `ne-IN`, `sa-IN`, `brx-IN`, `doi-IN`, `kok-IN`, `mai-IN`, `mni-IN`, `sat-IN`, and `sd-IN`, with styles `default`, `warm`, and `formal`.

If VEXYL-TTS is not configured or unavailable, the frontend falls back to the browser's `speechSynthesis`.

## Using the App

| Page | Route | What you can do |
| --- | --- | --- |
| **Landing** | `/` | Product overview and system architecture. |
| **Dashboard** | `/dashboard` | Active provider, provider health/latency, online count, recent agents. |
| **LLM Settings** | `/settings/ai` | Switch provider, edit Ollama/Gemini settings, configure fallback, test connections. |
| **Agents** | `/agents` | Create/edit/delete agents with prompts, provider/model overrides, language, voice. |
| **Mock Call** | `/mock-call` | Start a session, talk or type, hear spoken replies, see per-message provider/latency/token metadata. |

**Mock Call tips**

- Grant microphone permission when prompted.
- Choose an agent before starting to apply its prompt and LLM override.
- Press **Enter** to send; the language selector also controls recognition and TTS language.
- Ending a call clears the session; conversation history lives in memory only.

## API Reference

Base URL: `http://localhost:8000` — all application routes under `/api`.

### Application

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/` | Service metadata. |
| `GET` | `/health` | Health check. |

### Settings

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/settings/llm` | Get global LLM config (API key masked). |
| `PUT` | `/api/settings/llm` | Update config; only provided fields change. |

### Providers

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/providers/status` | Status for all providers + active provider. |
| `POST` | `/api/providers/{provider_name}/test` | Test a specific provider's connectivity. |

### Agents

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/agents/` | List agents (newest first). |
| `POST` | `/api/agents/` | Create an agent (`201`). |
| `GET` | `/api/agents/{agent_id}` | Get one agent. |
| `PUT` | `/api/agents/{agent_id}` | Update an agent. |
| `DELETE` | `/api/agents/{agent_id}` | Delete an agent. |

**Create agent request**

```json
{
  "name": "Support Agent",
  "description": "Handles billing questions",
  "llm_provider": "ollama",
  "llm_model": "llama3.1",
  "system_prompt": "You are a concise, friendly support agent.",
  "language": "English",
  "voice": "default"
}
```

### Conversation

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/conversation/start` | Start a session; optional `agent_id`, `system_prompt`, `provider_name`. |
| `POST` | `/api/conversation/{session_id}/message` | Send a user message; returns `LLMResponse` and records usage. |
| `POST` | `/api/conversation/{session_id}/end` | End the session; returns total turns. |
| `GET` | `/api/conversation/{session_id}/history` | Get the session transcript. |

**Message response shape**

```json
{
  "text": "How can I help you today?",
  "intent": "",
  "should_end_call": false,
  "should_transfer": false,
  "collected_information": {},
  "usage": { "input_tokens": 120, "output_tokens": 18, "total_tokens": 138 },
  "provider": "ollama",
  "model": "llama3.1",
  "latency_ms": 842
}
```

### Text-to-speech

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/tts/synthesize` | Synthesize text via VEXYL-TTS; returns base64 WAV. |

**Synthesize request**

```json
{ "text": "Hello, how can I help?", "language": "en-IN", "style": "default" }
```

Returns `503` if VEXYL-TTS is not configured or unreachable, and `422` for unsupported language/style.

## Data Models

| Table | Purpose |
| --- | --- |
| `llm_config` | Singleton (id `1`) global provider config: active/fallback provider, Ollama URL/model, encrypted Gemini key, Gemini model, timeout. |
| `agents` | Agent definitions: name, description, optional per-agent provider/model, system prompt, language, voice, active flag, timestamps. |
| `llm_usage` | One row per LLM request: provider, model, token counts, estimated cost, latency, timestamp, optional `call_id`/`agent_id`. |

Tables are created automatically at startup. To reset local state, stop the backend and delete `backend/calling_agent.db`.

## Security

- **Encryption at rest** — Gemini API keys are encrypted with Fernet, deriving the cipher key from `APP_SECRET_KEY` via SHA-256.
- **Masked responses** — the API never returns a full key; only `prefix...suffix` masks are exposed.
- **No frontend secrets** — all provider calls happen server-side. The frontend only ever talks to `/api`.
- **Redacted errors** — authentication errors are sanitized before logging/returning.
- **CORS allowlist** — controlled by `CORS_ORIGINS`.

**Production checklist**

- Set a strong, unique `APP_SECRET_KEY` before storing any provider keys. Rotating it makes previously encrypted keys undecryptable.
- Serve the frontend over HTTPS and restrict `CORS_ORIGINS` to your real domain.
- Put the backend behind a reverse proxy / process manager (e.g., Nginx + systemd or a container).
- Do not expose `/docs` publicly if unintended.
- Keep `.env` out of version control.

## Testing

```bash
cd backend
source venv/bin/activate
pytest -q
```

Coverage includes:

- Provider factory selection, defaults, overrides, and unsupported-provider errors.
- `LLMResponse` / `ProviderStatus` serialization.
- Plain-text vs. structured-JSON response parsing.
- Gemini async health check behavior.
- API-key encrypt/decrypt round-trips and masking.

## Production Build

```bash
cd frontend
npm run build        # outputs to frontend/dist
npm run preview      # preview the production bundle
npm run lint         # Oxlint
```

For deployment, serve `frontend/dist` from a static host (or have the backend serve it) and point the `/api` proxy at your backend origin. Run the backend with a production server:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Troubleshooting

| Symptom | Likely cause / fix |
| --- | --- |
| Dashboard shows Ollama `disconnected` | Ollama isn't running or `OLLAMA_BASE_URL` is wrong. Run `ollama serve` and verify `curl http://localhost:11434/api/tags`. |
| Gemini `not_configured` | No key in `.env` or **LLM Settings**. Add one and retry the connection test. |
| `Unsupported LLM provider` | `LLM_PROVIDER` / agent override must be exactly `ollama` or `gemini`. |
| `Session not found` | Conversation sessions are in-memory; a backend restart clears them. Start a new call. |
| Microphone doesn't work | Use Chrome/Edge, serve over `localhost` or HTTPS, and allow mic permission. Typing still works. |
| No spoken replies | VEXYL-TTS may be offline; the app should fall back to browser speech. If neither works, check browser audio permissions. |
| `VEXYL-TTS is not configured` (503) | `VEXYL_TTS_URL` is empty. Set it, or leave TTS disabled. |
| CORS error in browser | Add your frontend origin to `CORS_ORIGINS` (comma-separated) and restart the backend. |
| Settings changes don't apply | The factory reads runtime config from the DB-backed settings; confirm the update succeeded and check the active provider on the dashboard. |

---

## License

Private. All rights reserved.
