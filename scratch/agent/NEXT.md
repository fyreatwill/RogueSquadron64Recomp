# NEXT work unit (s2153) — A13 busy-return polarity

HYPOTHESIS-ID: m5-ai-status-poll

## Work unit

s2152 closed the presence/execution half of A13 (`H-BusyIsThePoll`).
Named `osAiGetStatus` is not a jal target. Do not change
`osAiGetStatus_recomp`. The live host shortcut is
`osAiSetNextBuffer_recomp` skipping `__osAiDeviceBusy`.

The next unit is one retail-oracle census of the set-next reject path
versus the success path, with whole-RDRAM, `osAiSetNextBuffer`, and
`__osAiDeviceBusy` as same-run controls. No port build, audio-arm change,
task ABI, output route, host-shortcut edit, guard, or default dispatch
change.

## Competing hypotheses and discriminator

- `H-BusyAlwaysClear`: after title/hangar gates, success PC `0x80029EF4`
  (`jal osVirtualToPhysical`) equals `osAiSetNextBuffer` count and reject
  PC `0x80029EF0` (`li v0,-1`) stays at zero.
- `H-BusySometimesFull`: reject PC `0x80029EF0` is nonzero in the same
  run as live set-next/busy and title/hangar gates.
- `H-BusyReturnUnmapped`: the two PCs do not partition the set-next
  count (success + reject != set-next, after allowing the n=1 dispatcher
  resume at `0x8002BEEC`).
- `H-CoverageFailure`: whole-RDRAM control or title/hangar VI gates miss,
  so a zero reject count is unevaluable.

The discriminator is one table: whole-RDRAM write control, title `1024`
plus hangar `512 @ 0x006AB400`, `osAiSetNextBuffer` count, 
`__osAiDeviceBusy` count, success PC `0x80029EF4` count, reject PC
`0x80029EF0` count. Zero reject with matching success/set-next selects
`H-BusyAlwaysClear`; nonzero reject selects `H-BusySometimesFull`;
non-partitioning counts select `H-BusyReturnUnmapped`; missing
control/gates select `H-CoverageFailure`. Do not treat a silent
`AI_STATUS_REG` MMIO watch as evidence.

## Exact commands

    tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
      --secs 70 --hit-cap 64 \
      --watch-write 0x0:0x800000 \
      --watch-pc 0x80029E80,0x80029F30,0x80029EF4,0x80029EF0 \
      --first-watch 0 --vi-trace \
      --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
      > scratch/agent/oracle_s2153_ai_busy_return.log 2>&1

If the first oracle run saturates `--hit-cap` before the PC watches
count, rerun with `--detail-watch` on the four PC watches after the
whole-RDRAM threshold, following the s2121/s2134/s2152 recipe. Counts
and `exec-prev` remain the discriminator even when `[hit]` lines go
silent. Do not change `osAiGetStatus_recomp` or `osAiSetNextBuffer_recomp`.
