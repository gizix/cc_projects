"""Audio extraction from video files using ffmpeg."""

import shutil
import subprocess
from pathlib import Path


def check_ffmpeg() -> bool:
    """Return True if ffmpeg is available on PATH."""
    return shutil.which("ffmpeg") is not None


def extract_audio(
    video_path: str | Path,
    output_path: str | Path | None = None,
    sample_rate: int = 16000,
    channels: int = 1,
) -> Path:
    """Extract audio from a video file using ffmpeg.

    Args:
        video_path: Path to the input video file.
        output_path: Path for the output WAV file. If None, derived from video_path.
        sample_rate: Audio sample rate in Hz. Whisper expects 16000.
        channels: Number of audio channels. Whisper expects mono (1).

    Returns:
        Path to the extracted audio file.

    Raises:
        RuntimeError: If ffmpeg is not found or extraction fails.
    """
    if not check_ffmpeg():
        raise RuntimeError(
            "ffmpeg not found on PATH. "
            "Install from https://ffmpeg.org/download.html or run /setup."
        )

    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if output_path is None:
        output_path = video_path.parent / f"{video_path.stem}_audio.wav"
    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-vn",                          # no video stream
        "-acodec", "pcm_s16le",         # 16-bit PCM WAV
        "-ar", str(sample_rate),        # sample rate (16kHz for Whisper)
        "-ac", str(channels),           # mono audio
        "-y",                           # overwrite existing output
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg extraction failed:\n{result.stderr}"
        )

    return output_path


def get_video_duration(video_path: str | Path) -> float:
    """Return duration of a video file in seconds using ffprobe."""
    if not shutil.which("ffprobe"):
        raise RuntimeError("ffprobe not found on PATH (usually installed with ffmpeg).")

    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed:\n{result.stderr}")

    return float(result.stdout.strip())


SUPPORTED_VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".mov", ".avi", ".webm",
    ".wmv", ".flv", ".m4v", ".ts", ".mts",
}

SUPPORTED_AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".flac", ".aac", ".ogg",
    ".m4a", ".wma", ".opus",
}


def is_supported_file(path: str | Path) -> bool:
    """Return True if the file extension is a supported video or audio format."""
    suffix = Path(path).suffix.lower()
    return suffix in SUPPORTED_VIDEO_EXTENSIONS | SUPPORTED_AUDIO_EXTENSIONS


def is_audio_file(path: str | Path) -> bool:
    """Return True if the file is a native audio format (skip extraction)."""
    return Path(path).suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS
