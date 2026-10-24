# NEXT: G1c - fold s6050_dd2_l5, s6050_dd2_l10 (now with planet unlock), s6051_dd1_l10pu (control)
HYPOTHESIS-ID: g1c-draw-distance
Hypotheses: H-holds (2x survives 300 s on lvl5 and lvl10 with span-table bound) vs H-levelspecific (another unbounded writer on those levels crashes).
Discriminator: SOAK-RESULTS rc and run-dir summary (crashlines, vi_stalls30s) for tags g1cdd2l5, g1cdd2l10pu; controls g1cdd1l5 (done, clean) and g1cdd1l10pu must be rc=0. Check `grep -a '[spanbound]'` / '[gridlog]' in scratch/agent/m6/g1_lvl*/run.log.
If crash: lldb backtrace, name writer (iron rule 11). If both pass: G1c half done; build G1b per-VI wall-clock instrument for the frame-time clause (ROGUESQ_G1B already logs sd_wall/sd_cpu per second - use it), then ask owner to judge the look.
NOTE: level 10 recipes MUST export ROGUESQ_FORCE_PLANET_UNLOCK=0xFF and SOAK_TIMEOUT>=900.
