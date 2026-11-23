# NEXT (s7846)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Crash/owner report outranks this. CURRENT-TRUTH is 59.7 KB: if Step 0 trips (>60000) this is maintenance.
Why: s7845 closed 0x31=5: with retail's dt sequence replayed (S7844_DT_AT) and rngSeed poked at mission tick 0, port == retail
(rand stream 2451 ticks, hits, 460-w record 2262 rows). Next level of the sweep: 0x31=6.
Recipe (both pins from the start):
 1. save: python3 tools/g3_eep_patch.py scratch/s7832/lvl.eep scratch/s7846/lvl.eep --set 0x31=6
 2. retail r1: s7845 r4 command (PORTING-STATE s7845) with EEP=scratch/s7846/lvl.eep, keep RS64_ORACLE_FPR=1 + watches
    0x800FA738,0x800FA7D0 (for the dt list, scratch/s7844/snap.py) as s7844 r3 did. Read seed at tick 0 from the first
    `pc=800fa730` row (m=80003470:...), dt overrides from snap.py (non-88 ticks >1).
 3. port p1: s7845 p7 command with the new save, that seed in ROGUESQ_XTRACE_POKE and the new DT_AT list; p2 = same with no
    seed poke and no DT_AT (control that the instrument sees a fork).
 4. score: tools/s7845_rng_tick_cmp.py r1/oracle.log p1_rand.txt; scratch/s7845/al2.py-style record align; render census
    tools/s7827_tri_yshift_census.py --controls if an RDP bin is kept.
Hypotheses: H-exact (pins suffice: all three scores equal) vs H-new-fork (a third oracle-timing input or a real port defect;
name the first differing tick + caller). Positive control: p2 must fork (seed differs at tick 0).
