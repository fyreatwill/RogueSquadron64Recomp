# Next work unit: M5 transient host-side exact route-field ownership

HYPOTHESIS-ID: m5-host-exact-route-field-ownership

Resolve the remaining transient-write gap for exact physical fields `0x128C92`
and `0x128CD0..0x128CD4` with one writer-PC-capable host watch or a complete
central host-write API census, then run one qualified real/silent pair. Do not
alter `0x800078EC`. The generated scalar/non-literal, RSP-DMA, and persistent
1 ms poll classes are closed at s3745.

Competing hypotheses:

- `H-HostExactWriter`: a runtime/host-side writer supplies the exact fields in the port but is outside guest stores and RSP DMA.
- `H-ExactFieldUnwritten`: no remaining host writer exists before source DMA, so the port route state is an absent producer.
- `H-RouteStateNotSource`: the exact fields are control metadata and the image source is produced by a separate unjoined object.
- `H-HostTransient`: a host write changes and clears an exact field between
  1 ms samples, so only a writer-PC-capable watch can see it.

Discriminator: a host-side exact-field write with a nonzero payload and a
writer PC before a zero source-DMA row selects `H-HostTransient`; no host exact
write in a qualified target phase selects `H-ExactFieldUnwritten`; matching
route metadata with no exact-field/source join selects `H-RouteStateNotSource`.
Missing oracle control, positive port control, or either port target phase is
unevaluable.

Ground truth must be checked before building: retain the oracle whole-RDRAM
control, exact physical watches, title/hangar phase buckets, and writer-PC
histogram. Prefer a platform-native writer-PC watch; if unavailable, inventory
every central host-to-RDRAM write API in one bounded change. Batch all host
write hooks in one build and one qualified pair.
