"""Tests for the transcription pipeline."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.formatter import (
    FORMAT_HANDLERS,
    format_result,
    to_json,
    to_srt,
    to_txt,
    to_vtt,
)
from src.transcriber import Segment, TranscriptionResult, Transcriber


@pytest.fixture
def sample_result():
    return TranscriptionResult(
        file="meeting.mp4",
        language="en",
        language_probability=0.99,
        duration=10.5,
        model="base",
        segments=[
            Segment(id=0, start=0.5, end=3.2, text=" Hello, welcome to the meeting."),
            Segment(id=1, start=3.5, end=7.0, text=" Today we will discuss the project."),
            Segment(id=2, start=7.2, end=10.1, text=" Let's get started."),
        ],
    )


class TestTranscriptionResult:
    def test_full_text(self, sample_result):
        text = sample_result.full_text
        assert "Hello, welcome to the meeting." in text
        assert "Today we will discuss the project." in text
        assert "Let's get started." in text

    def test_segment_count(self, sample_result):
        assert len(sample_result.segments) == 3


class TestFormatter:
    def test_to_txt(self, sample_result):
        output = to_txt(sample_result)
        assert "Hello, welcome to the meeting." in output
        assert "-->" not in output  # no timestamps in plain text

    def test_to_srt(self, sample_result):
        output = to_srt(sample_result)
        assert "00:00:00,500 --> 00:00:03,200" in output
        assert "Hello, welcome to the meeting." in output
        assert "1\n" in output

    def test_to_vtt(self, sample_result):
        output = to_vtt(sample_result)
        assert output.startswith("WEBVTT")
        assert "00:00:00.500 --> 00:00:03.200" in output
        assert "Hello, welcome to the meeting." in output

    def test_to_json(self, sample_result):
        import json

        output = to_json(sample_result)
        data = json.loads(output)
        assert data["language"] == "en"
        assert data["model"] == "base"
        assert len(data["segments"]) == 3
        assert data["segments"][0]["text"] == "Hello, welcome to the meeting."

    def test_format_result_unsupported(self, sample_result):
        with pytest.raises(ValueError, match="Unsupported format"):
            format_result(sample_result, "docx")

    def test_all_formats_available(self):
        assert set(FORMAT_HANDLERS.keys()) == {"txt", "srt", "vtt", "json"}


class TestTranscriber:
    def test_init_defaults(self):
        t = Transcriber()
        assert t.model_size == "base"
        assert t.device == "auto"
        assert t.compute_type == "int8"

    def test_init_custom(self):
        t = Transcriber(model_size="medium", device="cpu", compute_type="float32")
        assert t.model_size == "medium"
        assert t.device == "cpu"
        assert t.compute_type == "float32"

    def test_lazy_model_loading(self):
        t = Transcriber()
        assert t._model is None  # model not loaded at init

    def test_transcribe_calls_whisper(self, tmp_path):
        audio_file = tmp_path / "test.wav"
        audio_file.write_bytes(b"fake audio data")

        mock_segment = MagicMock()
        mock_segment.start = 0.0
        mock_segment.end = 2.0
        mock_segment.text = " Test transcription."
        mock_segment.avg_logprob = -0.3
        mock_segment.no_speech_prob = 0.1

        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.99
        mock_info.duration = 2.0

        mock_model = MagicMock()
        mock_model.transcribe.return_value = ([mock_segment], mock_info)

        with patch("src.transcriber.WhisperModel", return_value=mock_model):
            t = Transcriber(model_size="base", device="cpu")
            result = t.transcribe(audio_file)

        assert result.language == "en"
        assert len(result.segments) == 1
        assert result.segments[0].text == " Test transcription."

    def test_transcribe_missing_file(self):
        t = Transcriber()
        with pytest.raises(FileNotFoundError):
            t.transcribe("/nonexistent/path/audio.wav")


class TestSRTTimestamp:
    def test_zero(self):
        from src.formatter import _seconds_to_srt_timestamp

        assert _seconds_to_srt_timestamp(0.0) == "00:00:00,000"

    def test_one_hour(self):
        from src.formatter import _seconds_to_srt_timestamp

        assert _seconds_to_srt_timestamp(3600.0) == "01:00:00,000"

    def test_milliseconds(self):
        from src.formatter import _seconds_to_srt_timestamp

        assert _seconds_to_srt_timestamp(1.5) == "00:00:01,500"
