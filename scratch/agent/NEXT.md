# NEXT (s7386)
HYPOTHESIS-ID: render-to-rdram-double-pass

s7385 added ROGUESQ_RENDER_TO_RAM=0 (opt-in) and ROGUESQ_RENDER_TO_RAM_TOG=<secs> (in-run A/B, [s4267] lines carry r2r=/ntog=).
Covered scenes look the same with the pass off; Gfx-thread per-task cost -2.5 ms mission / -1.2 ms front end (in-run toggle).
First: fold the s7385_r2r_off_levels soak verdict (SOAK-RESULTS.md; L1/L4/L12 300 s, pass = alive, 0 crash, knob line, no Gfx Thread
row in [s7384]).

Work unit: close H-partial and measure the busy-host payoff in ONE build (no rebuild needed) and ONE run per arm.
- Hypotheses: H-redundant-all (no scene needs the readback), H-partial (a scene not covered yet reads the rendered fb from RDRAM:
  mission intro/outro cutscenes, LEVEL DESCRIPTION, results/debrief, a level with a screen-effect), H-headroom (under host CPU load
  the 2.5 ms becomes fps: off blocks show more gfx tasks/s than on blocks), H-noheadroom (task rate equal under load too: the
  ucode run binds, nothing to offer beyond the frame-time margin).
- Coverage arm pair: env SECS=200 zsh scratch/s7385/run.zsh <name> '<env>' with an AP that reaches LEVEL DESCRIPTION, a mission
  intro cutscene, a mission end/results (forced-level route recipes in scratch/agent/g1_level_coverage_common.zsh, LEVEL=4 Gerrard V
  intro). Arms: unset vs ROGUESQ_RENDER_TO_RAM=0; contact sheet at the same keyed times (scratch/s7385 sheet code in the s7385
  PORTING-STATE entry). Any black / stale / garbled frame only in the off arm = H-partial: name the scene and write-watch its fb span.
- Busy-host arm: ROGUESQ_RENDER_TO_RAM_TOG=10 ROGUESQ_S4267=1 with a background load (e.g. 15 x `yes > /dev/null`, killed at end;
  s7277 recipe) on the same route; python3 scratch/s7385/tog.py (edit the path) -> sendDl/s by r2r in mission. Off > on by >= 2/s
  = H-headroom (add to OWNER-OPT-INS row); equal = H-noheadroom.
Do NOT change the default. Owner save read-only.
