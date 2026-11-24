# NEXT (s7902)
HYPOTHESIS-ID: g3-island-b
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7901): m11 burst-replay crawl tail = 68 ODD frames from port 5639, each 4-40 differing white tris (not 1 tri); even frames
exact. Per-site ordinal skew refuted on both parities (ROGUESQ_RAND_REPLAY_SKEW arms scratch/s7901/m11skew{,a}: contiguous
N212/N213). Post-replay flame seeds equal retail's table in the crawl window on both sites.
Hypotheses for the odd-frame diff:
  H-draw: the odd frame draws a buffer whose values were written by a call the port and retail map to different frames (retail
          starts burst 2 on the 1FC parity; port on 174), i.e. the drawn buffer index (*(0x8013889C)&1) vs the written one differs.
  H-other: the differing tris are not the flame meshes (another object on odd frames), e.g. the first large white object.
  H-clip: same vertices, different clip output (tri counts differ 0-4) -> RSP side (unlikely, s7899 cxd4 bit-identical).
Discriminator (one port run + one retail run): dump the vertex arena 0x749000-0x74D000 and 0x8013889C at osSpTaskLoad for port
frames 5639..5650 (ROGUESQ_S7751_SNAP / S7751_EVERY) and retail (rs64_oracle --pc-ram-dump-also, scratch/s7900/run_retail.sh with the
VI window moved to the crawl tail, ~VI 10480-10700). For each odd frame: which mesh addresses differ (tools/s7900_tri_source.py), and
whether the differing port z values equal retail's z from the adjacent frame (H-draw) or match no retail frame (H-other/H-clip).
Recipe base: scratch/s7901/run_m11skew.sh without the SKEW env (needs scratch/s7901/<dir>/r1/oracle.log decompressed from
scratch/s7895/m11k/r1/oracle.log.zst, else p1only re-runs retail). Then m6 (0x31=5) with the burst arm.
