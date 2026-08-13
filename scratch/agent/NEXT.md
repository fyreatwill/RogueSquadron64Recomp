# NEXT work unit (s864)

HYPOTHESIS-ID: m3-coalesce-entry-state

Run one retail-oracle writer-attribution experiment. Watch the coalescer caller
globals at physical `0x1163E4:0x1163F0` and the coalescer head global at
`0x10FF18:0x10FF1C`, alongside the whole-RDRAM positive control. Include
`--vi-trace` and the documented repeated-Start schedule. Do not build, edit
runtime behavior, or add a mitigation.

Competing hypotheses:

- H-retail-writer: a watched state write fires with a guest PC, identifying the
  writer boundary that can be compared with the port's invalid entry values.
- H-retail-no-write: whole-RDRAM and VI controls fire but neither state watch
  fires; retail initializes this state elsewhere or the target phase is not
  reached.
- H-retail-control-invalid: whole-RDRAM or VI positive control fails, so a null
  state watch is unevaluable.

Discriminating measurement: in the same run, whole-RDRAM must report writes and
`--vi-trace` must report VI activity. With both controls live, any hit in either
state range selects H-retail-writer; zero hits selects H-retail-no-write. Failed
controls select H-retail-control-invalid. A null is not evidence without both
controls.

Exact command:

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 30 --watch-write 0x0:0x800000 \
  --watch-write 0x1163E4:0x1163F0 --watch-write 0x10FF18:0x10FF1C \
  --vi-trace \
  --press '6:start,11:start,16:start,21:start,26:start'
```

Keep the current probe build; no port run is needed unless the oracle controls
are valid and the result requires a paired port measurement.
