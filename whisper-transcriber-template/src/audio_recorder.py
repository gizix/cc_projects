"""Live audio recording from system/loopback devices using sounddevice."""

from __future__ import annotations

import platform
import queue
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


WHISPER_SAMPLE_RATE = 16000
WHISPER_CHANNELS = 1
WHISPER_DTYPE = "int16"


@dataclass
class AudioDevice:
    """Metadata for an audio input device."""

    index: int
    name: str
    hostapi: str
    max_input_channels: int
    default_samplerate: float
    is_loopback: bool = False


@dataclass
class RecordingResult:
    """Result of a completed recording session."""

    output_path: Path
    duration: float
    sample_rate: int
    channels: int
    device_name: str


def _is_loopback_device(name: str, hostapi: str) -> bool:
    """Return True if the device appears to be a loopback/system-audio capture source."""
    name_lower = name.lower()
    system = platform.system()

    if system == "Windows":
        # PortAudio WASAPI appends "[Loopback]" to mirrored output devices
        return "loopback" in name_lower
    elif system == "Darwin":
        # Common virtual audio drivers on macOS
        return any(k in name_lower for k in ("blackhole", "soundflower", "loopback"))
    else:
        # PulseAudio monitor sources end with ".monitor"
        return name_lower.endswith(".monitor")


def list_devices() -> list[AudioDevice]:
    """Return all audio input devices, with loopback devices flagged.

    Filters out pure output-only devices (max_input_channels == 0).
    Raises ImportError if sounddevice is not installed.
    """
    try:
        import sounddevice as sd
        raw = sd.query_devices()
        hostapis = sd.query_hostapis()
    except ImportError as exc:
        raise ImportError(
            "sounddevice is not installed. Run: pip install sounddevice"
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"Failed to query audio devices: {exc}") from exc

    devices: list[AudioDevice] = []
    for idx, dev in enumerate(raw):
        if dev["max_input_channels"] == 0:
            continue
        hostapi_name = hostapis[dev["hostapi"]]["name"] if dev["hostapi"] < len(hostapis) else ""
        devices.append(
            AudioDevice(
                index=idx,
                name=dev["name"],
                hostapi=hostapi_name,
                max_input_channels=dev["max_input_channels"],
                default_samplerate=dev["default_samplerate"],
                is_loopback=_is_loopback_device(dev["name"], hostapi_name),
            )
        )
    return devices


def find_loopback_device() -> AudioDevice | None:
    """Return the first loopback device found, or None."""
    for dev in list_devices():
        if dev.is_loopback:
            return dev
    return None


def get_device_by_index_or_name(identifier: int | str) -> AudioDevice:
    """Resolve a device by integer index or name substring.

    Args:
        identifier: Integer device index, string digit, or partial device name.

    Returns:
        Matching AudioDevice.

    Raises:
        ValueError: If no matching device is found.
    """
    devices = list_devices()

    # Integer or string digit → look up by index
    if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
        target_idx = int(identifier)
        for dev in devices:
            if dev.index == target_idx:
                return dev
        raise ValueError(f"No input device with index {target_idx}")

    # String → substring match on name (case-insensitive)
    name_lower = str(identifier).lower()
    for dev in devices:
        if name_lower in dev.name.lower():
            return dev
    raise ValueError(f"No input device matching name '{identifier}'")


def record_audio(
    output_path: str | Path,
    duration: float | None,
    device: AudioDevice,
    sample_rate: int = WHISPER_SAMPLE_RATE,
    channels: int = WHISPER_CHANNELS,
    stop_event: threading.Event | None = None,
) -> RecordingResult:
    """Record audio from *device* and save it as a 16kHz/int16 WAV file.

    Args:
        output_path: Destination WAV path.
        duration: Maximum recording length in seconds, or None to record until
                  *stop_event* is set or KeyboardInterrupt.
        device: AudioDevice to record from.
        sample_rate: Target sample rate (default: 16000 for Whisper).
        channels: Output channels (default: 1 / mono).
        stop_event: Optional threading.Event; recording stops when set.

    Returns:
        RecordingResult with path, duration, and metadata.

    Raises:
        ImportError: If sounddevice or soundfile are not installed.
        RuntimeError: If no audio was captured or a PortAudio error occurred.
    """
    try:
        import sounddevice as sd
    except ImportError as exc:
        raise ImportError(
            "sounddevice is not installed. Run: pip install sounddevice"
        ) from exc

    try:
        import soundfile as sf
    except ImportError as exc:
        raise ImportError(
            "soundfile is not installed. Run: pip install soundfile"
        ) from exc

    try:
        import numpy as np
    except ImportError as exc:
        raise ImportError(
            "numpy is not installed. Run: pip install numpy"
        ) from exc

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    audio_chunks: list[Any] = []
    audio_queue: queue.Queue = queue.Queue()
    record_error: list[Exception] = []

    def callback(indata, frames, time_info, status):
        if status:
            pass  # silently ignore under-/overruns during recording
        audio_queue.put(indata.copy())

    start_time = time.monotonic()

    try:
        with sd.InputStream(
            samplerate=sample_rate,
            channels=min(channels, device.max_input_channels),
            dtype=WHISPER_DTYPE,
            device=device.index,
            callback=callback,
        ):
            while True:
                elapsed = time.monotonic() - start_time
                if duration is not None and elapsed >= duration:
                    break
                if stop_event is not None and stop_event.is_set():
                    break
                try:
                    chunk = audio_queue.get(timeout=0.1)
                    audio_chunks.append(chunk)
                except queue.Empty:
                    continue

    except KeyboardInterrupt:
        pass  # drain remaining chunks below
    except Exception as exc:
        error_msg = str(exc)
        if "-9985" in error_msg or "Invalid device" in error_msg:
            raise RuntimeError(
                f"PortAudio error -9985: Device '{device.name}' is unavailable. "
                "Another application may have exclusive audio mode. "
                "Check Sound settings → Exclusive Mode and disable it."
            ) from exc
        raise RuntimeError(f"Recording failed: {exc}") from exc
    finally:
        # Drain any remaining chunks from the queue
        while not audio_queue.empty():
            try:
                audio_chunks.append(audio_queue.get_nowait())
            except queue.Empty:
                break

    if not audio_chunks:
        raise RuntimeError("No audio was captured. Ensure audio is playing and the device is active.")

    audio = np.concatenate(audio_chunks, axis=0)

    # Downmix to mono if needed
    if audio.ndim > 1 and audio.shape[1] > 1:
        audio = audio.mean(axis=1).astype(np.int16)
    elif audio.ndim > 1:
        audio = audio[:, 0]

    actual_duration = len(audio) / sample_rate

    sf.write(str(output_path), audio, sample_rate, subtype="PCM_16")

    return RecordingResult(
        output_path=output_path,
        duration=actual_duration,
        sample_rate=sample_rate,
        channels=1,
        device_name=device.name,
    )
