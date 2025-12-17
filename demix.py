#!/usr/bin/env python
"""
Backwards-compatible wrapper for demix CLI.

This file is kept for backwards compatibility with `python demix.py` usage.
For new installations, use `pip install demix` and run `demix` directly.
"""
import sys
import os

# Add src directory to path for development usage
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from demix.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
