# NEXT work unit — port callback-table writer/source census

HYPOTHESIS-ID: m5-callback-table-writer

Session 3360's independent retail oracle passed the whole-RDRAM positive
control, reached title 1024 and hangar 512, and recorded 20 callback-table
writes. Writers were `0x80007928` (9), `0x80007968` (6), and `0x80017D08`
(5). Sampled values included `0x8009123C`; the new writer-to-value pairing is
not yet joined. The port table pre-populates three `0x8009123C` occupants
before the known direct callers run.

Competing hypotheses:

- `H-PortWriterIsIndirectJalr`: an untraced port jalr near `0x800919EC`
  writes `0x8009123C` as the registered value.
- `H-PortWriterIsEarlyInit`: a port-only early initialization path writes the
  value before the main registration loop, outside `registerSiCallback`.
- `H-PortWriterIsThirdGuestSite`: a port guest-side store corresponding to
  retail `0x80017D08` supplies the problematic value.
- `H-PortWriterIsStoreViaAlias`: the port writes the table through a different
  base, so the expected physical range is unobserved.

Discriminating measurement: build one regeneration-surviving aggregated port
log recording every callback-table store's site, slot, and value, plus the
`0x800919EC` indirect edge. Run once with the validated task/host/title/hangar
controls. A third-site/value pairing selects `H-PortWriterIsThirdGuestSite`;
only known sites with `0x8009123C` select the indirect/argument path; no target
rows select alias or route invalidity. Positive controls must all fire in that
same run.

Before building, inspect the existing aggregate instrumentation and update
the fixup source that regenerates it. Then run:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Use the established Debug AUTOPILOT/spin-yield recipe, with task/host probes,
VI phase gates, and aggregated drain output. Do not change audio behavior, do
not add a mitigation, and do not emit one line per store from the hot path.
