#!/usr/bin/env python3
"""Census guest-pointer handling in timer, virtual-address, and cache wrappers."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

FILES = (
    "lib/N64ModernRuntime/librecomp/src/ultra_translation.cpp",
    "lib/N64ModernRuntime/ultramodern/src/timer.cpp",
    "lib/N64ModernRuntime/ultramodern/src/misc_ultra.cpp",
)
TARGETS = {
    "osSetTimer", "osStopTimer", "osVirtualToPhysical", "osInvalDCache",
    "osWritebackDCache", "osWritebackDCacheAll", "osPiGetCmdQueue",
}
FUNCTION = re.compile(
    r"(?m)^\s*(?:extern \"C\" )?(?:static )?(?:[\w:<>*&]+\s+)+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\([^\n]*\)\s*\{"
)


def blocks(text: str):
    for match in FUNCTION.finditer(text):
        name = match.group("name")
        if name.removesuffix("_recomp") not in TARGETS:
            continue
        depth = 0
        end = match.end() - 1
        for pos in range(end, len(text)):
            if text[pos] == "{":
                depth += 1
            elif text[pos] == "}":
                depth -= 1
                if depth == 0:
                    yield name, text[match.start():pos + 1]
                    break


def classify(name: str, body: str) -> str:
    base = name.removesuffix("_recomp")
    if base in {"osInvalDCache", "osWritebackDCache", "osWritebackDCacheAll"}:
        return "intentional no-op"
    if base in {"osSetTimer", "osStopTimer"} and "TO_PTR" in body:
        return "translated/range-checked callee"
    if base == "osVirtualToPhysical":
        return "host integer translation, no guest dereference"
    if "MEM_" in body or "TO_PTR" in body or "PTR(" in body:
        return "translated/range-checked callee"
    if re.search(r"\*\s*\w+\s*=|\(\s*\w+\s*\*\s*\)\s*(?:ctx->|rdram)", body):
        return "raw-dereferenced"
    return "no pointer dereference observed"


def scan(root: pathlib.Path):
    rows = []
    found = set()
    for rel in FILES:
        path = root / rel
        if not path.exists():
            continue
        for name, body in blocks(path.read_text(errors="replace")):
            found.add(name.removesuffix("_recomp"))
            rows.append((rel, name, classify(name, body)))
    for target in sorted(TARGETS - found):
        rows.append(("<searched sources>", target, "not found"))
    return rows


def selftest() -> int:
    sample = """
    void osSetTimer_recomp(uint8_t* r, recomp_context* c) { auto p = TO_PTR(int, c->r4); *p = 1; }
    void osVirtualToPhysical(uint32_t p) { return p & 0x1fffffff; }
    void osWritebackDCache_recomp(uint8_t* r, recomp_context* c) { ; }
    void osPiGetCmdQueue(uint8_t* r, recomp_context* c) { int* p = (int*)c->r4; *p = 1; }
    """
    got = [(name, classify(name, body)) for name, body in blocks(sample)]
    expected = [
        ("osSetTimer_recomp", "translated/range-checked callee"),
        ("osVirtualToPhysical", "host integer translation, no guest dereference"),
        ("osWritebackDCache_recomp", "intentional no-op"),
        ("osPiGetCmdQueue", "raw-dereferenced"),
    ]
    print("positive-control rows:", len(got), "expected:", len(expected))
    print("synthetic classifications:", got)
    return 0 if got == expected else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    rows = scan(pathlib.Path(args.root))
    for rel, name, result in rows:
        print(f"{rel}:{name}: {result}")
    counts = {}
    for _, _, result in rows:
        counts[result] = counts.get(result, 0) + 1
    print("summary:", ", ".join(f"{key}={counts[key]}" for key in sorted(counts)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
