# NEXT (s7525)
HYPOTHESIS-ID: rsp-task-v2p

Check `wc -c < docs/CURRENT-TRUTH.md` first (>60000 = MAINTENANCE iteration instead).

Unit: qualify ROGUESQ_S7524_V2P=1 (retail _VirtualToPhysicalTask applied to the DMEM OSTask copy, src/main/main.cpp
rs64_run_lle_gfx) under the DEFAULT instant-DPC bridge (no SLOWRDP). s7524 proved the port's DMEM task carries KSEG0 pointers where
retail has physical ones (the s7523 ring late-rewrite was this). Under the instant bridge the outputs could still differ:
- H-same: V2P changes nothing observable (DMA masks the high bits; CURRENT==END so L_116C proceeds either way).
- H-spin: s7095 'pend' (bridge snaps CURRENT to the new START at a ring wrap) + physical base -> L_115C (beq CURRENT==base) spins
  until the bridge's 64-identical-poll escape (rs64_dpc_current_read returns v+8): escape fires > 0, possibly a skipped command.
- H-branch: task-entry L_1DB0 decision changes (b2 vs b4/b5) because the buffer start is now physical vs END 0 after rs64_dpc_reset.
Discriminator, one build (already built), two arms back-to-back, L4 dd1 120 s each, same recipe:
  `mkdir -p scratch/s7525_v2p; env R=$PWD/scratch/s7525_v2p HOLD=120 DONE=quiet.done ARMS="1:off:ROGUESQ_FORCE_SAVE_MISSION=4+ROGUESQ_S7096_FWD=1+ROGUESQ_S7095_DPC=1" zsh tools/g1e_owner_quiet_arms.zsh`
  then the same with tag `on` and `+ROGUESQ_S7524_V2P=1` (check the s7095 env name in src/rsp/s7095_dpc_model.cpp first; copy
  build/rs64_s7096.log after each arm). Count: bridge escape fires (add a counter in dpc_bridge rs64_dpc_current_read if none is
  logged), s7096 MAIN missing/dup/order, s7095 shadow mismatch contexts, s7521 l1db0 branch counts (ROGUESQ_S7521 env), fb dump hash
  of a fixed frame if available. Positive control: the s7095 ctl (planted reset) must fire in both arms.
If H-same on L4 and L15 21:9: propose default-on to the owner (it is a retail-fidelity fix) with =0 restoring today's behaviour.
If H-spin: fix the bridge's wrap CURRENT to the hardware value (old END, as the s7095 shadow) under V2P, re-run.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
