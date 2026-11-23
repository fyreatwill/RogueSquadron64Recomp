#!/usr/bin/env python3
"""s6751 G3: entry hook on rand_recomp (0x80003430) for ROGUESQ_RAND_TRACE (src/main/rt64_render_context.cpp).
Logs the caller's jal address and the seed before the call; off (one predicted branch) unless the trace file is
open. Recompiled calls do not set $ra, so every `rand_recomp(rdram, ctx);` call site first stores its jal address in
the host global rs64_rand_site (no guest state touched). Idempotent. Usage: fixup_rand_trace.py <RecompiledFuncs dir>"""
import pathlib, re, sys

base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "../N64Recomp/RecompiledFuncs")
TAG = "/* PATCH: s6751 rand trace */"
entry = "RECOMP_FUNC void rand_recomp(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n"
hook = ("    if (__builtin_expect(g_rs64_rand_trace, 0)) rs64_rand_trace(rs64_rand_site, U32(MEM_W(0X3470, S32(0X8000 << 16)))); "
        + TAG + "\n")
decl = ("extern volatile int g_rs64_rand_trace; extern uint32_t rs64_rand_site; extern void rs64_rand_trace(uint32_t ra, uint32_t seed); " + TAG + "\n")
hits = [p for p in sorted(base.glob("funcs_*.c")) if entry in p.read_text()]
if len(hits) != 1:
    sys.exit(f"s6751 rand trace: rand_recomp entry found in {len(hits)} files (expected 1)")
p = hits[0]
s = p.read_text()
if TAG not in s:
    s = s.replace(entry, entry + hook, 1)
    if decl not in s:
        s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + decl, 1)
    if s.count(TAG) != 2:
        sys.exit("s6751 rand trace: hook insertion failed")
    p.write_text(s)
    print(f"[s6751] rand trace hook added to {p.name}")
SITE_TAG = "/* PATCH: s6751 rand site */"
jal = re.compile(r"\s*// 0x([0-9A-F]{8}): jal\s+0x80003430\s*$")
sites = files = 0
for p in sorted(base.glob("funcs_*.c")):
    lines = p.read_text().splitlines(True)
    if not any(l.strip() == "rand_recomp(rdram, ctx);" for l in lines):
        continue
    out, changed = [], False
    for i, l in enumerate(lines):
        if l.strip() == "rand_recomp(rdram, ctx);" and (not out or SITE_TAG not in out[-1]):
            for j in range(i - 1, max(i - 40, 0), -1):
                m = jal.match(lines[j])
                if m:
                    break
            else:
                sys.exit(f"s6751 rand site: no jal comment before {p.name}:{i + 1}")
            ind = l[:len(l) - len(l.lstrip())]
            out.append(f"{ind}rs64_rand_site = 0x{m.group(1)}u; {SITE_TAG}\n")
            sites += 1
            changed = True
        out.append(l)
    s = "".join(out)
    if decl not in s:
        s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + decl, 1)
        changed = True
    if changed:
        p.write_text(s)
        files += 1
print(f"[s6751] rand site stores added: {sites} sites in {files} files")

# advanceNpcOnCurvedPath (0x8006BEC8): its rand at 0x8006C0FC is the first call to diverge (s6751). Log its entry
# ($a3 = NPC record whose +0x1C countdown gates the call) and the 0x8001DC34 gate result ($v0 at 0x8006C018; 0 skips
# the countdown decrement) into the same stream, keyed by those PCs.
NPC_TAG = "/* PATCH: s6751 npc path trace */"
fentry = "RECOMP_FUNC void advanceNpcOnCurvedPath(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n"
gate = "    // 0x8006C018: andi        $v0, $v0, 0xFF\n"
hits = [p for p in sorted(base.glob("funcs_*.c")) if fentry in p.read_text()]
if len(hits) != 1:
    sys.exit(f"s6751 npc trace: advanceNpcOnCurvedPath entry in {len(hits)} files")
