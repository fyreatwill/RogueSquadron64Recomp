# NEXT work unit — port host-boundary census for callback-table writer (post-maintenance)

HYPOTHESIS-ID: m5-callback-table-writer

Maintenance session 3359 completed; run this bounded census next. No audio
behavior change or mitigation is authorized.

Session 3356's independent retail oracle attributed all 19 callback-table
writes to guest PCs `0x80007928` (11) and `0x80007968` (8), with post-values
only `0x8009B5A8`, `0x8009123C`, or zero. This refutes a retail host/runtime
writer. The port table pre-populates three `0x8009123C` occupants before
the known direct callers run (sessions 3334–3337).

The unresolved question: which port code path writes `0x8009123C` into the
callback table before the known `0x8009BC50` registration call?

Competing hypotheses:

- `H-PortWriterIsIndirectJalr`: an untraced port jalr at or near `0x800919EC`
  writes `0x8009123C` as the registered value (the store is in the same
  function body that loads and calls the pointer, and the store uses `0x8009123C`
  as its argument rather than `0x8009B5A8`).
- `H-PortWriterIsEarlyInit`: a port-only early initialization path writes
  `0x8009123C` before the main registration loop, not through `registerSiCallback`
  at all.
- `H-PortWriterIsStoreViaAlias`: the callback table alias or base address
  differs in the port, causing a write to an untraced physical address.

Discriminating measurement: obtain independent retail physical watches for the
four callback slot words (physical range covering `0x8011A8A4`–`0x8011A8B4`).
Arm a positive control (whole-RDRAM watch) and confirm the slot addresses match
expectations. Run the port with an aggregated table-write log (build one
regeneration-surviving fprintf covering all `registerSiCallback` store sites
and the `0x800919EC` jalr site), one build, one run with the validated route
(spin-yield, title 1024, hangar 512 controls).

Do NOT change audio behavior or add a mitigation. Do NOT add per-event output
that perturbs the scheduler — use the aggregated drain model from session 3343.

Exact commands for the retail watch (positive control first):
```sh
cd tools/oracle
# Physical address of callback table base 0x8011A8A4 → 0x0011A8A4
# Whole-RDRAM control must fire first
python3 run_oracle.py --watch-write 0x000000:0x800000 --watchdog 90 --reach-phase 512
python3 run_oracle.py --watch-write 0x11A8A4:0x11A8B8 --watchdog 90 --reach-phase 512
```

Outcomes:
- Watch fires, writers are `0x80007928` and `0x80007968` only → refutes
  `H-PortWriterIsIndirectJalr` (same writers as retail, port anomaly is in
  argument not writer).
- Watch fires with a new writer PC → identifies the actual port writer.
- Watch does not fire → `H-PortWriterIsStoreViaAlias` (wrong physical address).
