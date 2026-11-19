# NEXT (s7635)
HYPOTHESIS-ID: bridge-walker-fusion

G6a/G6b/G6c still wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports on any of them, take that first.
Otherwise this is CURRENT-TRUTH item 24, implementation step.

s7634 selected H-walk (scratch/s7634/RESULT.txt): a decode-only walk costs ~3.0 ms/s at L1 dd4 16:9 FPS60, so folding
rs64_spike_scan + rs64_region_scan into one walk saves ~6 ms/s (~0.1 ms/VI). The gain is small: keep the change mechanical.

Plan (one build):
- Split each walker into prologue (the per-call setup before its `for (a...)` loop, incl. the swap/radar/pause gates and the
  diag file flushes) and a per-command body `step(a, w0, w1, op) -> len`. Both walkers already use the same op-size rules
  (16 B texrect 0x24/0x25, tri len from op bits, `a + 32 > hi` break, 8 B else). Region must see spike's edits for the same
  command, so the fused loop runs spike's body then region's body on each command, in submit order (same bytes as 2 passes).
  floor_scan and g5b_frame stay where they are (after region).
- ROGUESQ_S7634_FUSE: default 1 (fused), 0 = old two walks, tog = old on odd GLUE_TOG=3 seconds (same-run A/B).
- If the spike or region early-return gates differ (spike: !(on||cull); region: !on), the fused loop calls each body only if
  its gate passed; if neither passed, no walk.
Proof, same run (FUSE=tog + GLUE_TIME=1): (1) byte-identical RDP output: hash every submit range after the region step in
both arms over the same frames is impossible (A/B in different seconds), so instead run ROGUESQ_S7634_FUSE=chk: fused walk on a
copy, old walks on the original, memcmp per submit, count mismatches (must be 0; positive control: chk with a 1-byte injected
edit in the copy every 4096th submit must count exactly those). (2) spike cull counts equal per arm rate. (3) GLUE_TIME
spike+tail on fused seconds ~= old - 2x null. L1 and L12, dd4 16:9.
Recipe base: `zsh scratch/s7634/run.zsh <lvl>` (edit the env string); needs host idle + AC. Never launch under lldb; never
touch build/saves; one game at a time; kill only by SIGKILL.
If the split turns out to entangle state (bodies reading other commands' bytes ahead of `a`), stop: close item 24 as
"not worth it at ~0.1 ms/VI" with the reason, and take the next ladder rung.
