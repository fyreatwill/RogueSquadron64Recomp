# NEXT (s7917)
HYPOTHESIS-ID: g3-m6-island-b-nondet
First: CURRENT-TRUTH is 59.9 KB: if `wc -c < docs/CURRENT-TRUTH.md` > 60000 this is a MAINTENANCE iteration (migrate items 0/12
G3 det-sweep detail s7909-s7916 to PROJECT-OVERVIEW, renumber), no experiments. Then: `python3 tools/crash_reports.py --since 2026-11-13`,
docs/OWNER-REVIEW-QUEUE.md answers, new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7916): H-rng SELECTED by correlation (15/15 pairs: element exact <=> rand (site,value) stream equal through element start;
tools/s7916_rand_site_cmp.py). Missing: the causal line (iron rule 4).
ONE unit, cap 1 iteration, then CLOSE the thread as timing class and take the next ladder rung (owner queue items / G1e):
Causal confirm: build a per-site ordinal table from D1's own trace (scratch/s7915/m6c1/p1_rand.txt.zst; seed-before = previous
row's value in the filtered global stream; format "SITE ORD SEED" as tools/s7896_rand_replay.py writes; check how
ROGUESQ_RAND_REPLAY reads it in src/main/rt64_render_context.cpp and whether it is limited to pre-first-tick calls) and run 2 arms of the
s7915 recipe (scratch/s7915/run.sh, drop DET_CLOCK) with ROGUESQ_RAND_REPLAY=<table>. Control: element in both arms must be present and
the replay must visibly fire (log count > 0); a third arm with the table's 0x8006C0FC rows dropped is the negative control.
Outcomes: E1==E2 (and ==D1) -> H-rng causal, close. E1!=E2 with replay firing on the element's sites -> element state is not only its
rand values (re-open H-race via XTRACE_MEM write watch on the element vertex source). Replay cannot reach the element window -> close
as single-source timing class and move on.
