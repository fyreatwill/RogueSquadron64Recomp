# NEXT (s7905)
HYPOTHESIS-ID: g3-island-b
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
Also first: gate sweep is RED 7 since the scratch/s7435, s7439, s7442 sample_*.txt(.zst) captures vanished (dir mtime 2026-11-23
20:25; see s7904 entry). Find what deleted them (zst/prune tooling? grep tools for rm of sample_) and restore from git-ignored backup or
re-capture / re-point the S7433-S7441 + S7723 gate rows; a RED sweep must not stay RED.
State (s7904): rand-replay keying is NOT the island-B residual. Two-site skew arms: A (800541fc:2:16,80054174:2:-16) residual
unchanged (odd 3051 tris vs base 3033 over 106 frames), B (swapped) worse. scratch/s7904/blk_search.py: at port task s5683 the
port's RDRAM holds retail's correct 700140 block h269d96e6 at 0x74D710 (retail draws it at 0x724F70); port 0x724F70 holds
h1ce7ed51 = retail's frame-5542 value; retail's next-frame blocks are already in port RAM. Values right, arena placement/timing wrong.
Hypotheses:
  H-sched: same writer PCs and same allocation order, but the port's CPU writes the next frame's blocks into the arena before the odd
           re-render task loads (CPU/RSP interleave differs in the crawl tail).
  H-alloc-seq: the arena allocation pointer sequence differs (the port allocates the flame block for frame k at the address retail
           uses for frame k+1, e.g. one extra/missing allocation per frame pair).
Discriminator (ONE retail run + ONE port run, m11 recipe scratch/s7904/run_arms.sh arm C = no SKEW):
  retail: scratch/s7903/run_retail.sh + `--watch-write` on 0x724F70:0x724FB0, 0x727BC8:0x727C08, 0x749930:0x749970, 0x74D710:0x74D750
          (oracle prints PC + VI; positive control: a whole-arena 0x720000:0x758000 watch must fire within vi 10560-10580).
  port: an equivalent guest write log on the same ranges (check src/main for an existing write-watch env first; else add one gated
          env in the store path used by ROGUESQ_XTRACE_MEM) with writer PC + rs64_vi_n_g + the gfx task-load serial.
  Outcome: identical (PC, address) sequences but different position vs task loads -> H-sched; different address per writer call ->
           H-alloc-seq (then dump the arena alloc pointer per frame on both sides).
Budget: this slug has run s7899-s7904; every iteration discriminated, but if s7905 cannot split H-sched/H-alloc-seq, park island B
with the table in CURRENT-TRUTH (flight is already exact 2667/2667; this is a pre-flight crawl-tail cosmetic det residual).
