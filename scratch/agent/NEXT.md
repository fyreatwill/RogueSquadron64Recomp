# NEXT: fold s6463_dd4_lvl10_retry + s6464_dd1_lvl10_ctl (both now carry FORCE_PLANET_UNLOCK=0xFF) (G1c phase 2)
HYPOTHESIS-ID: g1c-dd4-limits
H-recipe (fixed recipes pass lvl10 at dd1 and dd4 -> prior failures were the omitted export), H-dd4-real (dd1 passes, dd4 fails -> inspect m6/g1_lvl10s6463_dd4 keys/run.log), H-probe-race (SIGBUS in rs64_probe_audio_dma_write recurs -> lldb/ASan, name writer of probe->ranges).
Steps: tail scratch/agent/SOAK-RESULTS.md; summaries in scratch/agent/m6/g1_lvl10s6463_dd4 and g1_lvl10s6464_dd1; grep 'multiplier'. If clean: dd1 vs dd6 contact sheet for owner, then dd8 (raise clamp in apply_s6036 patch).
