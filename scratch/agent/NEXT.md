# Next work unit: M5 arbitrary host-side exact route-field ownership

HYPOTHESIS-ID: m5-host-exact-route-field-ownership

Resolve the remaining arbitrary-direct-host-write gap for exact physical fields
`0x128C92` and `0x128CD0..0x128CD4` with a platform-native writer-PC watch or
a census of direct host pointer writes outside the completed PI/RSP/zmemcpy
API surfaces, then run one qualified real/silent pair. Do not alter
`0x800078EC`. The generated scalar/non-literal, RSP-DMA, persistent-poll, and
central-host-API classes are closed at s3746.

Competing hypotheses:

- `H-HostExactWriter`: a runtime/host-side writer supplies the exact fields in the port but is outside guest stores and the censused host APIs.
- `H-ExactFieldUnwritten`: no remaining host writer exists before source DMA, so the port route state is an absent producer.
- `H-RouteStateNotSource`: the exact fields are control metadata and the image source is produced by a separate unjoined object.
- `H-HostTransient`: an arbitrary direct host write changes and clears an exact
  field between samples, so only a writer-PC-capable watch can see it.

Discriminator: a host-side exact-field write with a nonzero payload and a
writer PC before a zero source-DMA row selects `H-HostTransient`; no host exact
write in a qualified target phase selects `H-ExactFieldUnwritten`; matching
route metadata with no exact-field/source join selects `H-RouteStateNotSource`.
Missing oracle control, positive port control, or either port target phase is
unevaluable.

Ground truth must be checked before building: retain the oracle whole-RDRAM
control, exact physical watches, title/hangar phase buckets, and writer-PC
histogram. Prefer a platform-native writer-PC watch; if unavailable, inventory
every remaining direct host-to-RDRAM pointer write in one bounded change.
Batch all remaining host-write hooks in one build and one qualified pair.
