# NEXT (s7535)
HYPOTHESIS-ID: class-ga-host-read-decide

CURRENT-TRUTH is 26.9 KB after s7534 maintenance; no maintenance due. FZ qualified (s7533_fz_levels score 0).

Work unit: class GA static census (FV-FZ model: tools/s7529_fv_census.py .. tools/s7533_fz_census.py as templates).
Idiom: host-thread code that READS a guest RDRAM byte/word and takes a decision (branch, size, skip, index) while the
guest may change it in the same window (render-context / dpc_bridge / main.cpp present / FPS60 arbiter readers,
lib/rt64 hle readers already covered by FX are excluded).
Hypotheses per site: H-canon (read happens on the guest thread or under a guest-stopped barrier), H-dead (value
cannot change in the window: written once at init), H-latent-fix (torn/stale decision possible -> fix: snapshot once
under the existing lock, or move the read to the guest side).
Discriminator: census rows with thread + window evidence; for each H-latent-fix a same-run plant control
(ROGUESQ_S7535_GA_CHK) on L4 dd1 + L15 dd8 21:9; then queue a levels soak like s7533_fz_levels.
Tool: tools/s7535_ga_census.py --controls (synthetic rows must fire). Gate: 0 unclassified.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
