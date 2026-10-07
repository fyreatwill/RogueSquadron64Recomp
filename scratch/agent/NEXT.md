# Next work unit: pre-clear producer provenance

HYPOTHESIS-ID: m5-pre-clear-producer-provenance

Determine whether retail's nonzero source-span writer before the legitimate
`0x800078EC` clear is absent from the port or is present and subsequently
overwritten.

Competing hypotheses and discriminator:

- H-port-preclear-absent: the retail writer-PC histogram has nonzero stores
  before `0x800078EC`, while the same phase-gated port writer census has no
  corresponding nonzero source-span writer. This proves a missing port-side
  producer boundary.
- H-port-preclear-overwritten: the port has a nonzero source-span writer
  before its clear, but the later zero clear overwrites it. Matching writer
  order and a nonzero pre-clear port sample select this explanation.
- H-route-invalid: either arm lacks the whole-RDRAM control or a target phase;
  no provenance conclusion is valid.

Exact work: adapt the existing source-span writer-census recipe to watch the
same aligned source range and scalar post-store values in one rebuilt port /
retail pair. Use `--pc-hist-phase` and `--post-value-watch`/`--post-store-
scalar` for the retail arm, and the existing phase-scoped port source-span
writer rows. Run from `build/` for at least 75 seconds with the fixed
two-second launch stagger if needed; kill both processes with SIGKILL. Retain
the whole-RDRAM positive control and title `0x00790400/1024` plus hangar
`0x006AB400/512` phase gates. Do not change guest, audio, wait, cap,
predicate, slot, or writeback behavior.

Expected outcomes: nonzero retail writers with no port counterpart selects
H-port-preclear-absent; a nonzero port writer followed by the known clear
selects H-port-preclear-overwritten; missing controls/phases selects
H-route-invalid.
