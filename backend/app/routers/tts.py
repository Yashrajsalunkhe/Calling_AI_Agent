"""Text-to-speech proxy for the self-hosted VEXYL-TTS service."""

import asyncio
import time

import httpx
from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.schemas.tts import TTSRequest, TTSResponse

router = APIRouter(prefix="/api/tts", tags=["tts"])

SUPPORTED_LANGUAGES = {
    "en-IN", "en-US", "en-GB", "hi-IN", "ml-IN", "ta-IN", "te-IN",
    "kn-IN", "bn-IN", "gu-IN", "mr-IN", "pa-IN", "or-IN", "as-IN",
    "ur-IN", "ne-IN", "sa-IN", "brx-IN", "doi-IN", "kok-IN", "mai-IN",
    "mni-IN", "sat-IN", "sd-IN",
}


@router.post("/synthesize", response_model=TTSResponse)
async def synthesize(req: TTSRequest):
    """Submit text to VEXYL-TTS and wait for its WAV result."""
    settings = get_settings()
    if not settings.VEXYL_TTS_URL:
        raise HTTPException(status_code=503, detail="VEXYL-TTS is not configured")
    if req.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=422, detail=f"Unsupported TTS language: {req.language}")
    if req.style not in {"default", "warm", "formal"}:
        raise HTTPException(status_code=422, detail=f"Unsupported TTS style: {req.style}")

    headers = {"X-API-Key": settings.VEXYL_TTS_API_KEY} if settings.VEXYL_TTS_API_KEY else {}
    started = time.perf_counter()

    try:
        async with httpx.AsyncClient(timeout=settings.VEXYL_TTS_TIMEOUT_SECONDS) as client:
            submitted = await client.post(
                f"{settings.VEXYL_TTS_URL.rstrip('/')}/batch/synthesize",
                json={"text": req.text, "lang": req.language, "style": req.style},
                headers=headers,
            )
            submitted.raise_for_status()
            job_id = submitted.json().get("job_id")
            if not job_id:
                raise RuntimeError("VEXYL-TTS did not return a job id")

            result = None
            deadline = time.perf_counter() + settings.VEXYL_TTS_TIMEOUT_SECONDS
            while time.perf_counter() < deadline:
                response = await client.get(
                    f"{settings.VEXYL_TTS_URL.rstrip('/')}/batch/result/{job_id}",
                    headers=headers,
                )
                if response.status_code == 200:
                    result = response.json()
                    break
                if response.status_code != 202:
                    response.raise_for_status()
                await asyncio.sleep(0.15)

            if not result or not result.get("audio_b64"):
                raise TimeoutError("VEXYL-TTS synthesis timed out")

    except (httpx.HTTPError, TimeoutError, RuntimeError) as error:
        raise HTTPException(status_code=503, detail=f"VEXYL-TTS unavailable: {error}") from error

    return TTSResponse(
        audio_b64=result["audio_b64"],
        language=req.language,
        style=req.style,
        cached=result.get("cached", False),
        latency_ms=round((time.perf_counter() - started) * 1000),
    )