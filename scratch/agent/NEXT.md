# NEXT: G1 mission progression - lvl7 now soaks clean (n=3+). Queue lvl2/lvl3/lvl5 forced-save soaks (recipe: scratch/agent/soak_queue/done/s5714_lvl7b.sh with FORCE_SAVE_MISSION/UNLOCK=N), x2 each; log every CRASH/stall; fix each distinct failure at the root (name the writer).
H1: other missions crash on a new family; H2: they soak clean like lvl1/4/6/7. Discriminator: CRASH/SIGSEGV count + VI-origin stalls in run.log vs control line [lvsel] init.
HYPOTHESIS-ID: g1-level-select
