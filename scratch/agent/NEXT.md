# NEXT (s7906)
HYPOTHESIS-ID: g3-island-b
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
Fold the three s7905 recurrence soaks (SOAK-RESULTS lines s7905_island_b_rep1..3; tag lines carry load= and crawl_nonexact=).
State (s7905): island B (m11 crawl-tail odd-frame residual) is ABSENT 3/3 on the rebuilt binary (C, C2, D: crawl 3728/3728 exact,
flight 2667/2667), against 106 non-exact frames in s7904 m11A on the same recipe/pins/save. Frame-counter parity (port = retail+29)
refuted as a cause (poke -29 changes nothing). Retail write watch: the addresses are shared per-frame bump-arena slots.
Hypotheses:
  H-race: host timing of the re-render task load vs the CPU's arena rebuild; residual appears only under some host loads.
  H-stale: s7900-s7904 ran a binary with some stale input s7424 does not check (code diff vs today is inert).
Outcomes:
  soaks 0/3 non-exact -> CLOSE island B: m11 pre-flight crawl + flight det-exact. Write it in CURRENT-TRUTH (move the island B
    thread to Closed work), then take the next item of CURRENT-TRUTH Next steps / the G-ladder (G6 items first if open).
  any soak non-exact -> H-race: keep that soak's p1.bin (re-run its recipe without the unlink), find the first non-exact frame,
    and compare its task-load VI vs the arena writer marks (rand trace rows around it) against an exact run.
  soaks not run yet -> do not wait; take the next Next-steps item and leave this for the fold.
