# NEXT (s7573)
HYPOTHESIS-ID: guard6-fire-census

S6892 closed s7572 (CHAIN(TILEPOOL), dead at defaults); docs/COMPENSATION-CHAINS.md has 0 UNKNOWN. Remaining unexplained
default-on class: GUARD 6 (ROGUESQ_COPY_GUARD s5037, PIO_GUARD s5062, PI_DMA_GUARD s5061, SPAI_GUARD s5063, GR s1978
drain-base/hdr hang breaker, GR musyxKeyOnVoice div-trap). Each repairs a wild value whose writer was never named (rule 11).
Hypotheses per guard: H-dead (never fires on the retail route at defaults: keep as cheap insurance, note it), H-live-ours
(fires, and the bad value comes from a port deviation: name it, CHAIN), H-live-retail (fires on a retail-legal value the
real hardware tolerates: RETAIL-GAP, name the hardware behaviour).
Discriminator, one build: a per-guard fire counter (+ first 4 fire PCs/values) dumped at exit, each with a planted control
env that forces one fire (positive control per guard), arms L1/L4/L12 dd1 4:3 and owner recipe, 180 s each.
First check the boring thing: grep each guard's existing stderr breadcrumb in retained scratch logs (capture once, analyze
many, as s7572 did) — that may already answer H-dead for some without a build.
Outcome: one verdict per guard in tools/s7565_comp_chain.py; then item 21 (next 3c rung).
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
Run template: scratch/s7572/run.zsh (g1e_owner_quiet_arms, ALLOW_SLOW; ARMS "dd:tag:ENV+ENV").
