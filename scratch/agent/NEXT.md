# NEXT (s7913)
HYPOTHESIS-ID: g3-m6-island-b-nondet
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, docs/OWNER-REVIEW-QUEUE.md answers,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7912): m6 island B = ONE particle element (RDP opcode 0x0D shade+z untextured, combine FFFFFF/FFFE793C, othermodes
082CC000504A50) drawn port 6071..6282 / retail 5539..5750, and it is port RUN-TO-RUN nondeterministic: same-config same-binary
arms scratch/s7912/m6a vs m6b differ on it 0/212 (symdiff 25463), the rest of the island is 212/212 exact
(tools/s7912_elem_cross.py, scratch/s7912/ab_rest.py).
Hypotheses:
- H-clock: the element (or its emitter) consumes osGetCount / osGetTime, which are host wall clock in the port
  (lib/N64ModernRuntime/ultramodern/src/timer.cpp osGetCount = time_now()) but cycle-deterministic under mupen.
- H-race: a host thread (RSP task / audio / RDP async) races the game thread on the element's vertex or state buffer.
- H-uninit: the element reads uninitialised / stale guest memory whose content depends on host timing earlier on.
Discriminator, ONE build, 3 arms (one game run at a time, sequential, same p1only recipe as s7912):
1. Passive (default off): ROGUESQ_S7913_CLOCKLOG=1 in osGetCount_recomp / osGetTime_recomp (lib/N64ModernRuntime/librecomp/src/
   ultra_translation.cpp) logs caller RA (ctx->r31) + port VI per call into a ring dumped at exit (no per-call stderr).
2. Lever (default off): ROGUESQ_DET_CLOCK=1 makes osGetCount/osGetTime a function of the VI count (rs64_vi_n_g * 781250 cycles
   per VI at 46.875 MHz, plus a fixed per-call increment), so they are identical run to run.
Arms: C1, C2 = DET_CLOCK=1 twice; the s7912 A/B pair is the control that differs. Score with
`python3 tools/s7912_elem_cross.py 635A40/f0/s3/w1 FFFFFFFFFE793C C1=... C2=... A=scratch/s7912/m6a/p1.bin B=scratch/s7912/m6b/p1.bin`.
Outcomes: C1==C2 exact on the element -> H-clock (then the CLOCKLOG callers active in the element's VI window name the consumer;
next: is it a retail-match fix worth an opt-in, e.g. pair with VI_STAMP determinism). C1!=C2 -> H-clock refuted, H-race/H-uninit:
next a write watch (XTRACE_MEM) on the element's vertex source. If DET_CLOCK breaks boot or audio, record it and use CLOCKLOG alone.
Any lib/ edit: `./submodule-patches/export.sh` + commit the refreshed patches in the same session.
Keep bins zstd'd (zstd -T2, iron rule 0). Budget: 2 iterations, then record the table and take the next ladder rung
(owner queue / G1e).
