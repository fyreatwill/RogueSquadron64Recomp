# NEXT work unit — M5 callback-table runtime writer attribution

HYPOTHESIS-ID: m5-consumer-reachability-audit

Session 3355 refuted a generated-table alias and dispatcher explanation. The
remaining candidate is a host/runtime or unresolved indirect writer that
populates the port's `0x8009123C` callback occupants before the qualified
consumer route, preventing `0x8009B5A8` from being installed.

Competing hypotheses for the next unit:

- `H-RuntimeTableWrite`: host/runtime code writes the guest callback table
  outside generated MIPS execution.
- `H-IndirectGuestTableWrite`: a generated indirect path writes the table but
  is absent from the literal/static census.
- `H-StaleTableState`: the table is not reset between overlay/runtime phases,
  so the occupants are valid earlier state rather than a writer defect.

Discriminator: first ask the retail oracle for a physical watch on all four
callback slots, with whole-RDRAM and title/hangar controls, and capture each
write's guest PC/value. In parallel, inspect the host write boundary exposed
by the existing callback-table census and runtime memory helpers; only build a
port instrument after the oracle control confirms the watch is live. A retail
write with no guest PC plus a matching port transition selects
`H-RuntimeTableWrite`; a guest PC outside the known generated writers selects
`H-IndirectGuestTableWrite`; a reset/phase transition with no corresponding
write selects `H-StaleTableState`. A null watch without its positive control is
unevaluable.

Exact commands: inspect `tools/oracle/README.md` and the existing oracle recipe
before preparing one watch matrix; use `rg -n
'callback_table|11A8A4|registerSiCallback' src lib tools`; do not build or
change behavior until the oracle watch/control is positively armed.
