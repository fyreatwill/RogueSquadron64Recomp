# NEXT (s7564)
HYPOTHESIS-ID: regen-fidelity-drift

19b s7420 CLOSED s7563 (H-blind: fixup_patches_host.py edits the never-weakened RecompiledPatches/patches.c; census
PATCHES-TREE/IMMUNE-TREE, control 4 plants a weak header there and must reopen; `--controls` is a regen_replay gate).
Unit: 19b(c) B40 A/B. s7558_b40_ab voided 5/5 (on battery -> g1e_owner_quiet_arms clk cap exit 2). Rerun in-session:
  check screen unlocked (CGSSessionScreenIsLocked) and HID idle first, then
  env ALLOW_SLOW=1 zsh scratch/agent/soak_queue/done/s7558_b40_ab_20261117-172950.sh   (6 arms x 240 s, R=scratch/s7558_b40_ab)
Hypotheses: H-gate0-safe (default B40=0 arms alive, no crash/stall: keep, report) vs H-passthrough-needed (gate-0 arms crash
or stall like s4700's synth crash 2/4 while B40=1 arms are clean -> recommend the s4701 pass-through default to the owner)
vs H-passthrough-harmful (B40=1 arms crash). Discriminator: per-arm alive/crash/stall from the tag= summaries; same-run
positive control = the probes' gen/s and ring present for every arm (arm with no ring = void, not a zero).
Then ask the owner about the B40 default (never flip it without them). If battery clock cap makes gen/s unreadable, say so.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
