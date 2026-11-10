#!/usr/bin/env python3
"""s6784: static reachability of the game-worker-queue (MEM_W 0x80138920) consumers/producers from each menu screen.

The menu dispatcher menuOverlayInit (jump table at 0x800A75C0, screen halfword) runs one handler per screen. Two code
paths drain the same queue: pollServiceMessageByte 0x800B3FD8 (menu image worker completions, id byte +0x17) and the
recv at 0x800C3B4C inside menuSubtype02Handler 0x800C30C8 (screen 10, song-asset-load worker doorbell). A completion
can only be eaten by the wrong consumer if the image worker can have a request pending (0x800B3F24 sends it) while
screen 10 runs. This walks the jal call graph of main + the menu overlay (retail ROM, mips64-elf-objdump via
tools/audit_service_msg_stack.py) from each screen handler and prints which of the targets it can reach, plus every
jalr (indirect call) in the reachable set, which a static walk cannot follow.
Function extent = from its entry to the next jal-target entry in the same segment (no reliance on jr ra).
Control: menuControllerInput 0x800B47D0 must reach both 0x800B3F24 and 0x800B3FD8 (it does, s6781 sites).
usage: menu_worker_reach.py [ROM]   exits 1 if the control fails.
"""
import bisect, pathlib, re, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from audit_service_msg_stack import SEGMENTS, disasm

ROM = sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64"
TARGETS = {0x800B3F24: "image request send", 0x800B3FD8: "image completion poll",
           0x800B3650: "image worker body", 0x800B3EB8: "initBackdropLoaderWorker",
           0x800C57CC: "initSongAssetLoadWorker", 0x800C5834: "song worker body", 0x80006EC4: "tryRecvServiceMessage", 0x80006F78: "sendServiceMessage"}
SCREENS = [  # jump table 0x800A75C0 cases (menuOverlayInit 0x800C5A7C), handler called from each case
    (0, 0x800C6854, "runHangarMenuFromOverlay"), (1, 0x800C5D9C, "case1"), (2, 0x800B47D0, "menuControllerInput"),
    (3, 0x800BF830, "runMenuRandomBackdropScreen"), (4, 0x800C5EF8, "runResultsTextScreenLoop"),
    (6, 0x800C6900, "case6"), (8, 0x800C131C, "runMenuShipSelectScreen"), (9, 0x800C28F0, "runMenuModelViewerScreen"),
    (10, 0x800C30C8, "menuSubtype02Handler")]


def load():
    rom = pathlib.Path(ROM).read_bytes()
    code = {}  # seg -> sorted list of (addr, mnem, ops)
    with tempfile.TemporaryDirectory() as tmp:
        for name, start, end, vram in SEGMENTS:
            if name not in ("main", "menu"):
                continue
            code[name] = disasm(rom, name, start, end, vram, tmp)
    return code


def main():
    code = load()
    addrs = {s: [r[0] for r in rows] for s, rows in code.items()}
    entries = {s: set() for s in code}
    for s, rows in code.items():
        for a, mn, ops in rows:
            if mn == "jal":
                t = int(ops.split()[0], 16)
                entries["menu" if t >= 0x800A5130 else "main"].add(t)
    for _, e, _ in SCREENS:
        entries["menu"].add(e)
    for t in TARGETS:
        entries["menu" if t >= 0x800A5130 else "main"].add(t)
    starts = {s: sorted(v) for s, v in entries.items()}

    def body(f):
        s = "menu" if f >= 0x800A5130 else "main"
        st = starts[s]
        k = bisect.bisect_right(st, f)
        end = st[k] if k < len(st) else 1 << 40
        i = bisect.bisect_left(addrs[s], f)
        while i < len(code[s]) and code[s][i][0] < end:
            yield code[s][i]
            i += 1

    def reach(root):
        seen, stack, jalr = {root}, [root], []
        while stack:
            f = stack.pop()
            for a, mn, ops in body(f):
                if mn == "jal":
                    t = int(ops.split()[0], 16)
                    if t not in seen:
                        seen.add(t); stack.append(t)
                elif mn == "jalr":
                    jalr.append((f, a))
        return seen, jalr

    ok = True
    for case, e, name in SCREENS:
        seen, jalr = reach(e)
        hit = [f"{TARGETS[t]} 0x{t:08X}" for t in sorted(TARGETS) if t in seen]
        ovl_jalr = [f"0x{a:08X}" for f, a in jalr if f >= 0x800A5130]
        print(f"screen {case:2d} {name:30s} funcs={len(seen):4d} reaches: {', '.join(hit) or '-'}")
        print(f"          jalr sites in overlay funcs: {len(ovl_jalr)} {' '.join(ovl_jalr[:12])}")
        if case == 2 and not (0x800B3F24 in seen and 0x800B3FD8 in seen):
            ok = False
    print("CONTROL", "PASS" if ok else "FAIL", "(menuControllerInput reaches 0x800B3F24 + 0x800B3FD8)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
