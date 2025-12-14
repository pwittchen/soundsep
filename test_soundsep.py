import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import pytest

from soundsep import (
    __version__,
    STEM_MODES,
    Spinner,
    parse_args,
    remove_dir,
    clean,
    convert_wav_to_mp3,
    convert_to_mp3,
    separate_audio,
    download_video,
    create_empty_mkv_with_audio,
)


class TestVersion:
    def test_version_is_string(self):
        assert isinstance(__version__, str)

    def test_version_format(self):
        parts = __version__.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)


class TestStemModes:
    def test_2stems_mode(self):
        assert "2stems" in STEM_MODES
        assert STEM_MODES["2stems"] == ["vocals", "accompaniment"]

    def test_4stems_mode(self):
        assert "4stems" in STEM_MODES
        assert STEM_MODES["4stems"] == ["vocals", "drums", "bass", "other"]

    def test_5stems_mode(self):
        assert "5stems" in STEM_MODES
        assert STEM_MODES["5stems"] == ["vocals", "drums", "bass", "piano", "other"]

    def test_all_modes_have_vocals(self):
        for mode, stems in STEM_MODES.items():
            assert "vocals" in stems, f"Mode {mode} should have vocals"


class TestParseArgs:
    def test_url_argument(self):
        with patch.object(sys, "argv", ["soundsep", "-u", "https://youtube.com/watch?v=test"]):
            args = parse_args()
            assert args.url == "https://youtube.com/watch?v=test"

    def test_default_output(self):
        with patch.object(sys, "argv", ["soundsep", "-u", "https://youtube.com/watch?v=test"]):
            args = parse_args()
            assert args.output == "output"

    def test_custom_output(self):
        with patch.object(sys, "argv", ["soundsep", "-u", "https://test.com", "-o", "my_output"]):
            args = parse_args()
            assert args.output == "my_output"

    def test_default_resolution(self):
        with patch.object(sys, "argv", ["soundsep", "-u", "https://test.com"]):
            args = parse_args()
            assert args.resolution == "1280x720"

    def test_custom_resolution(self):
        with patch.object(sys, "argv", ["soundsep", "-u", "https://test.com", "-r", "1920x1080"]):
            args = parse_args()
            assert args.resolution == "1920x1080"

    def test_default_tempo(self):
        with patch.object(sys, "argv", ["soundsep", "-u", "https://test.com"]):
            args = parse_args()
            assert args.tempo == 1.0

    def test_custom_tempo(self):
        with patch.object(sys, "argv", ["soundsep", "-u", "https://test.com", "-t", "0.8"]):
            args = parse_args()
            assert args.tempo == 0.8

    def test_default_mode(self):
        with patch.object(sys, "argv", ["soundsep", "-u", "https://test.com"]):
            args = parse_args()
            assert args.mode == "2stems"

    def test_mode_4stems(self):
        with patch.object(sys, "argv", ["soundsep", "-u", "https://test.com", "-m", "4stems"]):
            args = parse_args()
            assert args.mode == "4stems"

    def test_mode_5stems(self):
        with patch.object(sys, "argv", ["soundsep", "-u", "https://test.com", "-m", "5stems"]):
            args = parse_args()
            assert args.mode == "5stems"

    def test_clean_argument(self):
        with patch.object(sys, "argv", ["soundsep", "-c", "output"]):
            args = parse_args()
            assert args.clean == "output"

    def test_clean_models(self):
        with patch.object(sys, "argv", ["soundsep", "-c", "models"]):
            args = parse_args()
            assert args.clean == "models"

    def test_clean_all(self):
        with patch.object(sys, "argv", ["soundsep", "-c", "all"]):
            args = parse_args()
            assert args.clean == "all"


class TestSpinner:
    def test_spinner_init(self):
        spinner = Spinner("Test message")
        assert spinner.message == "Test message"
        assert spinner.spinning is False
        assert spinner.thread is None

    def test_spinner_default_message(self):
        spinner = Spinner()
        assert spinner.message == "Loading..."

    def test_spinner_context_manager(self):
        with patch.object(Spinner, "start") as mock_start:
            with patch.object(Spinner, "stop") as mock_stop:
                with Spinner("Test"):
                    mock_start.assert_called_once()
                mock_stop.assert_called_once_with(success=True)

    def test_spinner_context_manager_on_exception(self):
        with patch.object(Spinner, "start"):
            with patch.object(Spinner, "stop") as mock_stop:
                try:
                    with Spinner("Test"):
                        raise ValueError("Test error")
                except ValueError:
                    pass
                mock_stop.assert_called_once_with(success=False)


class TestRemoveDir:
    def test_remove_existing_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = os.path.join(tmpdir, "test_remove")
            os.makedirs(test_dir)
            assert os.path.exists(test_dir)
            remove_dir(test_dir)
            assert not os.path.exists(test_dir)

    def test_remove_nonexistent_directory(self, capsys):
        remove_dir("/nonexistent/path/that/does/not/exist")
        captured = capsys.readouterr()
        assert "does not exist" in captured.out


