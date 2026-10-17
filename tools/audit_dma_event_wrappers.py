#!/usr/bin/env python3
"""Census guest-pointer handling in DMA and event host wrappers."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

FILES = (
    "lib/N64ModernRuntime/librecomp/src/pi.cpp",
    "lib/N64ModernRuntime/librecomp/src/dp.cpp",
    "lib/N64ModernRuntime/librecomp/src/ultra_translation.cpp",
    "lib/N64ModernRuntime/ultramodern/src/events.cpp",
)
TARGETS = (
    "osPiStartDma", "osEPiStartDma", "osDpSetNextBuffer",
    "osSetEventMesg", "osViSetEvent", "do_dma",
)
FUNCTION = re.compile(
    r"(?m)^(?:extern \"C\" )?(?:__attribute__\(\([^\n]+\)\) )?"
    r"(?:static )?[\w:<>*& ]+\s+(?P<name>(?:__)?[A-Za-z][A-Za-z0-9_]*)\s*\([^\n]*\)\s*\{"
)


def blocks(text: str):
    for match in FUNCTION.finditer(text):
        name = match.group("name")
        base_name = name.removesuffix("_recomp")
        if base_name not in TARGETS:
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
    base_name = name.removesuffix("_recomp")
    if base_name == "osDpSetNextBuffer" and "assert(false)" in body:
        return "intentional assert/no-op"
    if base_name == "osSetEventMesg" and "events_context" in body:
        return "guest address stored, no dereference"
    if "TO_PTR" in body or "MEM_" in body or "PTR(" in body:
        return "translated/range-checked callee"
    if re.search(r"\b(?:osSetEventMesg|osViSetEvent)\s*\(rdram\s*,", body):
        return "forwarded to runtime callee"
    if re.search(r"\*\s*\w+\s*=|\(\s*\w+\s*\*\s*\)\s*(?:ctx->|rdram)", body):
        return "raw-dereferenced"
    if "enqueue_external_message_src" in body or "save_read" in body or "save_write" in body:
        return "host callee, no guest pointer dereference"
    return "no pointer dereference observed"


def scan(root: pathlib.Path):
    rows = []
    for rel in FILES:
        path = root / rel
        if not path.exists():
            continue
        for name, body in blocks(path.read_text(errors="replace")):
            rows.append((rel, name, classify(name, body)))
    return rows


def selftest() -> int:
    sample = """
    void osPiStartDma(uint8_t* r, recomp_context* c) { auto p = MEM_W(0x10, c->r29); *p = 1; }
    void osDpSetNextBuffer(uint8_t* r, recomp_context* c) { assert(false); }
    void osSetEventMesg(uint8_t* r, int q, int m) { events_context.dp.mq = q; }
    void osEPiStartDma(uint8_t* r, recomp_context* c) { int* p = (int*)c->r4; *p = 1; }
    """
    got = [(name, classify(name, body)) for name, body in blocks(sample)]
    expected = [
        ("osPiStartDma", "translated/range-checked callee"),
        ("osDpSetNextBuffer", "intentional assert/no-op"),
        ("osSetEventMesg", "guest address stored, no dereference"),
        ("osEPiStartDma", "raw-dereferenced"),
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
