import numpy as np
import pytest

from conftest import needs_ffmpeg

from earmark import audio


def test_silence_length():
    assert len(audio.silence(0.5, 24000)) == 12000


def test_format_duration():
    assert audio.format_duration(0) == "0:00:00"
    assert audio.format_duration(3661) == "1:01:01"
    assert audio.format_duration(59.6) == "0:01:00"


@needs_ffmpeg
def test_encode_produces_a_playable_mp3(tmp_path):
    out = tmp_path / "out.mp3"
    tone = np.sin(np.linspace(0, 400 * 2 * np.pi, 24000 * 2)).astype(np.float32) * 0.2
    written = audio.encode([tone, audio.silence(0.5), tone], out)
    assert written == 24000 * 2 * 2 + 12000
    assert out.exists() and out.stat().st_size > 1000
    assert out.read_bytes()[:3] in (b"ID3", b"\xff\xfb", b"\xff\xf3")


@needs_ffmpeg
def test_encode_rejects_an_empty_stream(tmp_path):
    with pytest.raises(RuntimeError, match="no speakable text"):
        audio.encode([], tmp_path / "empty.mp3")


@needs_ffmpeg
def test_duration_matches_samples(tmp_path):
    out = tmp_path / "d.mp3"
    written = audio.encode([audio.silence(3.0)], out)
    assert audio.duration_seconds(written) == pytest.approx(3.0, abs=0.01)
    # The file itself, not just the arithmetic: a wrong -ar pairing would
    # stretch or squash the audio and still report the input sample count.
    assert audio.probe_duration(out) == pytest.approx(3.0, abs=0.1)


@needs_ffmpeg
def test_encode_resamples_to_mpeg1(tmp_path):
    """24 kHz MP3 is MPEG-2, whose seek bar breaks in some players."""
    import subprocess

    out = tmp_path / "r.mp3"
    audio.encode([audio.silence(1.0)], out)
    rate = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0",
         "-show_entries", "stream=sample_rate", "-of", "csv=p=0", str(out)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert rate == str(audio.DEFAULT_SAMPLE_RATE)
