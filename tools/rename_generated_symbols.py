#!/usr/bin/env python3
"""Rename a checked, bounded batch of stale generated function symbols."""

from pathlib import Path
import argparse
import re
import sys


RENAMES = {
    "fake_func_800AA6CC": "npcPredictedRangeCheckPreamble",
    "fake_func_800AAADC": "playerSnowSpeederInitPreamble",
    "fake_func_8005C61C": "checkTrackedNpcProximityForCuePreamble",
    "fake_func_8005EE64": "steerOrientationTowardTargetPreamble",
    "fake_func_800613B8": "loadCharTextureSetPreamble",
    "fake_func_80069AEC": "collideSegmentAgainstObjectNodesPreamble",
    "fake_func_8006ACA4": "transformObjectColliderCenterPreamble",
    "fake_func_80082268": "cheatCodeConstantPreamble",
    "fake_func_800825C8": "rspbootTextPreamble",
    "fake_func_800AD378": "storeTrackedObjectAuxiliaryFields",
    "fake_func_800D2C98": "duplicateSymbolPrefixForNpcInitWithMotionParams",
    "fake_func_800D4EC4": "duplicateSymbolPrefixForNpcInitChildLinkedToParent",
    "fake_func_800DD2C4": "duplicateSymbolPrefixForNpcInitFullModel",
    "fake_func_800DFB8C": "duplicateSymbolPrefixForApplyCraftAnimAndDetailParams",
    "func_800E9AE0": "func_mission_overlay_800E9AE0",
    "fake_func_800E406C": "data_gap_800E406C",
    "fake_func_800E447C": "data_gap_800E447C",
    "fake_func_800E71C8": "data_gap_800E71C8",
    "fake_func_800E8A34": "duplicateSymbolPrefixForRunDestructionPhaseSequence",
    "fake_func_800E9AD8": "data_gap_800E9AD8",
    "fake_func_800EC10C": "data_gap_800EC10C",
    "fake_func_800ED148": "data_gap_800ED148",
    "fake_func_800EFD74": "data_gap_800EFD74",
    "fake_func_800EFDDC": "data_gap_800EFDDC",
    "func_800927B0": "interpolatePointTableSamplesToPackedWord",
    "func_80092A54": "interpolateLutSamplesToPackedWord",
    "func_80092CF0": "interpolateConstantSamplesToPackedWord",
    # These two generated entries decode data-gap bytes as invalid MIPS. Keep
    # the name mechanical: they are not callable game functions.
    "fake_func_800FBE14": "data_gap_800FBE14",
    "fake_func_800FEF04": "data_gap_800FEF04",
    "fake_func_80101CCC": "data_gap_80101CCC",
    "fake_func_80102A98": "data_gap_80102A98",
    "fake_func_8010357C": "data_gap_8010357C",
    "fake_func_80103D08": "data_gap_80103D08",
    "fake_func_80104208": "data_gap_80104208",
    "fake_func_801044D8": "data_gap_801044D8",
    "fake_func_80105B54": "data_gap_80105B54",
    "fake_func_8010619C": "data_gap_8010619C",
    "fake_func_80106BE8": "data_gap_80106BE8",
    "fake_func_8010721C": "data_gap_8010721C",
    "fake_func_80107EA4": "data_gap_80107EA4",
    "fake_func_80108B8C": "data_gap_80108B8C",
    "fake_func_80109428": "data_gap_80109428",
    "fake_func_80109618": "data_gap_80109618",
    # The companion map marks these defined fake entries immediately before
    # named functions; their short overlay records are data gaps, not callable
    # game routines.
    "fake_func_800027B8": "data_gap_800027B8",
    "fake_func_8000337C": "data_gap_8000337C",
    "fake_func_80003424": "data_gap_80003424",
    # The companion map marks these short fake records immediately before
    # named functions; keep their generated names explicit as data gaps.
    "fake_func_8000537C": "data_gap_8000537C",
    "fake_func_8000737C": "data_gap_8000737C",
    "fake_func_800074D8": "data_gap_800074D8",
    "fake_func_80007908": "data_gap_80007908",
    # This four-byte main-overlay record precedes the F3DEX text segment at
    # 0x80024A10 and is not a callable game function.
    "fake_func_80024A0C": "data_gap_80024A0C",
    # This eight-byte zlib record is an isolated store/halfword-load fragment
    # immediately before inflateReset; it is not a callable function body.
    "fake_func_80026B98": "data_gap_80026B98",
    # These eight-byte main-overlay records contain only an isolated
    # instruction fragment immediately before named routines.
    "fake_func_80079278": "data_gap_80079278",
    "fake_func_80079CD8": "data_gap_80079CD8",
    "fake_func_8007A0E8": "data_gap_8007A0E8",
    # The companion map places these short records immediately before named
    # functions; they are data gaps, not callable game routines.
    "fake_func_80064294": "data_gap_80064294",
    "fake_func_80064934": "data_gap_80064934",
    "fake_func_80065A5C": "data_gap_80065A5C",
    "fake_func_800663AC": "data_gap_800663AC",
    # These main-overlay entries are isolated instruction fragments with no
    # companion semantic symbol; make their non-callable status explicit.
    "fake_func_80005568": "data_gap_80005568",
    "fake_func_8000595C": "data_gap_8000595C",
    "fake_func_80006BFC": "data_gap_80006BFC",
    # This generated tail is the return sequence already belonging to
    # signalServiceWorkerStop; the false split does not define a callable.
    "static_3_80007064": "data_gap_80007064",
    "fake_func_8000751C": "data_gap_8000751C",
    # These short mission/menu-overlay fragments are contiguous preambles
    # before established callable bodies; the companion map and redefs agree
    # on the adjacent body names and exact boundaries.
    "fake_func_800B42BC": "playerXwingInitPreamble",
    "fake_func_800B47C4": "menuControllerInputPreamble",
    "fake_func_800B58B4": "playerAwingInitPreamble",
    "fake_func_800B75C4": "playerYwingInitPreamble",
    "fake_func_800B89F4": "playerVwingInitPreamble",
    # These short mission-overlay records are non-callable fragments between
    # established function boundaries.
    "fake_func_800BCC38": "data_gap_800BCC38",
    "fake_func_800BEBFC": "data_gap_800BEBFC",
    "fake_func_800BF498": "data_gap_800BF498",
    "fake_func_800BF784": "data_gap_800BF784",
    # These short main-overlay records precede named routines in the
    # companion map and are not callable function bodies.
    "fake_func_8001C3FC": "data_gap_8001C3FC",
    "fake_func_80023968": "data_gap_80023968",
    "fake_func_80024128": "data_gap_80024128",
    # These short main-overlay records are defined gaps immediately before
    # named routines; they are not callable function bodies.
    "fake_func_800186D8": "data_gap_800186D8",
    "fake_func_80019808": "data_gap_80019808",
    "fake_func_80024878": "data_gap_80024878",
    # These short defined records sit between named audio or mission
    # routines in the companion map and are not callable function bodies.
    "fake_func_80093E74": "data_gap_80093E74",
    "fake_func_80094348": "data_gap_80094348",
    "fake_func_8009711C": "data_gap_8009711C",
    "fake_func_800EC6EC": "data_gap_800EC6EC",
    "fake_func_800ECE04": "data_gap_800ECE04",
    # These short main-overlay records precede named routines in the
    # companion map and are not callable function bodies.
    "fake_func_80041EEC": "data_gap_80041EEC",
    "fake_func_800457CC": "data_gap_800457CC",
    # The companion map marks this defined 8-byte record as having no
    # accompanying real function; the generated body is invalid data.
    "fake_func_8003DF98": "data_gap_8003DF98",
    # These four-byte records contain only non-returning instruction
    # fragments immediately before named routines; they are not callable
    # function bodies.
    "fake_func_8006D8FC": "data_gap_8006D8FC",
    "fake_func_8006F4AC": "data_gap_8006F4AC",
    # These records have __builtin_trap() bodies from the fixup pass, confirming
    # the bytes decoded as invalid MIPS; they are not callable game routines.
    "fake_func_80099C4C": "data_gap_80099C4C",
    "fake_func_800AEC54": "data_gap_800AEC54",
    "fake_func_800AF6A8": "data_gap_800AF6A8",
    "fake_func_800C41AC": "data_gap_800C41AC",
    "fake_func_800C5898": "data_gap_800C5898",
    "fake_func_800C64A4": "data_gap_800C64A4",
    "fake_func_800C6968": "data_gap_800C6968",
    "fake_func_800C7DB4": "data_gap_800C7DB4",
    "fake_func_800CA26C": "data_gap_800CA26C",
    "fake_func_800CC038": "data_gap_800CC038",
    "fake_func_800CC3D4": "data_gap_800CC3D4",
    "fake_func_800CEF1C": "data_gap_800CEF1C",
    # This eight-byte mission-overlay record decodes as two invalid
    # negative-address loads immediately before initMission; it is not
    # callable game code.
    "fake_func_800FA248": "data_gap_800FA248",
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
