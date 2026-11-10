#!/usr/bin/env python3
"""s6782 census: every inter-thread send whose message may live on the sender's stack.

sendServiceMessage (0x80006F78) and osSendMesg (0x80033410) queue a POINTER, never a copy, so a message built on the
sender's stack is only safe if the receiver never reads it (doorbell) or the sender blocks until the receiver is done
(synchronous reply). s6781 found one that is neither (tickBackdropLoaderWorker 0x800B380C).

Disassembles main + every overlay of the retail ROM (rogue_squadron64/roguesquadron.yaml layout) with mips64-elf-objdump,
lists each send call, the instruction that last formed the message register before it, and the s6782 verdict.

usage: tools/audit_service_msg_stack.py [rom]   (default rogue_squadron.z64)
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SEGMENTS = [  # name, rom start, rom end, vram
    ("main", 0x1000, 0xA5D30, 0x80000400),
    ("mission", 0xA5D30, 0x10C2D0, 0x800A5130),
    ("menu", 0x10C2D0, 0x137580, 0x800A5130),
    ("cinematic", 0x137580, 0x144340, 0x800A5130),
]
SENDS = {0x80006F78: ("sendServiceMessage", "a2"), 0x80033410: ("osSendMesg", "a1")}

# s6782 classification of every stack-formed site (anything else that turns up stack-formed is NEW and unaudited).
VERDICT = {
    ("main", 0x8000582C): "doorbell: worker 0x80005570 discards the received pointer (only reads ring 0x801112B0)",
    ("main", 0x800058FC): "doorbell: same worker as 0x8000582C",
    ("menu", 0x800B380C): "LIVE, fixed s6781 (tools/fixup_menu_worker.py completion-id FIFO)",
    ("menu", 0x800C5880): "doorbell: tickSongAssetLoadWorker completion; receiver 0x800C3B4C tests v0 != 0 only",
    ("main", 0x80091E78): "dead: shutdownAudioEngine quit byte; only caller shutdownMusyXEngine has no jal/pointer",
}
# Heap messages carrying a pointer to the sender's stack (sp+16 in payload +0x10): sender blocks in a
# 0x80006F24 loop until that 0x80FF-tagged object comes back (server 0x80004540 replies into it).
SYNC_STACK_REPLY = {0x80004BE4, 0x80004D0C, 0x80004F28}

INSN = re.compile(r"\s*([0-9a-f]+):\s+[0-9a-f]+\s+(\S+)\s*(.*)")


def disasm(rom, name, start, end, vram, tmp):
    binp = Path(tmp) / f"{name}.bin"
    binp.write_bytes(rom[start:end])
    out = subprocess.run(["mips64-elf-objdump", "-D", "-b", "binary", "-m", "mips:4300", "-EB",
                          f"--adjust-vma={vram:#x}", str(binp)], capture_output=True, text=True, check=True).stdout
    return [(int(m.group(1), 16), m.group(2), m.group(3).strip()) for m in map(INSN.match, out.splitlines()) if m]


def msg_source(lines, i, reg):
    """Last instruction writing reg before the call (delay slot first, then backwards within the block)."""
    for addr, op, args in [lines[i + 1]] + [lines[j] for j in range(i - 1, max(i - 40, 0), -1)]:
        if op in ("jal", "jalr", "jr", "j") and addr != lines[i][0]:
            return f"(crossed {op} {addr:08x})"
        if args.split(",")[0] == reg and op not in ("sw", "sh", "sb", "beq", "bne", "beqz", "bnez"):
            return f"{addr:08x} {op} {args}"
    return "?"


def main():
    rom = Path(sys.argv[1] if len(sys.argv) > 1 else "rogue_squadron.z64").read_bytes()
    unaudited = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name, start, end, vram in SEGMENTS:
            lines = disasm(rom, name, start, end, vram, tmp)
            for i, (addr, op, args) in enumerate(lines):
                if op != "jal" or int(args, 16) not in SENDS:
                    continue
                fn, reg = SENDS[int(args, 16)]
                src = msg_source(lines, i, reg)
                stack = ",sp," in src
                verdict = VERDICT.get((name, addr))
                if verdict is None and addr in SYNC_STACK_REPLY:
                    verdict = "heap msg, stack reply object: sender blocks until it returns"
                if verdict is None and stack:
                    verdict = "UNAUDITED stack payload"
                    unaudited += 1
                if stack or verdict:
                    print(f"{name:9} {addr:08x} {fn:18} {src:32} {verdict}")
    print(f"unaudited stack-payload sends: {unaudited}")
    return 1 if unaudited else 0


if __name__ == "__main__":
    sys.exit(main())
