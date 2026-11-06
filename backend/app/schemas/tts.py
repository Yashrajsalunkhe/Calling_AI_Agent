"""Request and response models for text-to-speech."""

from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    """Text and voice options sent to the configured TTS provider."""

    text: str = Field(min_length=1, max_length=5000)
    language: str = "en-IN"
    style: str = "default"


class TTSResponse(BaseModel):
    """Synthesized WAV audio encoded for browser playback."""

    audio_b64: str
    content_type: str = "audio/wav"
    language: str
    style: str
    cached: bool = False
    latency_ms: int = 0