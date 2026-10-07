# Next work unit: join matched source writers to caller/object context

HYPOTHESIS-ID: m5-step4-writer-context-join

The previous iteration landed and built the audio task-contract guard. Keep
the valid declared `0x800` image path; do not use the new reject path as an
explanation for the qualified zero PCM payload.

Run one phase-gated retail/port comparison using
`scratch/agent/run_s4148_m5_source_callsite.sh`. Extend the retail command
with `--pc-field-dump 0x80090268,0x80090278,0x8008ff04,0x8008ff0c,0x8008ff14`
and retain `--pc-hist-watch 1 --post-value-watch 1 --watch-pc 0x800078EC`.
Keep the whole-RDRAM positive control, `PROBE_PHASE_WIDTH=1024`,
`PROBE_KEYS_FROM_PHASE=1`, and the real-audio/LLE/ungated/solo route. Keep
the existing M5 source/context, task-contract, and PCM logs. Kill all game
processes with SIGKILL and capture from `build/`.

Competing hypotheses and discriminator:

- H-context-parity: retail field/context rows and port source-producer rows
  agree on caller/callsite, object base, destination layout, and value
  provenance; the boundary moves earlier to the producer input.
- H-context-mismatch: at least one matched writer has a missing or different
  caller/object/destination/value context in the port; select the first such
  row as the next source boundary.
- H-route-invalid: either arm misses the whole-RDRAM positive control or
  title/hangar VI, making context and PCM nulls unevaluable.

The result table must include route/positive-control status, retail field and
caller context, port writer context/destination/value, source-span FNV/nz,
image task input, and PCM source/consumer. A parity result advances to the
producer input; a mismatch result audits the first divergent context. No
mitigation is authorized without an identified writer and legitimacy check.
