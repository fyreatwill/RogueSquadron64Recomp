# NEXT (s7849)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Crash/owner report outranks this. CURRENT-TRUTH compacted to ~26 KB in s7848.
Why (s7848 was maintenance, unit carried over unchanged): s7847 closed 0x31=6 under seed + dt pins (port == retail 1876 ticks, record 0 diffs, p2 control forks). Next level: 0x31=7.
Recipe (copy scratch/s7847 commands, PORTING-STATE s7847):
 1. `python3 tools/g3_eep_patch.py scratch/s7832/lvl.eep scratch/s7849/lvl.eep --set 0x31=7`
 2. retail r1: the s7847 r1 command with EEP/outdir s7848. RS64_ORACLE_FPR MUST be the list 0,4,6,14,20 (=1 prints only f1).
    seed = first `pc=800fa730` [xtrace] row's m=80003470 value; dt list = `python3 scratch/s7844/snap.py r1/oracle.log`
    "all non-88 ticks" minus ticks 0,1 (89).
 3. port: copy scratch/s7847/run_port.sh to s7848, set seed + DT_AT list (comma tick:hex), run (~11 min, background it; it exceeds
    the 600 s foreground cap).
 4. score: tools/s7845_rng_tick_cmp.py r1/oracle.log p1_rand.txt (and p2); scratch/s7847/al2.py with its retail path edited.
Hypotheses: H-exact (all scores equal) vs H-new-fork (name first differing tick + caller). Positive control: p2 must fork.
Engineering option if time: fold steps 1-4 into one driver tool (tools/s7849_det_pair.sh) and use it for this pair.
