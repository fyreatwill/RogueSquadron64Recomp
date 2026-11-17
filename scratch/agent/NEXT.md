# NEXT (s7536)
HYPOTHESIS-ID: class-ga-early-spcomplete

s7535 found an OPEN H-latent-fix: ultramodern events.cpp sends the gfx sp_complete BEFORE send_dl, so in flight the game builds the
next frame into the 0x720000-0x75FFFF gfx pool while the F5 LLE still fetches it (same-run A/B ROGUESQ_S7535_GA_CHK=1 +
ROGUESQ_S7535_LATE=alt: diff bytes/task early 635 vs hardware-order 164 at L4, 472 vs 53 at L15 dd8 21:9; pool 1.19 MB vs 6.7 kB).
Read PORTING-STATE s7535 first.

Work unit (ONE build, every arm in one iteration, iron rule 13):
1. Standalone knob: ROGUESQ_SP_LATE=0|1|alt in events.cpp (the s7535 `s7535_late` decision without needing GA_CHK; alt = the same
   splitmix64(task)&1 per-task split). Echo the mode at boot. Keep ROGUESQ_S7535_LATE working (GA_CHK runs).
2. Visible consequence, same run, per task state (alt): count per state (i) CULL_SPIKE wedges culled (rs64_spike_scan: add a
   per-state counter), (ii) vertex-fetch diffs in the gfx pool (GA_CHK), (iii) terrain pixel fraction drops on presented frames if a
   per-task attribution is feasible (else per-second with alt period 1 s? NO - per-task split only; skip (iii) if not attributable).
   Arms: L4 dd2 16:9, L4 dd4 16:9, L1 dd8 21:9 (window grows with dd).
3. Cost: owner recipe FPS60 fullscreen, ROGUESQ_SP_LATE=0 vs =1 (two arms each, not alt: frame pacing is per run), L1/L4/L12 at dd1
   and dd4, OWNER_TIMING=1: fl_shown / tasks/s / [g1b] sd_wall. AC power only (battery x1.4: check pmset first; CLK_MAX refusal).
Hypotheses: H-visible (early-state tasks carry more spikes/drops -> the race is user-visible; fix is worth its cost), H-colour-only
(only shade bytes differ; no geometry effect -> fix is fidelity-only), H-cost (late SPC drops FPS60 below 60/s -> keep opt-in, or
deliver SP done at the LLE's last input fetch instead of after send_dl).
Discriminator: per-state spike count ratio (alt, same run) + fl_shown early vs late.
Gate: census tools/s7535_ga_census.py exits 0 only after the fix lands (rule -> H-latent-FIXED with a verify on the knob).
Never flip a default without the owner (Durable constraints); propose with =0 old.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
