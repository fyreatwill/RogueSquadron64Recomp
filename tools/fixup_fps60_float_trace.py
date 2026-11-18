#!/usr/bin/env python3
"""s6826 G3 FPS60: trace hooks on the per-tick FLOAT load-op-store sites (tools/g3_float_quanta_audit.py) whose other
operand is not dt-derived (STEP / DAMP / step-* / mul-*), plus the dt-scaled controls (updateNpcEventTimer +0x10,
the s6817 resolver accumulators). After each site's lwc1 the hook calls the s6821 recorder rs64_tctr(pc, field
address, raw float bits), so the records land in the same ROGUESQ_TICK_TRACE file as the integer timers, keyed by the
same per-tick {0, game time, dt, tick#} rows. Off unless ROGUESQ_TICK_TRACE is set. Diagnostic only: no value change.
Loads sitting in a branch delay slot are hooked on the fall-through copy only. Idempotent; run after fixup_fps60_ticks.py.
Usage: fixup_fps60_float_trace.py <RecompiledFuncs dir>"""
import pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import rs64_anchor  # s7558
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from g3_float_quanta_audit import scan, CONTROLS

base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "../N64Recomp/RecompiledFuncs")
TAG = "/* PATCH: s6826 fps60 float trace */"
DECL = "extern void rs64_tctr(uint8_t* rdram, uint32_t pc, uint32_t addr, int32_t v); " + TAG + "\n"
rows = scan(str(base))
want = {(r[0], r[1]) for r in rows if r[6] and (r[5] != 'ok' or (r[0], r[1]) in CONTROLS
        or (r[0] == 'stepObjectOrientationTowardTarget' and 0x800FF47C <= r[1] < 0x800FF98C))}
COMMENT = re.compile(r"    // 0x([0-9A-F]{8}): lwc1 ")
LOAD = re.compile(r"    " + rs64_anchor.WRAP_OPEN + r"ctx->f(\d+)\.u32l = MEM_W\(ctx->r(\d+), (-?0X[0-9A-F]+)\);")  # s7558: s7484 wrap
hooked = set()
for p in sorted(base.glob("funcs_*.c")):
    lines = p.read_text().splitlines(True)
    out, fn, changed, i = [], None, False, 0
    while i < len(lines):
        l = lines[i]; out.append(l)
        m0 = re.match(r'RECOMP_FUNC void (\w+)\(', l)
        if m0: fn = m0.group(1)
        m = COMMENT.match(l)
        if m and fn and (fn, int(m.group(1), 16)) in want:
            pc = int(m.group(1), 16)
            c = lines[i + 1]; cm = LOAD.match(c)
            if not cm:
                sys.exit(f"s6826 float trace: unexpected load line {p.name}:{i + 2}: {c.strip()}")
            out.append(c); i += 1
            if not (i + 1 < len(lines) and TAG in lines[i + 1]):
                out.append(f"    rs64_tctr(rdram, 0x{pc:08X}u, (uint32_t)(ctx->r{cm.group(2)} + {cm.group(3)}), "
                           f"(int32_t)ctx->f{cm.group(1)}.u32l); {TAG}\n")
                changed = True
            hooked.add(pc)
        i += 1
    if changed:
        s = "".join(out)
        if DECL not in s:
            s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + DECL, 1)
        p.write_text(s)
# s6828: the a1 step dt passed to updatePlayerVehicleByControlMode at each of its 5 call sites (addr = call-site pc),
# recorded after the mfc1 so it shows the value actually passed (fixup_fps60_float_quanta.py may rewrite it).
CALLERS = ("8004EF38", "8004F160", "8004F990", "8004FA54", "8004FB24")
ctag = "/* PATCH: s6828 vehicle-step caller trace */"
ncall = 0
for p in sorted(base.glob("funcs_*.c")):
    s = p.read_text(); ch = False
    for c in CALLERS:
        com = f"    // 0x{c}: mfc1        $a1, $f20\n"
        if com not in s:
            continue
        i = s.index(com) + len(com); j = s.index("\n", i) + 1
        ncall += 1
        if ctag in s[j:s.index("\n", j) + 1]:
            continue
        s = s[:j] + f"    rs64_tctr(rdram, 0x{c}u, 0x{c}u, (int32_t)ctx->r5); {ctag}\n" + s[j:]; ch = True
    if ch:
        if DECL not in s:
            s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + DECL, 1)
        p.write_text(s)
# s6829: hangar tilt trace, one row set per hangarVehicleDisplayNpcHandler call, after the 0x800C6D40 dt load:
# pc 0x800C6D40 = +0x8 tilt, 0x800C6D44 = +0xC tilt, 0x800C6D48 = the frame dt (*s3), 0x800C6D4C = stick x of the slot.
htag = "/* PATCH: s6829 hangar tilt trace */"
hcom = "    // 0x800C6D40: lwc1        $f2, 0x0($s3)\n"
hn = 0
for p in sorted(base.glob("funcs_*.c")):
    s = p.read_text()
    if hcom not in s:
        continue
    hn += 1
    i = s.index(hcom) + len(hcom); j = s.index("\n", i) + 1
    if htag in s[j:s.index("\n", j) + 1]:
        continue
    s = s[:j] + ("    rs64_tctr(rdram, 0x800C6D40u, (uint32_t)(ctx->r18 + 8), MEM_W(0x8, ctx->r18)); "
                 "rs64_tctr(rdram, 0x800C6D44u, (uint32_t)(ctx->r18 + 0xC), MEM_W(0xC, ctx->r18)); "
                 "rs64_tctr(rdram, 0x800C6D48u, (uint32_t)ctx->r19, (int32_t)ctx->f2.u32l); "
                 "rs64_tctr(rdram, 0x800C6D4Cu, 0u, MEM_W(0, (gpr)(int32_t)0x8010BDD8 + (MEM_W(4, ctx->r18) << 3))); " + htag + "\n") + s[j:]
    if DECL not in s:
        s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + DECL, 1)
    p.write_text(s)
if hn != 1:
    sys.exit(f"s6829 hangar tilt trace: hook site found in {hn} files")
if ncall != len(CALLERS):
    sys.exit(f"s6828 caller trace: {ncall}/{len(CALLERS)} call sites found")
miss = {pc for _, pc in want} - hooked
if len(miss) > len(want) // 10:
    sys.exit(f"s6826 float trace: {len(miss)}/{len(want)} sites not hooked")
print(f"[s6826] fps60 float trace: {len(hooked)}/{len(want)} float sites hooked ({len(miss)} delay-slot/other misses)")