p = hits[0]
s = p.read_text()
if NPC_TAG not in s:
    if s.count(gate) != 1:
        sys.exit(f"s6751 npc trace: gate anchor count {s.count(gate)}")
    s = s.replace(fentry, fentry + "    if (__builtin_expect(g_rs64_rand_trace, 0)) rs64_rand_trace(0x8006BEC8u, U32(ctx->r7)); "
                  + NPC_TAG + "\n", 1)
    s = s.replace(gate, "    if (__builtin_expect(g_rs64_rand_trace, 0)) rs64_rand_trace(0x8006C018u, U32(ctx->r2)); "
                  + NPC_TAG + "\n" + gate, 1)
    if decl not in s:
        s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + decl, 1)
    p.write_text(s)
    print(f"[s6751] npc path trace added to {p.name}")

# s6752: ROGUESQ_XTRACE_MEM marker rows (rs64_xtrace_mark dumps guest words per spec) right after every
# timeSnapshotFiller call returns (struct at caller sp+0x10; marker PC = jal+8: 0x800AF374 cinematicComputeDt,
# 0x800C6674 advanceWrappingPhaseAccumulator, 0x800FA730 runInMissionFrame = the in-flight frame) and at the
# 0x8001DC34 gate call in advanceNpcOnCurvedPath (0x8006C010: $a0 = reference object, sp+0x18 = NPC point).
# Mirrors oracle RS64_XTRACE_MEM.
MEM_TAG = "/* PATCH: s6752 xtrace mem */"
mdecl = ("extern void rs64_xtrace_mark(uint32_t pc, const uint8_t* rdram, const uint64_t* gpr); " + MEM_TAG + "\n")
def mark(pc):
    return (f"    if (__builtin_expect(g_rs64_rand_trace, 0)) rs64_xtrace_mark(0x{pc:08X}u, rdram, (const uint64_t*)&ctx->r0); "
            + MEM_TAG + "\n")
tick = re.compile(r"(    timeSnapshotFiller\(rdram, ctx\);\n        goto (after_\d+);\n    // 0x([0-9A-F]{8}): addiu       \$a0, \$sp, 0x10\n"
                  r"    ctx->r4 = ADD32\(ctx->r29, 0X10\);\n    \2:\n)(?!.*s6752 xtrace mem)")
gcall = "    // 0x8006C010: jal         0x8001DC34\n"
for p in sorted(base.glob("funcs_*.c")):
    s = p.read_text()
    t = len(tick.findall(s))
    g = s.count(gcall) if mark(0x8006C010) + gcall not in s else 0
    if not t and not g:
        continue
    s = tick.sub(lambda m: m.group(1) + mark(int(m.group(3), 16) + 4), s)
    if g:
        s = s.replace(gcall, mark(0x8006C010) + gcall)
    for d in (decl, mdecl):
        if d not in s:
            s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + d, 1)
    p.write_text(s)
    print(f"[s6752] xtrace mem hooks in {p.name}: tick {t} gate {g}")

# s6755: marker rows at runAiAudioStreamPlaybackLoop's two osAiSetNextBuffer calls (fixed 0x300-byte buffers), so the
# rand-trace file carries one row per AI buffer with the VI count: AI buffers per VI = the audio clock vs the VI clock.
# Mirrors oracle --exec-trace-also 0x8008EE08 / 0x8008EE84.
AI_TAG = "/* PATCH: s6755 ai buffer mark */"
for p in sorted(base.glob("funcs_*.c")):
    s = p.read_text()
    n = 0
    for pc in (0x8008EE08, 0x8008EE84):
        call = f"    // 0x{pc:08X}: jal         0x80029E80\n"
        m = mark(pc).replace(MEM_TAG, AI_TAG)
        if call in s and m + call not in s:
            s = s.replace(call, m + call); n += 1
    if not n:
        continue
    for d in (decl, mdecl):
        if d not in s:
            s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + d, 1)
    p.write_text(s)
    print(f"[s6755] ai buffer marks in {p.name}: {n}")

