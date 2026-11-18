#!/usr/bin/env python3
"""s6831 G1e FPS60: integer constant-step (|K|>1) per-tick accumulators (tools/g1e_int_step_audit.py census, 41 sites).
Hand triage (s6831, PORTING-STATE): 40 sites are not game-time steps (heap/pointer/DL strides, JFIF/inflate parsers,
RSP ucode text, a tolower loop, the pause-menu layout cursor re-armed per call, audio sequence/stream offsets, and
tickTextureAnimSlots whose -0x100 drains carries of a dt-scaled float accumulator). One survives:
  advanceNpcOnCurvedPath 0x8006C124: rec +0x1E is a signed speed magnitude; each call adds 0x20, a positive value is
  clamped at 0xFF (ramp-up over 8 ticks), a negative one is zeroed once it crosses 0 (wind-down). The function runs
  once per mission tick (its +0x1C countdown at 0x8006C024 is already stepped by game time, s6821), so at
  ROGUESQ_FPS60 the ramp finishes in half the game time.
Fix: the 0x20 step becomes 0x20 * rs64_tick_step() (tools/fixup_fps60_ticks.py: number of 1/30 s game-time boundaries
this tick crossed, 1 outside FPS60 / outside a tick), so the ramp runs in 30 Hz ticks of game time.
ROGUESQ_FPS60_INTSTEP=0 restores the per-tick step (same build A/B). The load gets a ROGUESQ_TICK_TRACE hook
(rs64_tctr pc 0x8006C124, value = +0x1E before the step) for tools/g1e_int_step_rates.py.
Must run after fixup_fps60_ticks.py. Idempotent. Usage: fixup_fps60_int_step.py <RecompiledFuncs dir>"""
import pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import rs64_anchor  # s7558

base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "../N64Recomp/RecompiledFuncs")
TAG = "/* PATCH: s6831 fps60 int step */"
FN = "advanceNpcOnCurvedPath"
LOAD = "    // 0x8006C124: lhu         $v0, 0x1E($s1)\n"
LOAD_C = "    ctx->r2 = MEM_HU(ctx->r17, 0X1E);\n"
HOOK = "    rs64_tctr(rdram, 0x8006C124u, (uint32_t)(ctx->r17 + 0X1E), (int32_t)ctx->r2); " + TAG + "\n"
DECL = ("extern void rs64_tctr(uint8_t* rdram, uint32_t pc, uint32_t addr, int32_t v); extern int rs64_tick_step(void); "
        "extern char* getenv(const char*); static int rs64_int_step(void) { static int on = -1; if (on < 0) { "
        "const char* d = getenv(\"ROGUESQ_FPS60_INTSTEP\"); on = !(d && *d == '0'); } return on ? rs64_tick_step() : 1; } "
        + TAG + "\n")
done = 0
for p in sorted(base.glob("funcs_*.c")):
    s = p.read_text()
    i = s.find("RECOMP_FUNC void %s(" % FN)
    if i < 0:
        continue
    j = s.find("RECOMP_FUNC void", i + 10)
    j = len(s) if j < 0 else j
    body = s[i:j]
    sp = rs64_anchor.span(body, LOAD + LOAD_C)  # s7558: tolerate the s7484 load wrap
    if sp is None:
        sys.exit("s6831 fps60 int step: load 0x8006C124 not found in " + p.name)
    k = sp[1]
    if not body[k:].startswith(HOOK):
        body = body[:k] + HOOK + body[k:]
    # both copies of the bgez delay-slot addiu 0x8006C134 (taken and fall-through paths)
    a = body.find("// 0x8006C134: addiu       $v0, $v0, 0x20", k)
    b = body.find("// 0x8006C138:", k)
    if a < 0 or b < 0:
        sys.exit("s6831 fps60 int step: step 0x8006C134 not found")
    seg = body[a:b]
    seg, n = re.subn(r"^( +ctx->r2 = ADD32\(ctx->r2, 0X20)\);$", r"\1 * rs64_int_step()); " + TAG, seg, flags=re.M)
    n = seg.count("0X20 * rs64_int_step()); " + TAG)
    if n != 2:
        sys.exit(f"s6831 fps60 int step: expected 2 step copies at 0x8006C134, found {n}")
    body = body[:a] + seg + body[b:]
    s = s[:i] + body + s[j:]
    if DECL not in s:
        s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + DECL, 1)
    p.write_text(s)
    done += 1
if done != 1:
    sys.exit(f"s6831 fps60 int step: {FN} found in {done} files (want 1)")
print("[s6831] fps60 int step: advanceNpcOnCurvedPath +0x1E ramp stepped by game time, load traced")
