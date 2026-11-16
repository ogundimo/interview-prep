#!/usr/bin/env python3
"""Entry point: `python scripts/prep.py <command>` (or `prep` after `pip install -e .`)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prepkit.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
