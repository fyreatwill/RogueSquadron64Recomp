# NEXT (s7845)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Crash/owner report outranks this. CURRENT-TRUTH is 59.3 KB: if Step 0 trips (>60000) this is maintenance.
Why: s7844 (0x31=5) render exact; with retail's dt replayed (p4) the player record is bit-identical for 1321 ticks, then the
port takes its 2nd 50-hp hit 143 ticks after the 1st vs retail 265 (all 4 port arms 141-143) -> fork is in the shooter.
Hypotheses:
  H-rng: the enemy fire decision draws a different RNG value (port setRngSeed host override / extra draws / seed from count).
  H-ai-clock: shooter cadence keys off a frame/VI counter, not dt (port VI:game-frame ratio != oracle CPO model).
  H-bolt-geom: same bolt both sides, retail misses by a hair (float collision), port hits.
Discriminator, ONE pair (same save scratch/s7844/lvl.eep, p4 recipe incl. the 19 ROGUESQ_S7844_DT_AT overrides from
scratch/s7844/p4/run.log `[dt7844]` lines): retail r4 adds `--watch-write 0x137E7C:0x137E80` (hp, physical) with PC attribution
+ a --pc-ram-dump of the RNG state word(s) (find the seed/state address read by setRngSeed 0x80003460, funcs_1.c) at 0x80043918;
port: same RNG words via ROGUESQ_PLAYER_DUMP-style ramdump. Outcomes: RNG word forks before tick ~1320 -> H-rng (then name the
extra/missing draw); RNG equal but hit writer PC/caller object differs in timing -> H-ai-clock; same shooter+bolt spawn tick,
hit only in port -> H-bolt-geom. Positive control: the hp watch must fire at the shared 1st hit (retail row 1181/port 1179).
Score with tools/s7844_hp_events.py + scratch/s7844/al2.py/ev.py.
