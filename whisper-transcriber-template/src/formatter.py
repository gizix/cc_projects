"""Transcript output format converters (txt, srt, vtt, json)."""

from __future__ import annotations

import json
from pathlib import Path

from .transcriber import TranscriptionResult


def _seconds_to_srt_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _seconds_to_vtt_timestamp(seconds: float) -> str:
    """Convert seconds to VTT timestamp format: HH:MM:SS.mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def to_txt(result: TranscriptionResult) -> str:
    """Format transcript as plain text (no timestamps)."""
    lines = []
    for segment in result.segments:
        text = segment.text.strip()
        if text:
            lines.append(text)
    return "\n".join(lines)


def to_srt(result: TranscriptionResult) -> str:
    """Format transcript as SRT subtitle format."""
    blocks = []
    for segment in result.segments:
        text = segment.text.strip()
        if not text:
            continue
        index = segment.id + 1
        start = _seconds_to_srt_timestamp(segment.start)
        end = _seconds_to_srt_timestamp(segment.end)
        blocks.append(f"{index}\n{start} --> {end}\n{text}\n")
    return "\n".join(blocks)


def to_vtt(result: TranscriptionResult) -> str:
    """Format transcript as WebVTT subtitle format."""
    lines = ["WEBVTT", ""]
    for segment in result.segments:
        text = segment.text.strip()
        if not text:
            continue
        start = _seconds_to_vtt_timestamp(segment.start)
        end = _seconds_to_vtt_timestamp(segment.end)
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)


def to_json(result: TranscriptionResult) -> str:
    """Format transcript as structured JSON with metadata and timestamps."""
    data = {
        "file": result.file,
        "language": result.language,
        "language_probability": round(result.language_probability, 4),
        "duration": round(result.duration, 2),
        "model": result.model,
        "segments": [
            {
                "id": seg.id,
                "start": round(seg.start, 3),
                "end": round(seg.end, 3),
                "text": seg.text.strip(),
                "avg_logprob": round(seg.avg_logprob, 4),
                "no_speech_prob": round(seg.no_speech_prob, 4),
            }
            for seg in result.segments
            if seg.text.strip()
        ],
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


FORMAT_HANDLERS = {
    "txt": to_txt,
    "srt": to_srt,
    "vtt": to_vtt,
    "json": to_json,
}


def format_result(result: TranscriptionResult, fmt: str) -> str:
    """Convert a TranscriptionResult to the specified format string.

    Args:
        result: The transcription result to format.
        fmt: Output format — one of "txt", "srt", "vtt", "json".

    Returns:
        Formatted string content.

    Raises:
        ValueError: If fmt is not a supported format.
    """
    fmt = fmt.lower().lstrip(".")
    if fmt not in FORMAT_HANDLERS:
        raise ValueError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(FORMAT_HANDLERS)}"
        )
    return FORMAT_HANDLERS[fmt](result)


def save_transcript(
    result: TranscriptionResult,
    output_path: str | Path | None = None,
    fmt: str = "txt",
    input_path: str | Path | None = None,
) -> Path:
    """Save a formatted transcript to disk.

    Args:
        result: The transcription result to save.
        output_path: Full output path. If None, derived from input_path.
        fmt: Output format — one of "txt", "srt", "vtt", "json".
        input_path: Source video/audio path, used to derive output path if needed.

    Returns:
        Path where the transcript was saved.
    """
    fmt = fmt.lower().lstrip(".")

    if output_path is None:
        if input_path is None:
            raise ValueError("Either output_path or input_path must be provided.")
        output_path = Path(input_path).with_suffix(f".{fmt}")
    else:
        output_path = Path(output_path)

    content = format_result(result, fmt)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def convert_transcript_file(
    input_path: str | Path,
    output_fmt: str,
    output_path: str | Path | None = None,
) -> Path:
    """Convert an existing transcript file to a different format.

    Currently supports JSON → any format (JSON has all the metadata needed).
    For txt/srt/vtt inputs, only txt output is supported (no timestamp data).

    Args:
        input_path: Path to existing transcript file (must be JSON for format conversion).
        output_fmt: Target format.
        output_path: Output file path. If None, derived from input_path.

    Returns:
        Path to the converted transcript.
    """
    input_path = Path(input_path)
    output_fmt = output_fmt.lower().lstrip(".")

    if input_path.suffix.lower() != ".json":
        raise ValueError(
            "Full format conversion requires a JSON transcript (which contains timestamps). "
            "TXT/SRT/VTT transcripts do not have enough metadata for conversion."
        )

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    from .transcriber import Segment, TranscriptionResult

    segments = [
        Segment(
            id=seg["id"],
            start=seg["start"],
            end=seg["end"],
            text=seg["text"],
            avg_logprob=seg.get("avg_logprob", 0.0),
            no_speech_prob=seg.get("no_speech_prob", 0.0),
        )
        for seg in data["segments"]
    ]

    result = TranscriptionResult(
        file=data["file"],
        language=data["language"],
        language_probability=data["language_probability"],
        duration=data["duration"],
        model=data["model"],
        segments=segments,
    )

    if output_path is None:
        output_path = input_path.with_suffix(f".{output_fmt}")
    else:
        output_path = Path(output_path)

    content = format_result(result, output_fmt)
    output_path.write_text(content, encoding="utf-8")
    return output_path