# s6781: menu-overlay image worker handshake (SELECT GAME slot panels). Marker rows at the worker's completion send
# (0x800B380C jal sendServiceMessage, $a2 = completion msg on the WORKER STACK, request id at +0x14), at the menu's
# request send (0x800B3FA0, $a2 = heap request, id at +0x5C) and at the menu poll's receive (0x800B4004 lbu 0x17($v1),
# $v1 = received msg). ROGUESQ_XTRACE_MEM=800B380C:6:0:8,800B3FA0:6:58:2,800B4004:3:0:8 dumps the words.
WK_TAG = "/* PATCH: s6781 menu worker mark */"
for p in sorted(base.glob("funcs_*.c")):
    s = p.read_text()
    n = 0
    for pc, ins in ((0x800B380C, "jal         0x80006F78"), (0x800B3FA0, "jal         0x80006F78"), (0x800B4004, "lbu         $v0, 0x17($v1)")):
        line = f"    // 0x{pc:08X}: {ins}\n"
        m = mark(pc).replace(MEM_TAG, WK_TAG)
        if s.count(line) == 1 and m + line not in s:
            s = s.replace(line, m + line); n += 1
    if not n:
        continue
    for d in (decl, mdecl):
        if d not in s:
            s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + d, 1)
    p.write_text(s)
    print(f"[s6781] menu worker marks in {p.name}: {n}")

# s6784: song-asset-load worker handshake (menuSubtype02Handler, menu overlay), the second consumer of the game worker
# queue (MEM_W 0x80138920) that pollServiceMessageByte (0x800B3FD8) also drains. Marks at the request send (0x800C3B38,
# $a2 = heap request), the worker's completion send (0x800C5880, $a2 = msg on the worker stack), the receive call
# (0x800C3B4C, $a0 = queue) and right after it returns (0x800C3B54, row $v0 = received msg or 0).
# ROGUESQ_XTRACE_MEM=800C3B38:6:0:8,800C5880:6:0:8,800C3B4C:4:0:1,800C3B54:2:0:8 dumps the words.
SG_TAG = "/* PATCH: s6784 song worker mark */"
for p in sorted(base.glob("funcs_*.c")):
    s = p.read_text()
    n = 0
    for pc, ins in ((0x800C3B38, "jal         0x80006F78"), (0x800C5880, "jal         0x80006F78"),
                    (0x800C3B4C, "jal         0x80006EC4"), (0x800C3B54, "beq         $v0, $zero, L_800C3BA4")):
        line = f"    // 0x{pc:08X}: {ins}\n"
        m = mark(pc).replace(MEM_TAG, SG_TAG)
        if s.count(line) == 1 and m + line not in s:
            s = s.replace(line, m + line); n += 1
    if not n:
        continue
    for d in (decl, mdecl):
        if d not in s:
            s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + d, 1)
    p.write_text(s)
    print(f"[s6784] song worker marks in {p.name}: {n}")

# s6816: enemy-bolt rows for the FPS60 hit-probability question (lvl14). The bolt update (audioCueDispatcherNpcHandler,
# mis-named; s5793) runs a 3-phase look-ahead hit test from L_8005CE5C (tick%3, segment vel*dt*3.5, hit if t<=0.34).
# rs64_bolt_mark (src/main/rt64_render_context.cpp) logs one row per bolt per tick within 40 units of the player
# (kind 0, tag b0170000) and one row per msg-5 hit send with the victim id (kind 1, tag b0170005). $s1 = bolt node,
# $s6 = bolt slot (id +0x16, flags +0x14), $a0 = victim id at the send.
BT_TAG = "/* PATCH: s6816 bolt mark */"
bdecl = ("extern void rs64_bolt_mark(const uint8_t* rdram, uint32_t node, uint32_t slot, uint32_t victim, int kind); "
         + BT_TAG + "\n")
def bmark(kind):
    return (f"    if (__builtin_expect(g_rs64_rand_trace, 0)) rs64_bolt_mark(rdram, (uint32_t)ctx->r17, (uint32_t)ctx->r22, "
            f"(uint32_t)(ctx->r4 & 0xFFFF), {kind}); " + BT_TAG + "\n")
