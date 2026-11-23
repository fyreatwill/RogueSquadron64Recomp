# NEXT (s7861)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. A crash or owner report outranks this.
State: main sweep 0x31=0..15 complete; bonus 16 (race) H-exact (s7860, scratch/s7860/v16s, PP_OVR/AP_OVR in s7849_det_pair.sh).
Unit: bonus 17 det pair. 0x31 clamps to 16, so on SELECT LEVEL add one d-pad RIGHT before the Start that commits the level
(retail key `dright` in PP, port key `right` in AP; s6772 used AP ...,23:w512,25:right,27:start and PRESS ...,41:dright,44:start).
First find which press in the det_pair timebase commits the level. Read s7860/v16s/r1/oracle.log [press] lines and
p1/run.log [autopilot] fire lines against the VI width/phase. The pick is probably the 43.5 s Start (PP 43.5 = retail 49.25 s).
Insert the right press ~2 s before it on both sides, keep the extra port 67.5 Start, and use base_bonus.eep (+0x39=0x60; check
that bonus 17 is unlocked by it, otherwise set the next bit):
  `env BASE_EEP=scratch/s7859/base_bonus.eep PP_OVR=19.5:start,31.5:start,41.5:dright,43.5:start AP_OVR=6:start,11:start,11.5:w1024,19.5:start,31.5:start,41.5:right,43.5:start,67.5:start zsh tools/s7849_det_pair.sh 16 scratch/s7861/v17`
Check retail picked a different mission (seed != ebdad279) before scoring. Outcomes: H-exact closes 17; a fork with
equal press ticks gets its writer named with tools/s7858_store_seq_cmp.py. Controls: p2 fork t0, flip caught t100, press ticks
pre-race or equal. Then bonus 18 (two RIGHTs, X-wing craft-select Start, s6772).
