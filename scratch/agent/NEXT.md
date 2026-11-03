# NEXT: G1e FPS60 residual - per-tick FLOAT quanta class audit (integer tick-timer class closed s6825)
HYPOTHESIS-ID: g3-fps60-float-quanta

Context: FPS60 (owner's setting) runs the mission sim at dt=1/60. Closed classes: rotate-helper K*dt quanta (s6817),
despawn grace (s6820), integer tick timers (s6821-s6825, FIX 7, UNFIX 8). The remaining idiom that would make FPS60 differ
from 30 Hz is a FLOAT field advanced by a constant per tick with no dt multiply (lwc1 field -> add.s/sub.s/mul.s with a
rodata/literal constant -> swc1 same field, inside a mission-tick handler), e.g. per-tick velocity damping (v *= 0.95) or
fade/scale ramps.
Hypotheses: H-none (every per-tick float update in mission handlers is dt-scaled; FPS60 float state matches 30 Hz),
H-some (a set of constant-step float accumulators exists; each runs 2x per game s at FPS60).
Step 1 (offline, one tool): extend the tools/g3_tick_counter_audit.py scan shape to float fields: in RecompiledFuncs,
load-op-store on the same base+offset where the op's other operand does not derive from the handler dt argument or the
dt global captured at 0x800FA90C. Classify each site: dt-scaled / constant step / multiplicative damping. Positive
control: the scan must list 0x800FEF10's K*dt sites as dt-scaled and the s6821 advanceNpcOnCurvedPath float path.
Step 2 (one build): trace hook on the constant-step sites (same ROGUESQ_TICK_TRACE format, new pc tag), lvl1 + lvl14
FPS60 vs a30 400 s (lvl16/17 need >=400 s). 2x ex/game-s with a value change per execution => H-some for that site.
Fix candidate: scale the constant by dt*30 under ROGUESQ_FPS60 (pow for damping), env opt-out, same discipline as
tools/fixup_fps60_scrape.py.
