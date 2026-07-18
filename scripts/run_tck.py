#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import platform
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=1).run(suite)
    report = {
        "profile": "ASXP 0.2 Core",
        "implementation": "asxp-python-reference/0.2.0",
        "platform": platform.platform(),
        "time": datetime.now(timezone.utc).isoformat(),
        "testsRun": result.testsRun,
        "passed": result.wasSuccessful(),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
    }
    print(json.dumps(report, indent=2))
    if not result.wasSuccessful():
        print(output.getvalue(), file=sys.stderr)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
