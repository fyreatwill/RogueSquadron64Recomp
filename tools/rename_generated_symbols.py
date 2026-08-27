#!/usr/bin/env python3
"""Rename a checked, bounded batch of stale generated function symbols."""

from pathlib import Path
import argparse
import re
import sys


RENAMES = {
    "fake_func_80082268": "cheatCodeConstantPreamble",
    "fake_func_800825C8": "rspbootTextPreamble",
    "fake_func_800AD378": "storeTrackedObjectAuxiliaryFields",
    "fake_func_800D2C98": "duplicateSymbolPrefixForNpcInitWithMotionParams",
    "fake_func_800D4EC4": "duplicateSymbolPrefixForNpcInitChildLinkedToParent",
    "fake_func_800DD2C4": "duplicateSymbolPrefixForNpcInitFullModel",
    "fake_func_800DFB8C": "duplicateSymbolPrefixForApplyCraftAnimAndDetailParams",
    "func_800E9AE0": "func_mission_overlay_800E9AE0",
    "func_800927B0": "interpolatePointTableSamplesToPackedWord",
    "func_80092A54": "interpolateLutSamplesToPackedWord",
    "func_80092CF0": "interpolateConstantSamplesToPackedWord",
}


def in_region(address: str, start: int | None, end: int | None) -> bool:
    value = int(address, 16)
    return (start is None or value >= start) and (end is None or value < end)


def companion_renames(
    symbol_dir: Path, generated_text: str, start: int | None, end: int | None
) -> tuple[dict[str, str], list[tuple[str, str, str]]]:
    """Return only semantic companion names for placeholders in the snapshot."""
    result = {}
    decisions = []
    generated_placeholders = set(
        re.findall(r"\b(?:func|fake_func)_([0-9A-Fa-f]{8})\b", generated_text)
    )
    generated_names = set(
        re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", generated_text)
    )
    for symbol_file in sorted(symbol_dir.glob("*.txt")):
        for line in symbol_file.read_text().splitlines():
            match = re.match(
                r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*0x([0-9A-Fa-f]{8});(?:\s*//.*)?$",
                line,
            )
            if not match:
                continue
            name, address = match.groups()
            if not in_region(address, start, end):
                continue
            if name.startswith(("D_", "fake_func_", "func_")):
                decisions.append((address.upper(), name, "ambiguous-or-fake"))
                continue
            old_names = [
                f"func_{address.upper()}",
                f"fake_func_{address.upper()}",
            ]
            old = next(
                (candidate for candidate in old_names if candidate in generated_names),
                old_names[0],
            )
            if address.upper() in generated_placeholders:
                previous = result.get(old)
                if previous is not None and previous != name:
                    result.pop(old)
                    decisions.append(
                        (address.upper(), name, f"ambiguous-conflicting-with-{previous}")
                    )
                elif old not in result:
                    result[old] = name
                    decisions.append((address.upper(), name, "selected"))
                else:
                    decisions.append((address.upper(), name, "ambiguous-duplicate"))
            else:
                decisions.append((address.upper(), name, "already-synchronized"))
    return result, decisions


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
    parser.add_argument(
        "--require-rename",
        action="store_true",
        help="fail if the bounded selection changes no generated references",
    )
    parser.add_argument("--start-address", type=lambda value: int(value, 0))
    parser.add_argument("--end-address", type=lambda value: int(value, 0))
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
    if args.start_address is not None and args.end_address is not None:
        if args.end_address <= args.start_address:
            parser.error("--end-address must be greater than --start-address")
    renames = {
        old: new
        for old, new in RENAMES.items()
        if in_region(old.rsplit("_", 1)[-1], args.start_address, args.end_address)
    }
    decisions = []
    if args.companion_dir:
        discovered, decisions = companion_renames(
            args.companion_dir, generated_text, args.start_address, args.end_address
        )
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
    for address, name, decision in decisions:
        print(f"candidate 0x{address} {name}: {decision}")
    for old, count in counts.items():
        state = "updated" if count else "already synchronized"
        print(f"{old} -> {renames[old]}: {count} ({state})")
    if args.require_rename and not changed:
        print("error: bounded sweep selected no generated references", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
