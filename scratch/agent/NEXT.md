# NEXT (s7634)
HYPOTHESIS-ID: bridge-walker-fusion

G6a/G6b/G6c still wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports on any of them, take that first.
Otherwise this is CURRENT-TRUTH item 24.

s7633 (class HB closed) measured the per-RDP-submit walkers in rs64_dpc_record_submit_impl (src/rsp/dpc_bridge.cpp ~6081) at
L1 dd4 16:9 FPS60: pillar (rs64_g1d_pillar_scan, already fused with rect_wrap by s7016, rs64_glue_fuse) 12.5 ms/s, spike
(rs64_spike_scan, CULL_SPIKE) 8.2 ms/s, tail (rs64_region_scan, armed at wide aspect by main.cpp:14403) ~6 ms/s. Each walks
the whole submit byte range again. Timer: ROGUESQ_GLUE_TIME=1 ([s7016-glue], per walk bucket, split by mach-second parity).

Hypotheses: H-walk (most of each walker's cost is the shared decode loop -> fusing saves ~half of spike+region, ~7 ms/s);
H-body (cost is in per-command bodies (spike: per-tri vertex math; region: bbox) -> fusion saves <2 ms/s, close as not worth it).
Discriminator, one build: add a cheap "decode-only" walk arm (ROGUESQ_S7634_NULLWALK=1 walks the submit with the same op-size
table and does nothing) timed in its own GLUE_TIME bucket in the same run. decode-only cost ~= spike+region cost -> H-walk ->
fuse; << -> H-body -> close, no change.
If H-walk: fold spike + region per-command bodies into the fused walk behind ROGUESQ_S7634_FUSE (default on, =0 old, =tog
mach-second parity like GLUE_TOG). Proof: byte-identical RDP output (ROGUESQ_G5B_FRAME recording, fused vs =0, same run via tog,
or s7016's fused_patches check pattern) + spike cull count equal + the GLUE_TIME saving; L1 and L12 at dd4 16:9.
Recipe: `zsh scratch/s7633/run.zsh` (arm.zsh 1 4 ..., HOLD 100+140, sampler from +90 s); needs host idle and AC.
Witness hygiene: kill only the game pid with SIGKILL; never launch under lldb; never touch build/saves; one game at a time.
