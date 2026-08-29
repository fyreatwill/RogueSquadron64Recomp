#!/usr/bin/env python3
"""Apply the bounded final callable-symbol rename to a generated snapshot."""

from pathlib import Path
import argparse


RENAMES = {
    "static_4_80106C50": "lvc_registerObjectiveBooleanCounts",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("generated_dir", type=Path)
    args = parser.parse_args()

    files = [args.generated_dir / "funcs.h"] + sorted(
        args.generated_dir.glob("funcs_*.c")
    )
    changed = 0
    for path in files:
        original = path.read_text()
        updated = original
        for old, new in RENAMES.items():
            updated = updated.replace(old, new)
        if updated != original:
            path.write_text(updated)
            changed += 1
    if changed == 0:
        raise SystemExit("no generated symbol matched; refusing a silent no-op")
    print(f"renamed {RENAMES['static_4_80106C50']} in {changed} generated files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
