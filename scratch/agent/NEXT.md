# NEXT (s7540)
HYPOTHESIS-ID: class-gb-device-done-before-read

s7539 measured the open GB row TORN: under ROGUESQ_RDP_ASYNC=1 ROGUESQ_RDP_NODRAIN=1 RT64's fullSync tail (the only place RT64 reads
texture sources from RDRAM: State::fullSyncFramebufferPairTiles -> load*Operation(deferred=false), lib/rt64/src/hle/rt64_state.cpp
~3110-3140) runs after dp_complete; on L1/L4/L12 one 2 KB 4-bit texture re-decoded every frame by swizzleTextureRowsToTmem
(0x800249B4/E4, via parseImageFile) is read while the CPU rewrites it (167-354 torn loads per 2-min flight). Read PORTING-STATE s7539.

Work unit: land an opt-in fix that ends the read window and keeps most of the overlap, then qualify it in ONE build, same-run arms.
- Mode ROGUESQ_RDP_NODRAIN=3: the worker sets a per-task "reads done" flag (+cv) right after the LAST fullSyncFramebufferPairTiles
  call of the job that runs fullSync (and after checkRDRAM/storeRAM reads, check what else in fullSync reads RDRAM first: grep
  RDRAM in State::fullSync 1945-3200); rs64_rdpq_task_exit in mode 3 waits for that flag instead of drain(). Hook from rt64 via an
  extern "C" rs64_s7540_reads_done() like rs64_s7539_load. Note the loop at ~3110 calls renderAndSynchronize per fb pair when
  fbPair.syncRequired (f>0 && !copyWithGPU), so with several fb pairs the wait still includes intermediate GPU syncs; measure.
- Also fix NODRAIN=2 so it alternates per TASK when async stays on (today async_windows only counts 0->1 flips, so =2 == =1),
  or add =4 alternating 1/3 per task: that gives a same-run A/B of torn loads and drain cost.
- Qualify: tools/g1e_owner_quiet_arms.zsh HOLD 120, owner recipe FPS60 16:9 fullscreen, L4 dd4 + L12 dd4 + L1 dd8 21:9, env
  ROGUESQ_RDP_ASYNC=1 ROGUESQ_RDP_NODRAIN=<alternating mode> ROGUESQ_S7539_GB_CHK=1 ROGUESQ_G1B=1 (for [g1e-aq] drain ms per as=).
  Score with python3 tools/s7539_gb_score.py <logs> (it reads as=3 rows; extend it to report each mode tag).
Hypotheses / outcomes:
- H-fix-cheap: mode-3 diff_loads 0 (planted caught, older-snapshot diffs > 0) and drain ms well below a full drain (~3.3 ms)
  -> recommend NODRAIN=3 in OWNER-OPT-INS instead of =1; census row -> H-latent-FIXED(opt-in), census exits 0.
- H-fix-costly: diff 0 but drain ~= full drain (reads finish late, e.g. many fb pairs) -> capture the load sources on the producer
  instead (parse SetTextureImage/SetTile/Load* in submit(), copy those bytes into the job, have the load hook read them).
- H-residual: mode-3 diff_loads > 0 -> some RDRAM read sits after the flag; find it with the gbd events.
Battery note: on battery (clk ~1.5) timing arms need ALLOW_SLOW=1 and are only comparable within the same run.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
