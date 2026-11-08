"""Allow ``python -m skill_sync``."""

import sys

from skill_sync.cli import main

if __name__ == "__main__":
    sys.exit(main())
