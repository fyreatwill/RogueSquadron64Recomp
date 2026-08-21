# NEXT work unit (s2113) — resolve the image-task completion/output contract

HYPOTHESIS-ID: m5-audio-image-task-contract

## Work unit

Add one regeneration-stable, phase-keyed contract table covering the opt-in
Factor 5 image task from host dispatch through generated final DMA, the
image-side `break 0`, host task exit/writeback, output-buffer selection, and
the first slot/PCM consumer. Run the same build with the default silent stub
and `ROGUESQ_AUDIO_UCODE=1` arms concurrently. Include task ordinal, stage,
guest source/destination/length, full-span hash/nonzero count, break PC,
`RspExitReason`, output buffer, canary result, slot status, and PCM join.
Require a positive dispatch/DMA control in each arm before interpreting any
null. Do not change task fields, DMA, exit mapping, output routing, canary,
slot, PCM, waits, guards, queues, or default behavior.

## Competing hypotheses and discriminator

- H-TaskExitMapping: the generated `break 0` is the legitimate completion
  edge, and the host `Broke` result is compatible with the valid task output.
- H-OutputRoute: the image task produces a valid nonzero span, but the host
  routes or names the output buffer incorrectly before slot/PCM consumption.
- H-WritebackLoss: the generated task writes a valid span, but host writeback
  or the task-field destination loses it before the canary/consumer boundary.
- H-NoValidOutput: the task's final fields or transformed data are invalid or
  zero at the output boundary, so no host contract change is justified.

The single joined table is the discriminator. A valid span plus matching
writeback and a `Broke` exit selects H-TaskExitMapping; valid span plus a
different output/consumer destination selects H-OutputRoute; valid generated
DMA followed by failed host writeback selects H-WritebackLoss; and zero or
invalid final data with positive dispatch selects H-NoValidOutput. Missing
rows despite positive dispatch/DMA select an instrumentation-coverage defect;
do not add another field in this iteration.

## Ground-truth prerequisite

Before adding the contract witness, run the retail whole-RDRAM positive
control and physical `0x000A0F50` read watch. Retail does not reach the port's
mission route, so only the positive control and named writer/read PCs are
coverage evidence; a null target-task result is not evidence about the port.

## Exact commands

Confirm the existing image-task and host anchors before editing:

    rg -n 'ROGUESQ_AUDIO_UCODE|RspExitReason::Broke|output_buff|canary|pcm|audio.*dispatch|break 0' src/main ../N64Recomp/fixup_game_funcs.py ../N64Recomp/RecompiledFuncs/funcs_*.c | head -160

Run the independent retail controls first:

    tools/oracle/build/rs64_oracle --core ../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom ../rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 8 --hit-cap 100 --watch-write 0x0:0x800000 --watch-read 0x000A0F50 --first-watch 1 --detail-watch 1 --pc-hist-watch 1 --vi-trace > scratch/agent/s2113_oracle_audio_contract.log 2>&1

Keep the durable transform in `fixup_game_funcs.py`. Do not invoke the
known unsupported `../N64Recomp/build/N64Recomp`; use the older complete
recompiler only if it exists. If it does not, preserve the intact generated
tree and apply the new diagnostic transform there without truncating it.
Build once:

    python3 -m py_compile ../N64Recomp/fixup_game_funcs.py
    cmake --build build --config Debug --target RogueSquadron64Recomp

Run both arms concurrently from the repository root with the same route,
ABI/DMA, stage, slot, PCM, ordering, and VI controls:

    env GAME_EXTRA_ENV='ROGUESQ_M5_B40_VALUE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2113_m5_task_stub 30 12 > scratch/agent/s2113_m5_task_stub_driver.log 2>&1
    env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_B40_VALUE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2113_m5_task_image 30 12 > scratch/agent/s2113_m5_task_image_driver.log 2>&1

Kill remaining process groups with SIGKILL. Inspect only phase-keyed counts,
joined rows, and tails; never read a full run log.
