# Next work unit: M5 arbitrary host-side exact route-field ownership

HYPOTHESIS-ID: m5-host-exact-route-field-ownership

Instrument the remaining runtime/host RDRAM write paths for exact physical
fields `0x128C92` and `0x128CD0..0x128CD4`, then run one qualified real/silent
pair with the oracle exact-watch control retained. Do not alter `0x800078EC`.
The generated scalar/non-literal and RSP-DMA classes are closed at s3744.

Competing hypotheses:

- `H-HostExactWriter`: a runtime/host-side writer supplies the exact fields in the port but is outside guest stores and RSP DMA.
- `H-ExactFieldUnwritten`: no remaining host writer exists before source DMA, so the port route state is an absent producer.
- `H-RouteStateNotSource`: the exact fields are control metadata and the image source is produced by a separate unjoined object.

Discriminator: a host-side exact-field write with a nonzero payload before a
zero source-DMA row selects `H-HostExactWriter`; no host exact-field write in a
qualified target phase selects `H-ExactFieldUnwritten`; matching route
metadata with no exact-field/source join selects `H-RouteStateNotSource`.
Missing oracle control, positive port control, or either port target phase is
unevaluable.

Ground truth must be checked before building: retain the oracle whole-RDRAM
control, exact physical watches, title/hangar phase buckets, and writer-PC
histogram. Batch all host write hooks in one build and one qualified pair.
