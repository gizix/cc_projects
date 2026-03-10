"""Click CLI for the whisper transcriber."""

from __future__ import annotations

import os
import platform
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path

import click
from rich.console import Console
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from .audio_extractor import (
    SUPPORTED_AUDIO_EXTENSIONS,
    SUPPORTED_VIDEO_EXTENSIONS,
    extract_audio,
    is_audio_file,
    is_supported_file,
)
from .formatter import FORMAT_HANDLERS, save_transcript
from .transcriber import AVAILABLE_MODELS, Transcriber

console = Console()


@click.group()
def cli():
    """Whisper Transcriber — local video/audio transcription using faster-whisper."""


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--model", "-m", default=None, help="Whisper model size (default: base)")
@click.option("--language", "-l", default=None, help="Language code (default: auto-detect)")
@click.option(
    "--format", "-f", "fmt",
    default="txt",
    type=click.Choice(list(FORMAT_HANDLERS.keys())),
    help="Output format (default: txt)",
)
@click.option("--output", "-o", default=None, help="Output file path")
@click.option("--device", "-d", default=None, help="Device: cpu, cuda, auto")
@click.option("--beam-size", default=5, help="Beam size 1-10 (default: 5)")
@click.option("--no-vad", is_flag=True, help="Disable VAD silence filter")
@click.option("--keep-audio", is_flag=True, help="Keep extracted audio file")
def transcribe(file, model, language, fmt, output, device, beam_size, no_vad, keep_audio):
    """Transcribe a video or audio file."""
    file_path = Path(file)

    if not is_supported_file(file_path):
        all_exts = SUPPORTED_VIDEO_EXTENSIONS | SUPPORTED_AUDIO_EXTENSIONS
        console.print(f"[red]Unsupported file type. Supported: {', '.join(sorted(all_exts))}[/red]")
        sys.exit(1)

    audio_path = None
    extracted = False

    try:
        if not is_audio_file(file_path):
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                progress.add_task("Extracting audio...", total=None)
                tmp_dir = Path(os.getenv("TMP_DIR", "./tmp"))
                tmp_dir.mkdir(parents=True, exist_ok=True)
                audio_path = tmp_dir / f"{file_path.stem}_audio.wav"
                extract_audio(file_path, audio_path)
                extracted = True
        else:
            audio_path = file_path

        transcriber = Transcriber(model_size=model, device=device)

        segments = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            progress.add_task(f"Transcribing with model '{transcriber.model_size}'...", total=None)
            result = transcriber.transcribe(
                audio_path,
                language=language,
                beam_size=beam_size,
                vad_filter=not no_vad,
            )
            segments = result.segments

        output_path = save_transcript(result, output_path=output, fmt=fmt, input_path=file_path)

        console.print(f"[green]✓ Transcript saved:[/green] {output_path}")
        console.print(
            f"  Language: {result.language} ({result.language_probability:.0%} confidence)"
        )
        console.print(f"  Segments: {len(segments)}")
        console.print(f"  Duration: {result.duration:.1f}s")

    finally:
        if extracted and audio_path and not keep_audio:
            try:
                audio_path.unlink(missing_ok=True)
            except Exception:
                pass


@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("--model", "-m", default=None, help="Whisper model size")
@click.option("--language", "-l", default=None, help="Language code")
@click.option(
    "--format", "-f", "fmt",
    default="txt",
    type=click.Choice(list(FORMAT_HANDLERS.keys())),
    help="Output format (default: txt)",
)
@click.option("--device", "-d", default=None, help="Device: cpu, cuda, auto")
@click.option("--keep-audio", is_flag=True, help="Keep extracted audio files")
def batch(directory, model, language, fmt, device, keep_audio):
    """Transcribe all video/audio files in a directory."""
    dir_path = Path(directory)
    files = [f for f in dir_path.iterdir() if f.is_file() and is_supported_file(f)]

    if not files:
        console.print(f"[yellow]No supported video/audio files found in {directory}[/yellow]")
        sys.exit(0)

    console.print(f"Found [bold]{len(files)}[/bold] file(s) to transcribe.\n")

    transcriber = Transcriber(model_size=model, device=device)
    success, failed = 0, 0

    for i, file_path in enumerate(files, 1):
        console.print(f"[{i}/{len(files)}] {file_path.name}")
        audio_path = None
        extracted = False

        try:
            if not is_audio_file(file_path):
                tmp_dir = Path(os.getenv("TMP_DIR", "./tmp"))
                tmp_dir.mkdir(parents=True, exist_ok=True)
                audio_path = tmp_dir / f"{file_path.stem}_audio.wav"
                extract_audio(file_path, audio_path)
                extracted = True
            else:
                audio_path = file_path

            result = transcriber.transcribe(audio_path, language=language)
            output_path = save_transcript(result, fmt=fmt, input_path=file_path)
            console.print(f"  [green]✓[/green] Saved: {output_path.name}")
            success += 1

        except Exception as e:
            console.print(f"  [red]✗ Failed:[/red] {e}")
            failed += 1

        finally:
            if extracted and audio_path and not keep_audio:
                try:
                    audio_path.unlink(missing_ok=True)
                except Exception:
                    pass

    console.print(f"\n[bold]Done.[/bold] {success} succeeded, {failed} failed.")


