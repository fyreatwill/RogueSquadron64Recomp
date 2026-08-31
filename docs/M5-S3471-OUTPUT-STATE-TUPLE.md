# M5 Session 3471 — qualified output/state tuple divergence

The independent Rice-oracle preflight used the same title route and the
whole-RDRAM positive control. The control recorded 29,630 writes, title origin
`0x00790400` was reached, and the four field watches produced 659/763/763/654
unique rows at `0x80001C98`/`0x80001CB8`/`0x80001CC8`/`0x80001F84`.

The configured port build emitted the regeneration-safe four-PC witness after
the title phase control fired. It produced 514/510/510/514 rows respectively,
2,048 rows total, and the schema positive-control line appeared once. The run
had no `CRASH` or `ABORT` marker.

The first qualified consumer tuple is materially different: the port has
`s1=0x80110000`, `source_word=0xFF5555FF`, and `branch_state=0`, while the
retail field table includes the qualified state tuple
`s1=0x801B1590`, `source_word=0x00000008`, and `branch_state=0` at
`0x80001CB8`. Retail also has varied `s1`/source tuples. This selects an
upstream producer/state-field divergence before the downstream output call;
the output-contract hypothesis is not yet selected.

This is two-source evidence for the field divergence, but not yet an exact
writer attribution: the retail rows are unique-field rows with no shared
invocation ordinal, and the port witness's ordinal is a per-run emission
counter. No runtime behavior or mitigation changed.
