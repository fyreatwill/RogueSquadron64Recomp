# NEXT (s7636)
HYPOTHESIS-ID: spike-body-cost

G6a/G6b/G6c still wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports on any of them, take that first.
Otherwise CURRENT-TRUTH item 25.

s7635 landed walker fusion (saving only ~0.8 ms/s; fused spike+region ~8.3 ms/s at L1 dd4 16:9 FPS60, region body ~4.1/half).
The spike body (default-on CULL_SPIKE) decodes every triangle to doubles (sx14, fx, 5 vertices) and tests a guard band.
Hypotheses: H-fp (double decode + guard compare dominate: an integer fast path - compare raw s11.2 y and s15.16 x words against
precomputed integer bounds, compute doubles only when bad or a diag file is open - saves >=2 ms/s), H-mem (cost is the loads of
the tri words, shared with the region body; fast path saves <1 ms/s).
Plan (one build): ROGUESQ_S7636_FASTSPIKE default 0 while measuring, tog = fast on even GLUE_TOG=3 seconds, chk = both paths,
count disagreements of `bad` (must be 0; control: chk with guard perturbed by 1 px every 4096th tri must count those).
Run `zsh scratch/s7635/run.zsh <lvl> <name> "<env>"` at L1 and L12 (GLUE_TIME=1 GLUE_TOG=3), score with scratch/s7634/an.py.
Decide: >=2 ms/s saved and chk 0 -> default on; else close item 25 as H-mem and take the next ladder rung (renaming sweep, item 4).
Never launch under lldb; never touch build/saves; one game at a time; SIGKILL only.
