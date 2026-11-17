# NEXT (s7524)
HYPOTHESIS-ID: rsp-dpc-register-model

Check `wc -c < docs/CURRENT-TRUTH.md` first: it was 58.5 KB after s7523; >60000 means a MAINTENANCE iteration instead.

Unit: name the writer of FT's same-task ring late-rewrites (s7523, CURRENT-TRUTH item 20 FT paragraph).
Under ROGUESQ_S7523_SLOWRDP (DP-gated), bytes of queued RDP ranges change after the END write + bridge submit and before the
model RDP consumes them, within the same task index (L4 dd1 8 B/poll: 1.5% of bytes; L15 dd8 21:9 64 B/poll: 0.004%).
Hypotheses:
- H-rsp-race: the gfx ucode itself overwrites ring bytes later in the same RSP task (its L_116C/L_114C waits would then be
  insufficient under a slow RDP = a retail ucode property, hardware-identical, not ours).
- H-cpu: the CPU thread (running concurrently with the port's RSP thread, after the port's instant DP/SP completion) rewrites
  the memory, i.e. the buffer is free on the port's timeline but not on hardware's.
- H-bridge: a dpc_bridge commit/edit path (deferral commit, synthetic FULL_SYNC, record_submit edit) writes RDRAM after submit.
Discriminator (one build, one run per level): in src/rsp/s7523_slow_rdp.cpp re-compare every still-queued range at (a) RSP task
end (hook where run_task returns for the gfx task, e.g. rs64_run_lle_gfx after the ucode returns) and (b) the next rs64_dpc_reset.
Changed at (a) -> RSP in-task (then log the r17/DMEM DMA address of the write via the DMA hook rsp.hpp dma_dmem_to_rdram ranges
overlapping a queued range -> H-rsp-race confirmed with the DMA site). Unchanged at (a) but changed at (b) -> CPU or bridge between
tasks: then flag bridge writes (grep dpc_bridge for RDRAM stores) with a thread-local "in bridge" bit. Also record the first
overlapping dma_dmem_to_rdram per mismatch: positive control = the ring chunk DMA itself must row on a planted early-snapshot.
Runs: `mkdir -p scratch/s7524_ft; env R=$PWD/scratch/s7524_ft HOLD=120 DONE=quiet.done ARMS="1:l4:ROGUESQ_FORCE_SAVE_MISSION=4+ROGUESQ_S7523_SLOWRDP=8,0+ROGUESQ_S7096_FWD=1"
zsh tools/g1e_owner_quiet_arms.zsh` then the L15 arm `8:l15:ROGUESQ_FORCE_SAVE_MISSION=15+ROGUESQ_ASPECT=21:9+ROGUESQ_S7523_SLOWRDP=64,4096`
(run separately; copy build/rs64_s7096.log after each, the harness overwrites it).
If H-rsp-race: FT closes H-dead (retail ucode property, the port's instant RDP never exposes it). If H-cpu/H-bridge: report as a
would-be divergence only reachable with a slow RDP; close FT and take item 21.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