@cli.command("extract-audio")
@click.argument("file", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Output WAV path")
@click.option("--sample-rate", default=16000, help="Sample rate in Hz (default: 16000)")
def extract_audio_cmd(file, output, sample_rate):
    """Extract audio track from a video file."""
    file_path = Path(file)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        progress.add_task("Extracting audio...", total=None)
        out_path = extract_audio(file_path, output, sample_rate=sample_rate)

    console.print(f"[green]✓ Audio extracted:[/green] {out_path}")


@cli.command("list-models")
def list_models():
    """Show available Whisper models with speed and accuracy tradeoffs."""
    table = Table(title="Available Whisper Models", show_header=True)
    table.add_column("Model", style="bold cyan")
    table.add_column("Parameters")
    table.add_column("Speed (RTF)")
    table.add_column("VRAM")
    table.add_column("Description")

    for name, info in AVAILABLE_MODELS.items():
        table.add_row(
            name,
            info["parameters"],
            info["relative_speed"],
            info["vram"],
            info["description"],
        )

    console.print(table)
    console.print(
        "\n[dim]RTF = Real-Time Factor (seconds of audio processed per second).[/dim]"
    )
    console.print(
        "[dim]Default model: base. Override with --model or WHISPER_MODEL env var.[/dim]"
    )


@cli.command("convert-format")
@click.argument("file", type=click.Path(exists=True))
@click.argument("format", type=click.Choice(list(FORMAT_HANDLERS.keys())))
@click.option("--output", "-o", default=None, help="Output file path")
def convert_format(file, format, output):
    """Convert an existing JSON transcript to another format."""
    from .formatter import convert_transcript_file

    try:
        output_path = convert_transcript_file(file, format, output)
        console.print(f"[green]✓ Converted:[/green] {output_path}")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.command("list-devices")
def list_devices_cmd():
    """List audio input devices and identify loopback/system audio sources."""
    try:
        from .audio_recorder import find_loopback_device, list_devices
    except ImportError as e:
        console.print(f"[red]Import error:[/red] {e}")
        sys.exit(1)

    try:
        devices = list_devices()
    except ImportError as e:
        console.print(f"[red]sounddevice not installed:[/red] {e}")
        console.print("Run: [bold]uv add sounddevice soundfile numpy[/bold]")
        sys.exit(1)
    except RuntimeError as e:
        console.print(f"[red]Error querying devices:[/red] {e}")
        sys.exit(1)

    table = Table(title="Audio Input Devices", show_header=True)
    table.add_column("Index", style="cyan", justify="right")
    table.add_column("Name")
    table.add_column("Host API")
    table.add_column("Channels", justify="right")
    table.add_column("Sample Rate", justify="right")
    table.add_column("Loopback")

    for dev in devices:
        loopback_marker = "[bold green]YES[/bold green]" if dev.is_loopback else ""
        name_display = f"[bold]{dev.name}[/bold]" if dev.is_loopback else dev.name
        table.add_row(
            str(dev.index),
            name_display,
            dev.hostapi,
            str(dev.max_input_channels),
            f"{dev.default_samplerate:.0f} Hz",
            loopback_marker,
        )

    console.print(table)

    loopback = find_loopback_device()
    if loopback:
        console.print(f"\n[green]Auto-detected loopback:[/green] [{loopback.index}] {loopback.name}")
        console.print(f"[dim]Use with:[/dim] uv run python -m src.cli record --device {loopback.index}")
    else:
        system = platform.system()
        console.print("\n[yellow]No loopback device detected.[/yellow]")
        if system == "Windows":
            console.print("  Enable 'Stereo Mix' in Sound settings → Recording → Show Disabled Devices.")
        elif system == "Darwin":
            console.print("  Install BlackHole: https://existential.audio/blackhole/")
        else:
            console.print("  Use PulseAudio monitor sources. Look for devices ending in '.monitor'.")


@cli.command("record")
@click.option("--duration", "-d", default=None, type=float, help="Max recording duration in seconds (omit for Ctrl+C)")
@click.option("--device", default=None, help="Device index or name substring (default: auto-detect loopback)")
@click.option("--model", "-m", default=None, help="Whisper model size (default: base)")
@click.option(
    "--format", "-f", "fmt",
    default="txt",
    type=click.Choice(list(FORMAT_HANDLERS.keys())),
    help="Transcript output format (default: txt)",
)
@click.option("--output", "-o", default=None, help="Transcript output file path")
@click.option("--no-transcribe", is_flag=True, help="Save WAV only — skip transcription")
def record_cmd(duration, device, model, fmt, output, no_transcribe):
    """Record system/browser audio in real-time and transcribe it with Whisper."""
    try:
        from .audio_recorder import (
            find_loopback_device,
            get_device_by_index_or_name,
            record_audio,
        )
    except ImportError as e:
        console.print(f"[red]Import error:[/red] {e}")
        sys.exit(1)

    # Resolve recording device
    try:
        if device is not None:
            audio_device = get_device_by_index_or_name(device)
        else:
            audio_device = find_loopback_device()
            if audio_device is None:
                console.print(
                    "[red]No loopback device found.[/red] Run [bold]/list-devices[/bold] "
                    "and pass [bold]--device <index>[/bold]."
                )
                sys.exit(1)
    except (ValueError, ImportError) as e:
        console.print(f"[red]Device error:[/red] {e}")
        sys.exit(1)

    duration_str = f"{duration:.0f}s" if duration else "until Ctrl+C"
    console.print(f"[bold]Recording device:[/bold] [{audio_device.index}] {audio_device.name}")
    console.print(f"[bold]Duration:[/bold] {duration_str}")
    if not no_transcribe:
        console.print(f"[bold]Model:[/bold] {model or 'base'}  [bold]Format:[/bold] {fmt}")
    console.print("[dim]Press Ctrl+C to stop early.[/dim]\n")

    # Create temp WAV path
    tmp_dir = Path(os.getenv("TMP_DIR", "./tmp"))
    tmp_dir.mkdir(parents=True, exist_ok=True)
    wav_path = tmp_dir / f"recording_{int(time.time())}.wav"

    stop_event = threading.Event()
    recording_result = None

    try:
        # Elapsed timer rendered with Rich Live
        start_ts = time.monotonic()

        def _live_content():
            elapsed = time.monotonic() - start_ts
            mins, secs = divmod(int(elapsed), 60)
            return f"[cyan]Recording...[/cyan]  [bold]{mins:02d}:{secs:02d}[/bold] elapsed"

        timer_done = threading.Event()

        def _render_loop(live: Live):
            while not timer_done.is_set():
                live.update(_live_content())
                time.sleep(0.25)

        with Live(_live_content(), console=console, refresh_per_second=4) as live:
            render_thread = threading.Thread(target=_render_loop, args=(live,), daemon=True)
            render_thread.start()
            try:
                recording_result = record_audio(
                    output_path=wav_path,
                    duration=duration,
                    device=audio_device,
                    stop_event=stop_event,
                )
            except KeyboardInterrupt:
                stop_event.set()
            finally:
                timer_done.set()

    except RuntimeError as e:
        console.print(f"\n[red]Recording error:[/red] {e}")
        sys.exit(1)
    except ImportError as e:
        console.print(f"\n[red]Missing dependency:[/red] {e}")
        console.print("Run: [bold]uv add sounddevice soundfile numpy[/bold]")
        sys.exit(1)

    if recording_result is None:
        console.print("[red]Recording failed — no output produced.[/red]")
        sys.exit(1)

    console.print(f"\n[green]✓ Recorded:[/green] {recording_result.duration:.1f}s → {wav_path}")

    if no_transcribe:
        console.print(f"[dim]WAV saved at {wav_path} (--no-transcribe set)[/dim]")
        return

    # Transcribe the captured WAV
    transcriber = Transcriber(model_size=model)

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            progress.add_task(f"Transcribing with model '{transcriber.model_size}'...", total=None)
            result = transcriber.transcribe(wav_path, vad_filter=True)

        output_path = save_transcript(result, output_path=output, fmt=fmt, input_path=wav_path)
        console.print(f"[green]✓ Transcript saved:[/green] {output_path}")
        console.print(f"  Language: {result.language} ({result.language_probability:.0%} confidence)")
        console.print(f"  Segments: {len(result.segments)}")
        console.print(f"  Duration: {result.duration:.1f}s")

    finally:
        try:
            wav_path.unlink(missing_ok=True)
        except Exception:
            pass


if __name__ == "__main__":
    cli()
