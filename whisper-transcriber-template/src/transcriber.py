"""Transcription engine using faster-whisper."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator, Literal

from dotenv import load_dotenv

load_dotenv()

ComputeType = Literal["int8", "float16", "int8_float16", "float32"]
DeviceType = Literal["cpu", "cuda", "auto"]


@dataclass
class Segment:
    """A single transcription segment with timing information."""

    id: int
    start: float
    end: float
    text: str
    avg_logprob: float = 0.0
    no_speech_prob: float = 0.0


@dataclass
class TranscriptionResult:
    """Complete transcription result with metadata."""

    file: str
    language: str
    language_probability: float
    duration: float
    model: str
    segments: list[Segment] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        """Return all segment text joined as a single string."""
        return " ".join(seg.text.strip() for seg in self.segments)


class Transcriber:
    """Wrapper around faster-whisper for audio transcription."""

    def __init__(
        self,
        model_size: str | None = None,
        device: DeviceType | None = None,
        compute_type: ComputeType | None = None,
    ) -> None:
        self.model_size = model_size or os.getenv("WHISPER_MODEL", "base")
        self.device = device or os.getenv("WHISPER_DEVICE", "auto")
        self.compute_type = compute_type or os.getenv("WHISPER_COMPUTE_TYPE", "int8")
        self._model = None

    def _load_model(self):
        """Lazily load the Whisper model."""
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as e:
                raise ImportError(
                    "faster-whisper is not installed. Run: pip install faster-whisper"
                ) from e

            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
        return self._model

    def transcribe(
        self,
        audio_path: str | Path,
        language: str | None = None,
        beam_size: int = 5,
        vad_filter: bool = True,
        word_timestamps: bool = False,
    ) -> TranscriptionResult:
        """Transcribe an audio file and return a TranscriptionResult.

        Args:
            audio_path: Path to the audio file (WAV, MP3, etc.)
            language: ISO language code or None for auto-detection.
            beam_size: Beam size for decoding (1=fastest, 10=most accurate).
            vad_filter: Enable Voice Activity Detection to skip silence.
            word_timestamps: Include per-word timestamps (slower).

        Returns:
            TranscriptionResult with all segments.
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        model = self._load_model()

        language = language or os.getenv("WHISPER_LANGUAGE") or None
        if not language:
            language = None

        raw_segments, info = model.transcribe(
            str(audio_path),
            beam_size=beam_size,
            language=language,
            vad_filter=vad_filter,
            vad_parameters={"min_silence_duration_ms": 500},
            word_timestamps=word_timestamps,
        )

        segments = []
        for i, seg in enumerate(raw_segments):
            segments.append(
                Segment(
                    id=i,
                    start=seg.start,
                    end=seg.end,
                    text=seg.text,
                    avg_logprob=seg.avg_logprob,
                    no_speech_prob=seg.no_speech_prob,
                )
            )

        return TranscriptionResult(
            file=str(audio_path),
            language=info.language,
            language_probability=info.language_probability,
            duration=info.duration,
            model=self.model_size,
            segments=segments,
        )

    def transcribe_streaming(
        self,
        audio_path: str | Path,
        language: str | None = None,
        beam_size: int = 5,
        vad_filter: bool = True,
    ) -> Generator[Segment, None, None]:
        """Stream transcription segments as they are produced.

        Yields Segment objects one at a time, useful for long files with progress display.
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        model = self._load_model()

        raw_segments, _ = model.transcribe(
            str(audio_path),
            beam_size=beam_size,
            language=language,
            vad_filter=vad_filter,
            vad_parameters={"min_silence_duration_ms": 500},
        )

        for i, seg in enumerate(raw_segments):
            yield Segment(
                id=i,
                start=seg.start,
                end=seg.end,
                text=seg.text,
                avg_logprob=seg.avg_logprob,
                no_speech_prob=seg.no_speech_prob,
            )


AVAILABLE_MODELS = {
    "tiny": {
        "parameters": "39M",
        "relative_speed": "~32x",
        "vram": "~1GB",
        "description": "Fastest. Good for quick previews or testing.",
    },
    "base": {
        "parameters": "74M",
        "relative_speed": "~16x",
        "vram": "~1GB",
        "description": "Default. Fast with good accuracy for most use cases.",
    },
    "small": {
        "parameters": "244M",
        "relative_speed": "~6x",
        "vram": "~2GB",
        "description": "Better accuracy with moderate speed.",
    },
    "medium": {
        "parameters": "769M",
        "relative_speed": "~2x",
        "vram": "~5GB",
        "description": "High accuracy. Recommended for important meetings.",
    },
    "large-v3": {
        "parameters": "1550M",
        "relative_speed": "~1x",
        "vram": "~10GB",
        "description": "Best accuracy. Use when quality is critical.",
    },
}