for p in sorted(base.glob("funcs_*.c")):
    s = p.read_text()
    a = "L_8005CE5C:\n    // 0x8005CE5C: lw          $v1, -0x7764($v0)\n"
    b = "    // 0x8005D35C: jal         0x8003E8DC\n"
    if s.count(a) != 1 or s.count(b) != 1 or BT_TAG in s:
        continue
    s = s.replace(a, a.split("\n")[0] + "\n" + bmark(0) + a.split("\n", 1)[1]).replace(b, bmark(1) + b)
    for d in (decl, bdecl):
        if d not in s:
            s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + d, 1)
    p.write_text(s)
    print(f"[s6816] bolt marks in {p.name}: 2")

# s6816: player hp word (0x80137E7C = player record 0x80137DB0 + 0xCC) writer rows (rs64_hp_mark,
# src/main/rt64_render_context.cpp): PC, function and host backtrace of every hp drop > 5. First statement of the
# s5798 store hook (needs ROGUESQ_STORE_DIAG=1), ahead of the watch blocks that return early for this range.
HP_TAG = "/* PATCH: s6816 hpwatch */"
hp_anc = "void rs64_s5798_st(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w, const char* fn) {\n"
hp_add = ("    if (a == 0x80137E7Cu) { extern void rs64_hp_mark(const uint8_t* rdram, uint32_t pc, const char* fn); "
          "rs64_hp_mark(rdram, pc, fn); } " + HP_TAG + "\n")
for p in sorted(base.glob("funcs_*.c")):
    s = p.read_text()
    if s.count(hp_anc) != 1 or HP_TAG in s:
        continue
    p.write_text(s.replace(hp_anc, hp_anc + hp_add, 1))
    print(f"[s6816] hp watch in {p.name}")

# s6816b: guided-projectile rows (guidedEffectNpcHandler 0x8005F9A4, the source of the 50-hp player hits): one row per
# missile per tick at the swept hit test (0x80060034 jal findNpcInScaledBoxRegionExcludingPair; $s1 = missile data,
# $s3 = slot) and one row when the test returns a victim (0x8006003C, $v0). rs64_guided_mark in rt64_render_context.cpp.
GD_TAG = "/* PATCH: s6816 guided mark */"
gdecl = ("extern void rs64_guided_mark(const uint8_t* rdram, uint32_t m, uint32_t slot, uint32_t victim, int kind); "
         + GD_TAG + "\n")
for p in sorted(base.glob("funcs_*.c")):
    s = p.read_text()
    a = "    // 0x80060034: jal         0x8005EA9C\n"
    b = "    // 0x8006003C: andi        $s0, $v0, 0xFFFF\n"
    if s.count(a) != 1 or s.count(b) != 1 or GD_TAG in s:
        continue
    mk = lambda k, v: (f"    if (__builtin_expect(g_rs64_rand_trace, 0)) rs64_guided_mark(rdram, (uint32_t)ctx->r17, (uint32_t)ctx->r19, "
                       f"{v}, {k}); " + GD_TAG + "\n")
    s = s.replace(a, mk(0, "0xFFFFu") + a).replace(b, mk(1, "(uint32_t)(ctx->r2 & 0xFFFF)") + b)
    for d in (decl, gdecl):
        if d not in s:
            s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + d, 1)
    p.write_text(s)
    print(f"[s6816] guided marks in {p.name}: 2")

# s6820: NPC (re)creation rows for the FPS60 20-tick AI cadence (lvl14). The rand sites 0x800D860C (wingman voice-line
# deadline seed) and 0x800F28F4 (initActorMotionParams) fire together every 20 ticks; both run inside
# npcInitFromTemplate (0x800D2B5C), which is only reached through a callback that createAndInitObject (0x800EC588)
# stores. rs64_bt_mark (src/main/rt64_render_context.cpp) logs one row per entry: tag b7000000, entry PC, $a0, host
# backtrace (recompiled function names = the guest call chain that gates the spawn).
BTM_TAG = "/* PATCH: s6820 spawn bt mark */"
btdecl = "extern void rs64_bt_mark(uint32_t pc, uint32_t a0); " + BTM_TAG + "\n"
for name, pc in (("npcInitFromTemplate", 0x800D2B5C), ("createAndInitObject", 0x800EC588)):
    fe = f"RECOMP_FUNC void {name}(uint8_t* rdram, recomp_context* ctx) {{\n    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n"
    for p in sorted(base.glob("funcs_*.c")):
        s = p.read_text()
        if fe not in s or f"rs64_bt_mark(0x{pc:08X}u" in s:
            continue
        s = s.replace(fe, fe + f"    if (__builtin_expect(g_rs64_rand_trace, 0)) rs64_bt_mark(0x{pc:08X}u, (uint32_t)ctx->r4); "
                      + BTM_TAG + "\n", 1)
        for d in (decl, btdecl):
            if d not in s:
                s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + d, 1)
        p.write_text(s)
        print(f"[s6820] spawn bt mark {name} in {p.name}")

