# NEXT (s7874)
HYPOTHESIS-ID: g3-cinematic-half-frame-phase
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7873): island A (port[3401:3560], 64 PRIM-FF tris, port ahead by 0.510 x speed) is NOT carried by dt (s7872), stall
parity (s7872), the timeSnapshotFiller stored value at retail values, or the post-load dt (s7873 arms A/B identical to pin).
This is iteration 3 on this slug with the lead moving each time. Budget rule 8: ONE more discriminating probe, then park it.
Hypotheses:
- H-phase: the element's animation reads a raw clock (mfc0 Count / osGetCount 0x8002BF00-class / VI stamp 0x80128ED8) at render
  time; the port samples at a different sub-frame phase -> constant half-frame lead.
- H-index: the element animates off a frame or VI counter that the port starts one VI earlier (the load-stall end), so a
  counter offset, not a time.
- H-retail-rdp: the retail RDP stream lags by half a frame (rdplog capture timing), i.e. a measurement artifact.
Unit (offline first, no build): census the readers of COUNT (mfc0 $9), of osGetCount callers and of 0x80128ED8 / VI counters
on the cinematic path (grep RecompiledFuncs for `mfc0`/`osGetCount`/`-0x7128(`). Then ONE retail oracle run (no game
instance, ~2 min) exec-tracing those PCs over the cinematic (RSECS 110, recipe as s7873: `env CPO=1 RSECS=110
EEP=scratch/s7872/w10/lvl.eep PP=19.5:start,31.5:start,43.5:start,67.5:start,79.5:start,91.5:start RDPBIN=/dev/null
XO="--exec-trace <pc>:8000000 ..." zsh tools/s7828_retail_cpo.sh scratch/s7874/r`), compared with the port's ROGUESQ_XTRACE
of the same PCs in a single det run. A value lead of ~1 VI on the port's clock read selects H-phase; equal clock reads with
an index offset select H-index; neither -> write the evidence table and park the slug (island A is timing-class and
pre-flight only; flight is retail-exact).
Tools: tools/s7873_snap_value.py (stored-value classes), tools/s7872_frame_clock.py, scratch/s7873/phase_a_p1.py pattern.
