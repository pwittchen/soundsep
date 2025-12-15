# Repository Guidelines

## Project Structure & Modules
- Core entrypoint: `demix.py` handles CLI parsing, YouTube/audio ingest, FFmpeg conversions, Spleeter stem separation, and output assembly.
- Tests: `test_demix.py` (pytest + unittest.mock) covers argument parsing, helpers, and workflow wiring; add new tests here.
- Assets/output: `output/` (contains `music/` for extracted audio and stems, `video/` for downloads and accompaniment video; cleaned by `--clean output`), `pretrained_models/` (downloaded once by Spleeter, can be wiped with `--clean models`).
- Misc: `requirements.txt` (runtime deps), `README.md` (setup/usage), `CLAUDE.md` (project notes).

## Build, Test, and Development
- Create env (example): `mkvirtualenv -p /Users/pw/.pyenv/versions/3.8.16/bin/python demix && workon demix`.
- Install deps: `pip install -r requirements.txt` (needs FFmpeg installed on PATH).
- Run CLI locally:
  - YouTube: `python demix.py -u "https://youtu.be/ID" -m 4stems -o output`
  - Local file: `python demix.py -f /path/to/song.wav -ss 0:30 -to 2:00 -t 0.9 -p -2`
- Tests: `pytest -v` (unit-level, no network/FFmpeg execution due to mocking).

## Coding Style & Naming
- Python 3.8+, 4-space indentation, prefer stdlib + installed deps (pytubefix, spleeter, ffmpeg bindings).
- Keep CLI args consistent with `argparse` setup in `parse_args`; reuse existing help text style.
- Functions are lowercase_with_underscores; constants ALL_CAPS. Keep side-effecting helpers small and composable.
- Suppress noisy subprocess output (stdout/stderr) unless explicitly needed.

## Testing Guidelines
- Add pytest coverage for new flags, edge cases, and error paths; mock heavy calls (`subprocess`, `YouTube`, filesystem) similar to existing tests.
- Use realistic sample arguments in `patch.object(sys, "argv", [...])`.
- When changing command construction, assert positional ordering in tests (e.g., `-ss` before `-i`).

## Commit & Pull Request Guidelines
- Follow recent history: short, imperative subject lines; reference issues with `closes #ID` when applicable (see `git log --oneline`).
- PRs should describe behavior changes, include sample CLI invocations, note test coverage, and call out any new external requirements (models, FFmpeg versions).
- If output format or directory layout changes, mention migration/cleanup steps (e.g., rerun with `--clean all`).

## Operational & Safety Notes
- Ensure `ffmpeg` and `ffprobe` are available before running (use `which ffmpeg`).
- Large model downloads occur on first separation; avoid committing `pretrained_models/` or `output/`.
- Prefer local testing; avoid network calls in tests and keep subprocesses mocked to prevent long runs.