# s7850: one marker row per SI-thread pass at processPolledControllerData entry (0x800027C0; siServiceThread calls it
# at 0x80002F24, once per pass). Rumble effect lifetimes count these passes (slot +0x80 += getViModePeriod, +0x6B
# cleared at 0x80002934), and retail runs exactly 1 pass per VI (s7849 r3: 2.001 per mission tick). Rows carry the
# update_screen # so passes/VI and passes/tick fall out offline (tools/s7850_si_cadence.py).
# ROGUESQ_XTRACE_MEM=800027C0:0:80110588:2 adds port-0 slot +0x68..+0x6F; ...:801105A0:1 adds +0x80.
SI_TAG = "/* PATCH: s7850 si pass mark */"
sife = "RECOMP_FUNC void processPolledControllerData(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n"
sih = [p for p in sorted(base.glob("funcs_*.c")) if sife in p.read_text()]
if len(sih) != 1:
    sys.exit(f"s7850 si pass mark: processPolledControllerData entry in {len(sih)} files")
s = sih[0].read_text()
if SI_TAG not in s:
    s = s.replace(sife, sife + "    if (__builtin_expect(g_rs64_rand_trace, 0)) rs64_xtrace_mark(0x800027C0u, rdram, (const uint64_t*)&ctx->r0); "
                  + SI_TAG + "\n", 1)
    for d in (decl, mdecl):
        if d not in s:
            s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + d, 1)
    sih[0].write_text(s)
    print(f"[s7850] si pass mark in {sih[0].name}")


# s7851: one marker row at entry of each 3D-sound node writer, so a port run gives the same call order as the oracle's
# --watch-write on sound node 0x80137FC4 (+0x08 flags, +0x40 fade timer). Retail s7851 r6: play3DSoundEvent (game thread)
# queues (flags |=2), dispatchPrioritizedSoundQueue + update3DAudioFrame (musyxSynthFrame, viRetraceHandlerThread, one per
# VI) dispatch and ramp +0x40 by 0.3 per VI to 1.2, factor5RemoveListNode unlinks. Rows carry the update_screen # (VI).
# ROGUESQ_XTRACE_MEM=<pc>:0:80137FCC:1,<pc>:0:80138004:1 adds the node words at each mark.
SND_TAG = "/* PATCH: s7851 snd node mark */"
SND = {"play3DSoundEvent": 0x800989D8, "factor5RemoveListNode": 0x80098DE0,
       "dispatchPrioritizedSoundQueue": 0x80099720, "update3DAudioFrame": 0x800998E8}
for name, pc in SND.items():
    hdr = f"RECOMP_FUNC void {name}(uint8_t* rdram, recomp_context* ctx) {{\n    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n"
    fs = [p for p in sorted(base.glob("funcs_*.c")) if hdr in p.read_text()]
    if len(fs) != 1:
        sys.exit(f"s7851 snd node mark: {name} entry in {len(fs)} files")
    s = fs[0].read_text()
    if f"rs64_xtrace_mark(0x{pc:08X}u, rdram, (const uint64_t*)&ctx->r0); {SND_TAG}" in s:
        continue
    s = s.replace(hdr, hdr + f"    if (__builtin_expect(g_rs64_rand_trace, 0)) rs64_xtrace_mark(0x{pc:08X}u, rdram, (const uint64_t*)&ctx->r0); "
                  + SND_TAG + "\n", 1)
    for d in (decl, mdecl):
        if d not in s:
            s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + d, 1)
    fs[0].write_text(s)
    print(f"[s7851] snd node mark {name} in {fs[0].name}")
