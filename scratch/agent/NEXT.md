# NEXT (s7432)
HYPOTHESIS-ID: default-fprintf-cost

Fold new scratch/agent/SOAK-RESULTS.md lines first (s7428_audio_route_arms: rc 0 = F9 gate two-arm verified; 2 = VOID).

Class CO (CURRENT-TRUTH Next steps item 1): s7431 capped what reaches the terminal, but 37 default-on tags still format every
frame on the calling threads (gfx thread: [dpc-fwd], [lle, [vi-mode-table]/[osViSetMode]; guest thread: [s2020-svc],
[s3290-stall], [s5855] ~5 KB/line, [s3294-stall], ...). Hypotheses: H-free (formatting + pipe write < 0.1 ms per frame on each
thread: the cap is enough) vs H-cost (gating the per-frame default-on sites at source lowers gfx-task ms or raises game fps at
FPS60 dd4 16:9 by a measurable amount) vs H-guest (cost lands on the guest thread only: game frame time, not gfx).
Discriminator, ONE build: a single global switch ROGUESQ_DIAG_QUIET=1 (read once into a global) that the top ~15 per-frame
sites test before fprintf (sites listed in the s7431 PORTING-STATE entry; generated sites go into their tools/apply_*.py /
fixup scripts, never hand-edit RecompiledFuncs), toggled IN-RUN at a fixed second (ROGUESQ_DIAG_QUIET_AT=<s>, phase-gated,
same-run A/B) on lvl1 flight with OWNER_TIMING-style gfx path and the G1b per-VI timing ring (ROGUESQ_PRESENT_RING) dumped
at exit. Compare gfx task host-ms and game fps before vs after the switch. Positive control: an injected 1 ms busy-wait
per frame toggled at a second time point must show up in the same metric. Then: if H-cost, make the quiet switch default-on
(sites become opt-in via ROGUESQ_DIAG_LOUD=1 for harnesses that parse them - check every grep in scratch/agent/*.sh first).
Reuse tools/s7431_stderr_volume.sh copied-folder runner.
