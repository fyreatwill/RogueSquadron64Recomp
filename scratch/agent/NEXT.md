# Next work unit: route-qualified pre-clear producer provenance

HYPOTHESIS-ID: m5-pre-clear-producer-provenance

Determine whether retail's nonzero source-span writer before the legitimate
`0x800078EC` clear is absent from the port or is present and subsequently
overwritten. Re-run the same discriminator with the canonical
route-qualified port launch; the s4154 port arm was boot-invalid and emitted
no target-phase rows.

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
retail pair. Use `--pc-hist-phase` and `--post-value-watch` (which emits the
scalar rows) for the retail arm, and the existing phase-scoped port source-span
writer rows. Use the previously qualified canonical real-audio/LLE/ungated/
solo/spin-yield launch and its autopilot; do not add the s4154 two-second
stagger unless the recipe requires it. Run from `build/` for at least 75
seconds; let the oracle flush its summary, then SIGKILL the port. Retain
the whole-RDRAM positive control and title `0x00790400/1024` plus hangar
`0x006AB400/512` phase gates. Do not change guest, audio, wait, cap,
predicate, slot, or writeback behavior.

Expected outcomes: nonzero retail writers with no port counterpart selects
H-port-preclear-absent; a nonzero port writer followed by the known clear
selects H-port-preclear-overwritten; missing controls/phases selects
H-route-invalid.
