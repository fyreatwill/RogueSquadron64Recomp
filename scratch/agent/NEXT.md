# NEXT work unit (s2029)

HYPOTHESIS-ID: m5-service-worker-dispatch-boundary

## Work unit

Implement one regeneration-stable writer/reaper join around
`stopVoiceSlotSynced` (`0x8009B268`) and shutdown call 3, then run one
phase-gated forced-LLE hangar capture. The new table must batch, in one build
and one run: both direct stop call sites (`0x8009BCD4` and `0x8009B3A8`), stop
entry/exit with slot, `ctx->r31`, status before/after, and the slot-record
address; every existing s2008 writer row; shutdown call 3 entry/scan/return;
service entry/store; and the s2006 positive control. Do not
force or skip a status value, change default audio, or enable the opt-in audio
image. Keep all diagnostics in `fixup_game_funcs.py` so regeneration can
reproduce them.

## Competing hypotheses and discriminator

- W1 legitimate writer/reaper ordering: call 3 invokes
  `stopVoiceSlotSynced` for the same slot, its caller is the shutdown loop, and
  the `0x8009B2C4` `0x01 -> 0x00` write occurs inside that stop call before the
  scan. Expected table: matching slot/address and stop call site
  `0x8009BCD4`, with no status-3 read.
- W2 wrong-slot or address alias: the writer is not operating on the slot
  shutdown is scanning. Expected table: mismatched slot/record address or a
  stop call outside the call-3 sequence.
- W3 hidden transition: another stop/reaper writer changes the state between
  call-3 entry and the scan. Expected table: an additional writer or stop
  interval, or a status transition not attributed to `0x8009B2C4`.
- W4 incomplete control: the phase gate or s2006 entry/exit control is absent.
  The run is not evidence for W1-W3 and must be repaired before interpretation.

The single discriminator is the phase-gated join table. W1, W2, or W3 is
selected only when the same row contains the positive controls and the
writer/stop/call ordering; a terminal PI `do_rom_read` crash after the table
does not erase it.

## Commands

Run the independent retail control first, with the whole-RDRAM watch armed:

~~~sh
tools/oracle/build/rs64_oracle --core ../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom ../rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 50 --hit-cap 10000 --watch-write 0x0:0x800000 --watch-write 0x154620:0x154632 --detail-watch 1 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --vi-trace > scratch/agent/s2029-groundtruth.log 2>&1
~~~

After adding the census to the fixup script, apply the incremental sentinel
patch, verify it, and build:

~~~sh
python3 -m py_compile ../N64Recomp/fixup_game_funcs.py
env RS64_S2029_STOP_JOIN=1 python3 ../N64Recomp/fixup_game_funcs.py
cmake --build build --target RogueSquadron64Recomp -j2
strings build/RogueSquadron64Recomp | rg 's2029|stop-entry|stop-exit|8009B2C4'
~~~

Run one capture and use SIGKILL only if the wrapper does not terminate itself:

~~~sh
env ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_CALLER=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_S2008_STATUS_WRITERS=1 ROGUESQ_LOG_S2029_STOP_JOIN=1 'PROBE_KEYS=6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 PROBE_LEAVE_OK=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 zsh tools/probe.sh scratch/agent/s2029-writer-reaper 120 2 > scratch/agent/s2029-writer-reaper.stdout 2>&1
~~~

Consume only bounded counts and selected phase/width rows from `run.log`; do
not cat the log.
