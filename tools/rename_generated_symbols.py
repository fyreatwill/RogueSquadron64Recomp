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
    "func_800E9AE0": "func_mission_overlay_800E9AE0",
}


def companion_renames(symbol_dir: Path, generated_text: str) -> dict[str, str]:
    """Return only semantic companion names for placeholders in the snapshot."""
    result = {}
    for symbol_file in sorted(symbol_dir.glob("*.txt")):
        for line in symbol_file.read_text().splitlines():
            match = re.match(
                r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*0x([0-9A-Fa-f]{8});", line
            )
            if not match:
                continue
            name, address = match.groups()
            if name.startswith(("D_", "fake_func_", "func_")):
                continue
            old = f"func_{address.upper()}"
            if re.search(rf"\b{re.escape(old)}\b", generated_text):
                result[old] = name
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("generated_dir", type=Path)
    parser.add_argument(
        "--companion-dir",
        type=Path,
        help="add exact semantic renames from a sibling symbol_files directory",
    )
    parser.add_argument(
        "--limit", type=int, default=32, help="maximum companion renames per run"
    )
    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit must be positive")

    files = sorted(args.generated_dir.glob("funcs_*.c"))
    files.extend(
        [
            args.generated_dir / "funcs.h",
            args.generated_dir / "recomp_overlays.inl",
        ]
    )
    generated_text = "\n".join(path.read_text() for path in files if path.exists())
    renames = dict(RENAMES)
    if args.companion_dir:
        discovered = companion_renames(args.companion_dir, generated_text)
        if len(discovered) > args.limit:
            parser.error(
                f"companion batch has {len(discovered)} matches; lower scope is required"
            )
        renames.update(discovered)
        names = list(renames.values())
        if len(names) != len(set(names)):
            parser.error("rename batch contains duplicate destination names")
        for old, new in discovered.items():
            if re.search(rf"\b{re.escape(new)}\b", generated_text) and not re.search(
                rf"\b{re.escape(old)}\b", generated_text
            ):
                parser.error(f"destination already exists in generated snapshot: {new}")
    counts = {old: 0 for old in renames}
    changed = []

    for path in files:
        text = path.read_text()
        updated = text
        for old, new in renames.items():
            hits = len(re.findall(rf"\b{re.escape(old)}\b", text))
            counts[old] += hits
            updated = re.sub(rf"\b{re.escape(old)}\b", new, updated)
        if updated != text:
            path.write_text(updated)
            changed.append(path)

    print(f"renamed {sum(counts.values())} references in {len(changed)} files")
    for old, count in counts.items():
        state = "updated" if count else "already synchronized"
        print(f"{old} -> {renames[old]}: {count} ({state})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
