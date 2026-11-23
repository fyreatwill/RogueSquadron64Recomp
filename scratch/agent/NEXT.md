# NEXT (s7850)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Crash/owner report outranks this.
Why: s7849 0x31=7: rand/hp/pose exact under pins, but the port starts 2 extra rumble effects (49 vs 47). Rumble lifetime =
processPolledControllerData (0x800027C0) calls x getViModePeriod; retail calls it exactly once per VI (2.001 per mission tick).
Unit: measure the port's SI-pass cadence and close or fix it, in ONE build.
 1. Instrument: count calls of processPolledControllerData per VI and per mission tick in the port (fixup probe at 0x800027C0, or
    ROGUESQ_XTRACE_MEM=800027C0:0:80110588:1 if xtrace reaches that pc -- check first; positive control: count > 0 at boot).
    Also log the slot +0x80/+0x6B at each pass for port 0 (cheap ring, dump at exit).
 2. Run p1 again (scratch/s7849/pins.txt, tools/s7849_det_pair.sh logic) with the probe.
Hypotheses: H-si-clock (port passes/tick != 2.000 or jittered around mission ticks -> pin the SI service to the VI, like VI_STAMP /
RETAIL_SNAP, opt-in env, then rerun 0x31=7 expecting rumble events 47 = 47) vs H-other (port passes exactly 1/VI aligned -> the
difference is in the effect header/duration or the call order inside the VI; compare slot +0x80 per pass vs a retail
--watch-write 0x110520+0x80 log).
After that: continue the sweep with `zsh tools/s7849_det_pair.sh 8 scratch/s785x` (0x31=8), background it (~28 min).
