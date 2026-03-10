"""Unit tests for src/audio_recorder.py — all hardware patched with mocks."""

from __future__ import annotations

import threading
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.audio_recorder import (
    WHISPER_CHANNELS,
    WHISPER_DTYPE,
    WHISPER_SAMPLE_RATE,
    AudioDevice,
    RecordingResult,
    _is_loopback_device,
    find_loopback_device,
    get_device_by_index_or_name,
    list_devices,
    record_audio,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_device(
    index=0,
    name="Test Device",
    hostapi="WASAPI",
    max_input_channels=2,
    default_samplerate=44100.0,
    is_loopback=False,
) -> AudioDevice:
    return AudioDevice(
        index=index,
        name=name,
        hostapi=hostapi,
        max_input_channels=max_input_channels,
        default_samplerate=default_samplerate,
        is_loopback=is_loopback,
    )


# ---------------------------------------------------------------------------
# TestIsLoopbackDevice
# ---------------------------------------------------------------------------

class TestIsLoopbackDevice:
    def test_windows_loopback_keyword(self):
        with patch("src.audio_recorder.platform.system", return_value="Windows"):
            assert _is_loopback_device("Speakers (Realtek) [Loopback]", "WASAPI") is True

    def test_windows_non_loopback(self):
        with patch("src.audio_recorder.platform.system", return_value="Windows"):
            assert _is_loopback_device("Microphone (USB Audio)", "WASAPI") is False

    def test_macos_blackhole(self):
        with patch("src.audio_recorder.platform.system", return_value="Darwin"):
            assert _is_loopback_device("BlackHole 2ch", "") is True

    def test_macos_soundflower(self):
        with patch("src.audio_recorder.platform.system", return_value="Darwin"):
            assert _is_loopback_device("Soundflower (2ch)", "") is True

    def test_macos_loopback_app(self):
        with patch("src.audio_recorder.platform.system", return_value="Darwin"):
            assert _is_loopback_device("Loopback Audio", "") is True

    def test_macos_non_loopback(self):
        with patch("src.audio_recorder.platform.system", return_value="Darwin"):
            assert _is_loopback_device("Built-in Microphone", "") is False

    def test_linux_pulse_monitor(self):
        with patch("src.audio_recorder.platform.system", return_value="Linux"):
            assert _is_loopback_device("alsa_output.pci-0000_00_1f.3.analog-stereo.monitor", "") is True

    def test_linux_non_monitor(self):
        with patch("src.audio_recorder.platform.system", return_value="Linux"):
            assert _is_loopback_device("alsa_input.pci-0000_00_1f.3.analog-stereo", "") is False


# ---------------------------------------------------------------------------
# TestListDevices
# ---------------------------------------------------------------------------

class TestListDevices:
    def _make_raw_devices(self):
        return [
            {"name": "Microphone", "hostapi": 0, "max_input_channels": 1, "default_samplerate": 44100.0},
            {"name": "Output Only", "hostapi": 0, "max_input_channels": 0, "default_samplerate": 44100.0},
            {"name": "Speakers [Loopback]", "hostapi": 0, "max_input_channels": 2, "default_samplerate": 44100.0},
        ]

    def _make_hostapis(self):
        return [{"name": "WASAPI"}]

    @patch("src.audio_recorder.platform.system", return_value="Windows")
    def test_filters_output_only_devices(self, _mock_sys):
        with patch("src.audio_recorder.platform.system", return_value="Windows"):
            with patch.dict("sys.modules", {"sounddevice": MagicMock()}):
                import sys
                sd_mock = sys.modules["sounddevice"]
                sd_mock.query_devices.return_value = self._make_raw_devices()
                sd_mock.query_hostapis.return_value = self._make_hostapis()

                devices = list_devices()

        names = [d.name for d in devices]
        assert "Output Only" not in names
        assert "Microphone" in names

    @patch("src.audio_recorder.platform.system", return_value="Windows")
    def test_flags_loopback_device(self, _mock_sys):
        with patch.dict("sys.modules", {"sounddevice": MagicMock()}):
            import sys
            sd_mock = sys.modules["sounddevice"]
            sd_mock.query_devices.return_value = self._make_raw_devices()
            sd_mock.query_hostapis.return_value = self._make_hostapis()

            devices = list_devices()

        loopback = next((d for d in devices if "Loopback" in d.name), None)
        assert loopback is not None
        assert loopback.is_loopback is True

    def test_import_error_raised(self):
        with patch.dict("sys.modules", {"sounddevice": None}):
            with pytest.raises(ImportError, match="sounddevice"):
                list_devices()


# ---------------------------------------------------------------------------
# TestFindLoopbackDevice
# ---------------------------------------------------------------------------

class TestFindLoopbackDevice:
    def test_returns_first_loopback(self):
        devices = [
            _make_device(index=0, name="Mic", is_loopback=False),
            _make_device(index=1, name="Speakers [Loopback]", is_loopback=True),
        ]
        with patch("src.audio_recorder.list_devices", return_value=devices):
            result = find_loopback_device()
        assert result is not None
        assert result.index == 1

    def test_returns_none_when_no_loopback(self):
        devices = [_make_device(index=0, name="Mic", is_loopback=False)]
        with patch("src.audio_recorder.list_devices", return_value=devices):
            result = find_loopback_device()
        assert result is None


# ---------------------------------------------------------------------------
# TestGetDeviceByIndexOrName
# ---------------------------------------------------------------------------

class TestGetDeviceByIndexOrName:
    def _devices(self):
        return [
            _make_device(index=0, name="Microphone Array"),
            _make_device(index=3, name="Speakers [Loopback]", is_loopback=True),
        ]

    def test_by_integer_index(self):
        with patch("src.audio_recorder.list_devices", return_value=self._devices()):
            dev = get_device_by_index_or_name(3)
        assert dev.name == "Speakers [Loopback]"

    def test_by_string_digit(self):
        with patch("src.audio_recorder.list_devices", return_value=self._devices()):
            dev = get_device_by_index_or_name("0")
        assert dev.name == "Microphone Array"

    def test_by_name_substring(self):
        with patch("src.audio_recorder.list_devices", return_value=self._devices()):
            dev = get_device_by_index_or_name("loopback")
        assert dev.is_loopback is True

    def test_raises_on_bad_index(self):
        with patch("src.audio_recorder.list_devices", return_value=self._devices()):
            with pytest.raises(ValueError, match="index 99"):
                get_device_by_index_or_name(99)

    def test_raises_on_bad_name(self):
        with patch("src.audio_recorder.list_devices", return_value=self._devices()):
            with pytest.raises(ValueError, match="nonexistent"):
                get_device_by_index_or_name("nonexistent")


# ---------------------------------------------------------------------------
# TestRecordAudio
# ---------------------------------------------------------------------------

class TestRecordAudio:
    def _make_device(self) -> AudioDevice:
        return _make_device(index=1, name="Speakers [Loopback]", is_loopback=True)

    def _fake_audio_chunk(self) -> np.ndarray:
        """Stereo int16 chunk of 1600 samples (0.1 s at 16kHz)."""
        return np.zeros((1600, 2), dtype=np.int16)

    @patch("soundfile.write")
    @patch("sounddevice.InputStream")
    def test_creates_wav_file(self, mock_stream_cls, mock_sf_write, tmp_path):
        out = tmp_path / "out.wav"
        device = self._make_device()
        chunk = self._fake_audio_chunk()

        # Simulate InputStream context manager delivering one chunk then stopping
        mock_ctx = MagicMock()
        mock_stream_cls.return_value.__enter__ = MagicMock(return_value=mock_ctx)
        mock_stream_cls.return_value.__exit__ = MagicMock(return_value=False)

        import queue as _queue

        real_queue = _queue.Queue()
        real_queue.put(chunk)

        with patch("src.audio_recorder.queue.Queue", return_value=real_queue):
            with patch("src.audio_recorder.time.monotonic", side_effect=[0.0, 0.15]):
                with patch.dict("sys.modules", {
                    "sounddevice": MagicMock(**{"InputStream": mock_stream_cls}),
                    "soundfile": MagicMock(**{"write": mock_sf_write}),
                    "numpy": np,
                }):
                    result = record_audio(
                        output_path=out,
                        duration=0.1,
                        device=device,
                        sample_rate=WHISPER_SAMPLE_RATE,
                    )

        assert isinstance(result, RecordingResult)

    def test_raises_on_sounddevice_import_error(self, tmp_path):
        out = tmp_path / "out.wav"
        device = self._make_device()
        with patch.dict("sys.modules", {"sounddevice": None}):
            with pytest.raises(ImportError, match="sounddevice"):
                record_audio(output_path=out, duration=1, device=device)

    def test_raises_on_soundfile_import_error(self, tmp_path):
        out = tmp_path / "out.wav"
        device = self._make_device()
        with patch.dict("sys.modules", {"sounddevice": MagicMock(), "soundfile": None}):
            with pytest.raises(ImportError, match="soundfile"):
                record_audio(output_path=out, duration=1, device=device)