class TestClean:
    def test_clean_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = os.path.join(tmpdir, "output")
            os.makedirs(output_dir)
            assert os.path.exists(output_dir)
            clean("output", output_dir)
            assert not os.path.exists(output_dir)

    def test_clean_models(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                models_dir = os.path.join(tmpdir, "pretrained_models")
                os.makedirs(models_dir)
                assert os.path.exists(models_dir)
                clean("models")
                assert not os.path.exists(models_dir)
            finally:
                os.chdir(original_cwd)

    def test_clean_all(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                output_dir = os.path.join(tmpdir, "output")
                models_dir = os.path.join(tmpdir, "pretrained_models")
                os.makedirs(output_dir)
                os.makedirs(models_dir)
                clean("all", output_dir)
                assert not os.path.exists(output_dir)
                assert not os.path.exists(models_dir)
            finally:
                os.chdir(original_cwd)


class TestConvertWavToMp3:
    @patch("soundsep.subprocess.run")
    @patch("soundsep.os.makedirs")
    def test_convert_without_tempo_change(self, mock_makedirs, mock_run):
        convert_wav_to_mp3("/input/file.wav", "/output/file.mp3", tempo=1.0)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "ffmpeg" in args
        assert "-i" in args
        assert "-af" not in args

    @patch("soundsep.subprocess.run")
    @patch("soundsep.os.makedirs")
    def test_convert_with_tempo_in_range(self, mock_makedirs, mock_run):
        convert_wav_to_mp3("/input/file.wav", "/output/file.mp3", tempo=0.8)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "-af" in args
        af_index = args.index("-af")
        assert "atempo=0.8" in args[af_index + 1]

    @patch("soundsep.subprocess.run")
    @patch("soundsep.os.makedirs")
    def test_convert_with_tempo_below_half(self, mock_makedirs, mock_run):
        convert_wav_to_mp3("/input/file.wav", "/output/file.mp3", tempo=0.25)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "-af" in args
        af_index = args.index("-af")
        # Should chain multiple atempo filters for values < 0.5 tempo
        assert "atempo=0.5" in args[af_index + 1]

    @patch("soundsep.subprocess.run")
    @patch("soundsep.os.makedirs")
    def test_convert_with_tempo_above_two(self, mock_makedirs, mock_run):
        convert_wav_to_mp3("/input/file.wav", "/output/file.mp3", tempo=3.0)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "-af" in args
        af_index = args.index("-af")
        # Should chain multiple atempo filters for values > 2.0 tempo
        assert "atempo=2.0" in args[af_index + 1]


class TestConvertToMp3:
    @patch("soundsep.subprocess.run")
    def test_convert_to_mp3_calls_ffmpeg(self, mock_run):
        convert_to_mp3("/input/video.mp4", "/output/audio.mp3")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "ffmpeg"
        assert "-i" in args
        assert "/input/video.mp4" in args
        assert "/output/audio.mp3" in args
        assert "-ar" in args
        assert "44100" in args


class TestSeparateAudio:
    @patch("soundsep.subprocess.run")
    def test_separate_audio_default_mode(self, mock_run):
        separate_audio("/input/music.mp3", "/output")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "spleeter"
        assert "separate" in args
        assert "-p" in args
        assert "spleeter:2stems" in args

    @patch("soundsep.subprocess.run")
    def test_separate_audio_4stems(self, mock_run):
        separate_audio("/input/music.mp3", "/output", mode="4stems")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "spleeter:4stems" in args

    @patch("soundsep.subprocess.run")
    def test_separate_audio_5stems(self, mock_run):
        separate_audio("/input/music.mp3", "/output", mode="5stems")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "spleeter:5stems" in args


class TestDownloadVideo:
    @patch("soundsep.YouTube")
    @patch("soundsep.os.makedirs")
    def test_download_video(self, mock_makedirs, mock_youtube):
        mock_stream = MagicMock()
        mock_stream.mime_type = "audio/mp4"
        mock_stream.download.return_value = None
        mock_yt = MagicMock()
        mock_yt.streams.filter.return_value.order_by.return_value.desc.return_value.first.return_value = mock_stream
        mock_youtube.return_value = mock_yt

        result = download_video("https://youtube.com/watch?v=test", "/output")

        mock_makedirs.assert_called_once_with("/output", exist_ok=True)
        mock_youtube.assert_called_once_with("https://youtube.com/watch?v=test")
        assert result == "/output/video.mp4"


class TestCreateEmptyMkvWithAudio:
    @patch("soundsep.subprocess.run")
    @patch("soundsep.subprocess.check_output")
    @patch("soundsep.os.makedirs")
    def test_create_empty_mkv(self, mock_makedirs, mock_check_output, mock_run):
        mock_check_output.return_value = b"120.5\n"
        create_empty_mkv_with_audio("/input/audio.mp3", "/output/video.mkv")

        # Check ffprobe was called to get duration
        mock_check_output.assert_called_once()

        # Check ffmpeg was called to create video
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "ffmpeg" in args
        assert "1280x720" in str(args)  # default resolution

    @patch("soundsep.subprocess.run")
    @patch("soundsep.subprocess.check_output")
    @patch("soundsep.os.makedirs")
    def test_create_empty_mkv_custom_resolution(self, mock_makedirs, mock_check_output, mock_run):
        mock_check_output.return_value = b"120.5\n"
        create_empty_mkv_with_audio("/input/audio.mp3", "/output/video.mkv", resolution="1920x1080")

        args = mock_run.call_args[0][0]
        assert "1920x1080" in str(args)
