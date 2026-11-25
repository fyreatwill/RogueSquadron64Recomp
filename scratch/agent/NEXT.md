# NEXT (s7916)
HYPOTHESIS-ID: g3-m6-island-b-nondet
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, docs/OWNER-REVIEW-QUEUE.md answers,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7915): H-clock REFUTED (D1 DET_CLOCK=2 == C1 DET_CLOCK=1 element 212/212; 14 other pairs 0/212). Clock thread closed.
ONE offline unit, no game run (6 arms already captured, p1_rand.txt.zst in scratch/s7912/m6{a,b}, s7913/m6c{1,2}, s7915/m6c{1,2}):
Hypotheses: H-rng (particle element draws from the shared rand stream; outcome = rand-stream state at the element's first frame),
H-race (host thread writes the element's vertex buffer), H-uninit (stale RAM read).
Discriminator: for each arm, take the rand-trace records (cols: idx, thread?, caller PC, value) in the VI/frame window of the element
(frames 6068..6282; map frame -> rand idx via the trace's frame/VI column, see tools/s7845_rng_tick_cmp.py) and compare the
value sequence and the caller-PC multiset pairwise. Plant control: flip one value in a copy, the compare must find it.
Outcomes: D1/C1 equal in the window AND every 0/212 pair differs -> H-rng (then find the seed/stream position that differs, at
its first divergence before the element); D1/C1 differ in the window or a 0/212 pair is equal -> H-rng refuted, H-race/H-uninit
(XTRACE_MEM write watch on the element vertex source, one run).
Budget: this thread gets at most this 1 more iteration, then the next ladder rung (owner queue / G1e).
