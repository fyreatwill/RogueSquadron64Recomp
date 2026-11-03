# NEXT: audit the whole boot -> flight route for other non-preemptible stretches (run-token class audit)
HYPOTHESIS-ID: g3-preempt-audit

State (s6808): the title AI gaps were a low-priority guest thread computing 70-90 ms with no OS call; ultramodern only
delivers host messages / swaps priority inside OS calls. Fixed at the 5 glyph-mesh functions (rs64_preempt_point,
tools/fixup_preempt_point.py). The same class may exist elsewhere (hangar entry, mission load, in-flight): s6807 port
fix arm also had 3-VI gaps @1958/2508 on the lvl3 route, and s6808 runs saw a 3-VI gap @1404 (512-wide entry, q 597 =
not an underrun).
Hypotheses: H-none (no other gap > 2 VI on the route: retail parity, close); H-class (more gaps, token held by a
low-priority OSId across the gap: add those functions to fixup_preempt_point.py after naming them with a host sample);
H-other (gap with a high-priority holder or idle token = a different mechanism, e.g. a host block in an OS call).
Discriminator, ONE build (current): an 85 s lvl3 boot -> flight run with
  env SAVE_FROM=scratch/s6807/lvl3.eep SECS=85 CAP0=9999 AP=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,50:start \
   XE="ROGUESQ_DEBUG_WRITE=80003470:1:320:0 ROGUESQ_VI_WALL=$PWD/scratch/s6809/a.vi.txt ROGUESQ_AI_TRACE=$PWD/scratch/s6809/a.ai.txt" \
   zsh tools/g3_port_capture.sh scratch/s6809/a
  then G3_GAP_MIN=3 python3 tools/g3_title_gap.py scratch/s6809/a. Same-run control: ROGUESQ_PREEMPT_POINT=0 arm must
  show the 737/973 gaps again. For each remaining gap with a low-pri holder: `/usr/bin/sample PID 8 1` across it (see
  PORTING-STATE s6808) to name the busy function. Fold the s6808_preempt_lvl1_fps60 soak verdict first.
If H-none: close; take the next ladder rung (G3 in-flight frame diffs vs retail on a level not yet matched).
