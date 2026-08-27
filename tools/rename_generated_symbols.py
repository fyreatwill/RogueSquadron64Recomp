#!/usr/bin/env python3
"""Rename a checked, bounded batch of stale generated function symbols."""

from pathlib import Path
import argparse
import re


RENAMES = {
    "fake_func_80082268": "cheatCodeConstantPreamble",
    "fake_func_800825C8": "rspbootTextPreamble",
    "fake_func_800AD378": "storeTrackedObjectAuxiliaryFields",
    "fake_func_800D2C98": "duplicateSymbolPrefixForNpcInitWithMotionParams",
    "fake_func_800D4EC4": "duplicateSymbolPrefixForNpcInitChildLinkedToParent",
    "fake_func_800DD2C4": "duplicateSymbolPrefixForNpcInitFullModel",
    "fake_func_800DFB8C": "duplicateSymbolPrefixForApplyCraftAnimAndDetailParams",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("generated_dir", type=Path)
    args = parser.parse_args()

    files = sorted(args.generated_dir.glob("funcs_*.c"))
    files.extend(
        [
            args.generated_dir / "funcs.h",
            args.generated_dir / "recomp_overlays.inl",
        ]
    )
    counts = {old: 0 for old in RENAMES}
    changed = []

    for path in files:
        text = path.read_text()
        updated = text
        for old, new in RENAMES.items():
            hits = len(re.findall(rf"\b{re.escape(old)}\b", text))
            counts[old] += hits
            updated = re.sub(rf"\b{re.escape(old)}\b", new, updated)
        if updated != text:
            path.write_text(updated)
            changed.append(path)

    missing = [old for old, count in counts.items() if count == 0]
    if missing:
        raise SystemExit("rename targets not found: " + ", ".join(missing))
    print(f"renamed {sum(counts.values())} references in {len(changed)} files")
    for old, count in counts.items():
        print(f"{old} -> {RENAMES[old]}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
