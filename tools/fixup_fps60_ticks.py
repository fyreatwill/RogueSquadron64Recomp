#!/usr/bin/env python3
"""s6821 G3 FPS60: per-object integer TICK timers beyond the s6820 despawn grace (tools/g3_tick_counter_audit.py table).
Two parts, one pass:
 (1) TRACE: every non-stack counter site the audit finds (load -> addiu +-1 -> store same field -> test) gets a hook
     after its load: rs64_tctr(pc, field address, loaded value). Off unless ROGUESQ_TICK_TRACE=<file> is set; records
     are 16 bytes {pc, addr, value, tick#}; one {0, game time bits, dt bits, tick#} record per mission tick (captured
     where runInMissionFrame advances game time, 0x800FA90C) so offline durations are in game seconds.
 (2) FIX: whitelisted in-mission timers (FIX below, read by hand: countdowns tested >0 / <=0 / ==0 that end an
     effect, a death sequence or a state; count-ups tested < K) step by rs64_tick_step() instead of 1. Under
     ROGUESQ_FPS60 the step is the number of 1/30 s game-time boundaries this tick crossed (dt 1/60 -> 0,1,0,1), so the
     timer runs in 30 Hz ticks of game time; retail (no FPS60) and ROGUESQ_FPS60_TICKS=0 keep step 1.
     s6822: the step only holds INSIDE a mission tick (from the dt capture to runInMissionFrame's return,
     0x800FADE4); everywhere else it is 1. The FIX count-ups at 0x800AF5A0 / 0x800B41B8 also run in the pre-mission
     intro, outside any tick (s6822 trace: tick 0), and used to read the LAST tick's step - 0 on every other FPS60
     tick, so a later mission load could freeze those `< 7` stage gates. With the trace on, each step read outside a
     tick logs {1, step it would have used before s6822, 0, tick#}.
Idempotent. Usage: fixup_fps60_ticks.py <RecompiledFuncs dir>"""
import pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from g3_tick_counter_audit import scan

base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "../N64Recomp/RecompiledFuncs")
TAG = "/* PATCH: s6821 fps60 ticks */"
FIX = {
    0x8007CD50: "npcTexturedEffectUpdateWithSlotChain +0xA0 lifetime",
    0x8007030C: "multiEventTemplateNpcHandler +0x6 lifetime",
    0x8006C024: "advanceNpcOnCurvedPath +0x1C countdown",
    0x800B41B8: "accumulateShipThrottleCharge 0x800CC860 count-up <7",
    0x800F8708: "executeActorType4Effect +0x92 count-up <20",
    0x80044938: "cutsceneActorNpcHandler +0x108 count-up <5",
    0x800AF5A0: "cinematicStageAdvancer +0x938 count-up <7",
    0x800FB4F8: "tickMissionTransitionAndTeardown countdown",
}
# s6822 lvl13 a30/off/fix: these decrement once per EVENT, not per tick (executions per game s equal at 30 Hz and FPS60:
# 800DAB64 0.54/0.54, one step per ~1.02 s in both; 800E32CC 0.21/0.25; 800E1E28 three steps 1/30 s apart in both), so
# stepping them by game time skipped every other event and doubled them (800DAB64 1 s -> 2 s per step). Reverted to 1.
# s6823 static read of the 7 sites no census level executed: 800C96B8 (npcTurretUpdate +0x88) and 800806AC
# (attachedAudioVisualEmitterNpcHandler +0xB4) decrement only when a float interval timer (+0x84 / +0xB0, minus the
# handler's dt argument *a2, re-armed to a random interval) expires - burst counts of the 800DAB64 kind. Reverted to 1.
# The other five decrement on every call, behind state/button/flag gates only, and keep the step (single-source).
# s6824: 800B5350 / 800BC778 (+0x15C) are gated by config +0x1E = C-down (0x0004), which the game's button word
# 0x80130B88 carries for ONE tick per press (edge), so they run once per press at both rates (lvl2 a30 2/2, FPS60 2/2);
# the game-time step was 0 on every other FPS60 tick and dropped those presses. Reverted to 1.
UNFIX = {0x800DAB64, 0x800E32CC, 0x800E1E28, 0x800C96B8, 0x800806AC, 0x800B5350, 0x800BC778}
DECL = ("extern void rs64_tctr(uint8_t* rdram, uint32_t pc, uint32_t addr, int32_t v); extern int rs64_tick_step(void); "
        + TAG + "\n")
