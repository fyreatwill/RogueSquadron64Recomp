# Next work unit: trace the first divergent writer object-field input

HYPOTHESIS-ID: m5-step4-object-field-boundary

Session 4173 selected H-context-mismatch. The retail oracle reached the
positive-control threshold, title VI 1024, and hangar VI 512; all five field
watches fired in hangar. The port reached the same phases and retained live
source/image/PCM controls, but its matched `0x800AB694 -> 0x800078EC` context
did not expose the retail per-object source-word/branch-field state and its
target-span payload stayed zero.

Do exactly one phase-gated instrument build/run. Use the existing
`scratch/agent/run_s4148_m5_source_callsite.sh` as the base. Add a single
port-side field/object witness for the first divergent relation identified by
the retail rows (object base plus the source word/branch field used by
`0x80090268`, `0x80090278`, `0x8008FF04`, `0x8008FF0C`, and `0x8008FF14`). Keep
the retail `--pc-field-dump` watches, whole-RDRAM positive control,
`PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`, real-audio/LLE/ungated/
solo route, and all existing source/task/image/PCM logs. Run both arms in one
build/run; kill with SIGKILL and capture under `build/`.

Discriminator:

- H-legitimate-field-mismatch: the port counterpart has a real, stable object
  and field relation, but its value/provenance differs from retail; select
  that writer/input boundary.
- H-instrumentation-alias: the apparent mismatch is caused by a join/address
  alias; object identity and field values reconcile after the witness.
- H-route-invalid: either arm misses the positive control or title/hangar VI;
  all object and PCM nulls are unevaluable.

No audio, gate, writer, payload, or mitigation behavior change is authorized.
