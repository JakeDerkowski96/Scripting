"""Allow `python -m repo_radar`, which works without the console script on PATH."""

import sys

from repo_radar.cli import main

sys.exit(main())
