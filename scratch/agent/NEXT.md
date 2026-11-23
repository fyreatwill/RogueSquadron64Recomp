# NEXT (s7862)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. A crash or owner report outranks this.
State: main sweep 0x31=0..15 complete; bonus 16 H-exact (s7860); bonus 17 H-audio-clock FORK t1124 (s7861, scratch/s7861/v17).
Unit: bonus 18 (Battle of Hoth, snowspeeder) det pair, the last mission in the sweep. Two d-pad RIGHTs inside the SELECT LEVEL
window (retail: between PP 19.5 and the 31.5 commit Start; port: between AP 31.5 and the 43.5 commit Start, s7861 cursor trace):
  `env BASE_EEP=scratch/s7859/base_bonus.eep PP_OVR=19.5:start,27.5:dright,29:dright,31.5:start,43.5:start,55.5:start AP_OVR=6:start,11:start,11.5:w1024,19.5:start,31.5:start,39.5:right,41:right,43.5:start,67.5:start,79.5:start zsh tools/s7849_det_pair.sh 16 scratch/s7862/v18`
Gate the retail mission before the port arms run (they take ~12 min): as soon as scratch/s7862/v18/pins.txt exists, SEED must not
be ebdad279 (race) or 8b1200fb (trench); otherwise kill the pair (SIGKILL) and probe the cursor like s7861/probe (xtrace
800C6674:0:800CDAC0:1, expect byte C1 0x10->0x12). If the press 1.5 s apart registers only once, space them 2 s apart.
Score: `python3 tools/s7856_det_verdict.py scratch/s7862/v18/score.txt --tag bonus18`. H-exact closes 18 (s6773 saw no song
switch). FORK fork=audio-clock = known class. fork=unclassified -> name the writer with tools/s7858_store_seq_cmp.py.
Controls: p2 forks t0, flip caught t100, all presses before each side's first tick.
After 18: the det sweep is complete for 0..18. Write the per-mission verdict table into CURRENT-TRUTH item 12 and take the next
ladder rung (ITERATION.md 3c).
