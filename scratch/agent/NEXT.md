# NEXT work unit — M5 callback-table writer/alias audit

HYPOTHESIS-ID: m5-consumer-reachability-audit

Session 3354 selected `H-PortConsumerIndirectGap`: retail independently shows
`0x8011A8A4 -> 0x80019B74 -> 0x8009B5A8`, while the qualified port route has a
live callback loop but only `[80003250,8009123C,8009123C,8009123C]` and zero
consumer entries. Keep that selection; do not add a status workaround.

Competing hypotheses for the next unit:

- `H-PortTableWriter`: a distinct registration path writes the port's three
  `0x8009123C` callback occupants and prevents the retail target from being
  installed.
- `H-PortTableAlias`: the port and retail use different base/address aliases,
  so the existing census observes different logical tables.
- `H-PortDispatcher`: the table matches retail, but the generated dispatcher
  loads or dispatches the wrong slot value.

Discriminator: statically enumerate every generated read/write of
`0x8011A8A4..0x8011A8B4`, every `registerSiCallback` base/alias, and the
`0x80019B74` load/`jalr` sequence, then reconcile each with the port census.
A writer that can produce `0x8009123C` at the exact callback-table slot
selects `H-PortTableWriter`; a base mismatch selects `H-PortTableAlias`; an
exact table match with a wrong loaded target selects `H-PortDispatcher`.
If no static source explains the occupants, record the writer as unresolved
and do not add a probe or behavior change.

Ground truth completed in Session 3354. Do not build until the bounded static
audit selects one writer, alias, or dispatcher outcome; this unit is static
and should not require a runtime build.
