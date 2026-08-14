# NEXT work unit (s1114)

HYPOTHESIS-ID: retail-oracle-mode-state-route

Run one phase-gated retail-oracle capture using the rebuilt debugger-enabled
core. Keep the whole-RDRAM, PIF, and VI controls armed; watch the mode selector
and pending-mask family identified by s1112 plus target `0x8011A8A0` (physical
`0x11A8A0`). Do not interpret target zeros unless the controls pass and the
512/1024 phase is reached.

Competing hypotheses:

* H-mode-writer: selector/pending-state writes occur before the 512/1024 phase,
  and their PC/value trace identifies the retail lifecycle gate.
* H-A0-writer: the A0 byte is written by the retail route, with a PC/value
  attribution independent of the port's generated-store probe.
* H-pre-phase-boundary: all controls pass but neither watched state family nor
  A0 is reached before the established attract route ends; the boundary is
  earlier than the suspected consumers.

Discriminator: the phase-gated run's independent PC-attributed writes and
controls. Mode-family writes before 512/1024 select H-mode-writer; an A0 write
with controls and phase selects H-A0-writer; positive controls without either
watch class or the phase select H-pre-phase-boundary. A zero target watch with
failed controls is invalid.

Exact commands:

```sh
mkdir -p scratch/agent/oracle_mode_capture
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom build/rogue_squadron.z64 --secs 120 --watch-write 0:0x800000 --watch-write 0x11A862:0x11A866 --watch-write 0x128E90:0x128E98 --watch-write 0x11A8A0:0x11A8A1 --vi-trace --vi-poll --pif-trace --press 6:return,12:return,18:return,24:return,30:return,36:return,42:return,48:return,54:return,60:return,66:return > scratch/agent/oracle_mode_capture/run.log 2>&1
```

The whole-RDRAM watch must reach its positive-control threshold, PIF must show
the scheduled Start edges, and VI callback/poll traces must agree. If the
front end's watch capacity rejects this four-watch command, increase capacity
in one bounded source edit and rerun the same complete table; do not drop a
watch.