DEF = ("extern char* getenv(const char*); "
       "static FILE* rs64_tt_f; static int rs64_tt_on = -1; static uint32_t rs64_tt_tick; static int rs64_tk_on = -1; "
       "static float rs64_tk_acc; static int rs64_tk_step = 1; static int rs64_tk_in; "
       "static void rs64_tt_rec(uint32_t a, uint32_t b, uint32_t c) { uint32_t r[4] = {a, b, c, rs64_tt_tick}; fwrite(r, 4, 4, rs64_tt_f); } "
       "void rs64_tctr(uint8_t* rdram, uint32_t pc, uint32_t addr, int32_t v) { (void)rdram; "
       "if (rs64_tt_on < 0) { const char* p = getenv(\"ROGUESQ_TICK_TRACE\"); rs64_tt_f = (p && *p) ? fopen(p, \"wb\") : 0; rs64_tt_on = rs64_tt_f != 0; } "
       "if (rs64_tt_on) rs64_tt_rec(pc, addr, (uint32_t)v); } "
       "int rs64_tick_step(void) { if (rs64_tk_in) return rs64_tk_step; if (rs64_tt_on > 0) rs64_tt_rec(1, (uint32_t)rs64_tk_step, 0); return 1; } "
       "static void rs64_tick_end(void) { rs64_tk_in = 0; } "
       "static void rs64_tick_begin(uint8_t* rdram, float dt, float t) { "
       "if (rs64_tk_on < 0) { const char* f = getenv(\"ROGUESQ_FPS60\"); const char* d = getenv(\"ROGUESQ_FPS60_TICKS\"); "
       "rs64_tk_on = f && *f && *f != '0' && !(d && *d == '0'); } "
       "if (rs64_tk_on && dt > 0.0f && dt < (1.0f / 30.0f)) { rs64_tk_acc += dt * 30.0f; rs64_tk_step = 0; "
       "while (rs64_tk_acc >= 0.999f) { rs64_tk_acc -= 1.0f; rs64_tk_step++; } } else { rs64_tk_acc = 0.0f; rs64_tk_step = 1; } "
       "rs64_tk_in = 1; rs64_tt_tick++; if (rs64_tt_on < 0) rs64_tctr(0, 0xFFFFFFFFu, 0, 0); "
       "if (rs64_tt_on) { union { float f; uint32_t u; } a, b; a.f = t; b.f = dt; rs64_tt_rec(0, a.u, b.u); "
       "rs64_tt_rec(2, MEM_HU(0, (gpr)(int32_t)0x80130B88), ((uint32_t)MEM_HU(0x1E, (gpr)(int32_t)0x8010BE18) << 16) "
       "| MEM_HU(0x1A, (gpr)(int32_t)0x8010BE18)); fflush(rs64_tt_f); } } "
       + TAG + "\n")
DT_SITE = "    // 0x800FA90C: swc1        $f2, 0xBA4($a0)\n"
DT_HOOK = "    rs64_tick_begin(rdram, ctx->f20.fl, ctx->f2.fl); " + TAG + "\n"
# s6824: pre-s6824 hook (no rdram); each tick now also records row pc=2: player-0 held buttons (0x80130B88) and the
# player-0 config halfwords +0x1E (hi) / +0x1A (lo) of 0x8010BE18, so a button-gated site can be tied to its button.
DT_HOOK_OLD = "    rs64_tick_begin(ctx->f20.fl, ctx->f2.fl); " + TAG + "\n"
END_SITE = "    // 0x800FADE4: jr          $ra\n"
END_HOOK = "    rs64_tick_end(); " + TAG + "\n"
DEF_OLD = re.compile(r"^extern char\* getenv\(const char\*\); static FILE\* rs64_tt_f;.*\n", re.M)
REG = {('$zero', 0), ('$at', 1), ('$v0', 2), ('$v1', 3)}
REG = {n: i for i, n in enumerate("zero at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 t8 t9 k0 k1 gp sp fp ra".split())}

