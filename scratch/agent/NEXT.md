# NEXT work unit (s2606) — re-evaluate M5 writer call-path on the restored route

HYPOTHESIS-ID: m5-writer-callpath-requal

## Single work unit

s2605 restored the `convertMat3x4ToN64Mtx` jr-$t9 host return and reached
title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400` with AUTOPILOT. s2586's
writer-entry census was unevaluable because that abort fired at first 640.
Re-run that complete writer/call-path table on the restored route. Do not
change stores, gates, task fields, or output pointers.

The generated-symbol census at `0x800E8A34` stays parked for this unit.

## Competing hypotheses and discriminator

- `H-PortWriterReachable`: retail-named `0x8008ED48` (`musyxNoopStub` `sb
  $zero`) and/or `0x80094648` run in title/hangar now that the converter
  continuation returns.
- `H-PortWriterMissing`: those sites still do not run; only
  `reapplyDisplayMode` `0x8008EC88` writes the gate (force-zero unless
  `ROGUESQ_M5_C88_VALUE` is set).
- `H-RouteAbortAgain`: the run dies before title/hangar, so the table is
  unevaluable.

The discriminator is one AUTOPILOT hangar run of the current image arm with
the existing s2586 writer-entry / gate / PCM instruments. Require title and
hangar phase rows as the positive control. A writer-PC table in both phases
selects reachable vs missing; an abort before those phases selects
`H-RouteAbortAgain`.

## Exact checks

1. Confirm `python3 tools/check_jr_t9_host_return.py` still passes (do not
   regenerate unless the canary fails).
2. One build if the writer-entry helper is not already in the binary; otherwise
   reuse the s2605 image.
3. Run from `build/` with ROM present:
   `env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_WRITER_ENTRY=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' ROGUESQ_AUTOPILOT_STOP_WIDTH=512 ./RogueSquadron64Recomp`
   SIGKILL at ~90s. Capture to a `scratch/agent/` log whose final component
   does not start with `.`.
4. Tabulate, per title and hangar: writer function, guest PC, store value,
   gate byte, and whether `0x8008ED48` / `0x80094648` / `0x8008EC88` fired.
   PCM source/consumer rows are supporting evidence, not a substitute control.