rows = [r for r in scan(str(base)) if r[6] != 'stack' and not r[9]]
want = {(r[0], r[1]): r for r in rows}
missing = set(FIX) - {r[1] for r in rows}
if missing:
    sys.exit("s6821 fps60 ticks: whitelisted sites not found by the audit: " + " ".join("%08X" % a for a in sorted(missing)))
traced, fixed, dt_done = set(), set(), 0
COMMENT = re.compile(r"    // 0x([0-9A-F]{8}): (\S+)\s+(.*)$")
for p in sorted(base.glob("funcs_*.c")):
    lines = p.read_text().splitlines(True)
    changed = False
    fn = None
    out = []
    i = 0
    while i < len(lines):
        l = lines[i]
        out.append(l)
        m0 = re.match(r'RECOMP_FUNC void (\w+)\(', l)
        if m0: fn = m0.group(1)
        m = COMMENT.match(l)
        if m and fn and (fn, int(m.group(1), 16)) in want and i + 1 < len(lines):
            pc = int(m.group(1), 16); r = want[(fn, pc)]
            c = lines[i + 1]; out.append(c); i += 1
            cm = re.match(r"    ctx->r(\d+) = MEM_\w+\(ctx->r(\d+), (-?0X[0-9A-F]+)\);", c)
            if not cm:
                sys.exit(f"s6821 fps60 ticks: unexpected load line {p.name}:{i + 1}: {c.strip()}")
            hook = f"    rs64_tctr(rdram, 0x{pc:08X}u, (uint32_t)(ctx->r{cm.group(2)} + {cm.group(3)}), (int32_t)ctx->r{cm.group(1)}); {TAG}\n"
            if i + 1 >= len(lines) or TAG not in lines[i + 1]:
                out.append(hook); changed = True
            traced.add(pc)
            if pc in FIX:
                # the +-1 step: next addiu comment's C line within 5 instructions
                for j in range(i + 1, min(len(lines), i + 24)):
                    mj = COMMENT.match(lines[j])
                    if mj and mj.group(2) in ('addiu', 'addi') and re.search(r', (-?0x1)$', mj.group(3).strip()):
                        cj = lines[j + 1]
                        if TAG not in cj:
                            new = re.sub(r"ADD32\((ctx->r\d+), (-?)0X1\)", r"ADD32(\1, \2rs64_tick_step())", cj, count=1)
                            if new == cj:
                                sys.exit(f"s6821 fps60 ticks: unexpected step line {p.name}:{j + 2}: {cj.strip()}")
                            lines[j + 1] = new.rstrip("\n") + " " + TAG + "\n"; changed = True
                        fixed.add(pc)
                        break
            elif pc in UNFIX:
                for j in range(i + 1, min(len(lines), i + 24)):
                    mj = COMMENT.match(lines[j])
                    if mj and mj.group(2) in ('addiu', 'addi') and re.search(r', (-?0x1)$', mj.group(3).strip()):
                        cj = lines[j + 1]
                        if TAG in cj and "rs64_tick_step()" in cj:
                            lines[j + 1] = cj.replace("rs64_tick_step()", "0X1").replace(" " + TAG, ""); changed = True
                        break
        i += 1
    s = "".join(out)
    if DT_SITE in s:
        s = s.replace(DT_HOOK_OLD, "")
        if DT_HOOK not in s:
            s = s.replace(DT_SITE, DT_HOOK + DT_SITE, 1); changed = True
        if END_SITE not in s:
            sys.exit("s6822 fps60 ticks: runInMissionFrame return 0x800FADE4 not in the dt-site file")
        if END_HOOK not in s:
            s = s.replace(END_SITE, END_HOOK + END_SITE, 1); changed = True
        if DEF not in s:
            s = DEF_OLD.sub("", s)  # s6822: replace a pre-s6822 definition line in an already-patched file
            s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + DEF, 1); changed = True
        dt_done += 1
    elif changed and DECL not in s:
        s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + DECL, 1)
    if changed:
        p.write_text(s)
if dt_done != 1:
    sys.exit(f"s6821 fps60 ticks: dt site found in {dt_done} files (want 1)")
if set(FIX) - fixed:
    sys.exit("s6821 fps60 ticks: step not patched at " + " ".join("%08X" % a for a in sorted(set(FIX) - fixed)))
print(f"[s6821] fps60 ticks: {len(traced)} counter sites traced, {len(fixed)} timers stepped by game time")
