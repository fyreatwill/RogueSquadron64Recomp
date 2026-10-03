# Next work unit: M5 platform-native writer-PC watch

HYPOTHESIS-ID: m5-host-exact-route-field-ownership

Resolve the remaining computed-pointer/external-host-write gap for exact
physical fields `0x128C92` and `0x128CD0..0x128CD4` with a platform-native
writer-PC watch, then run one qualified real/silent pair. Do not alter
`0x800078EC`. The generated scalar/non-literal, RSP-DMA, persistent-poll,
central-host-API, and literal-direct-host-writer classes are closed at s3747.

Competing hypotheses:

- `H-HostExactWriter`: a runtime/host-side writer supplies the exact fields in the port but is outside guest stores, literal direct writes, and the censused host APIs.
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
histogram. The direct-source census is now complete; do not repeat it. Batch
all remaining host-write hooks in one build and one qualified pair. If the
current platform cannot support a writer-PC watch, record that concrete
capability failure and stop rather than adding another field-only diagnostic.

Exact preflight/build/run shape: `uname -a`; inspect the platform-native
write-watch capability, then build one instrumented executable and run the
oracle control plus real/silent port arms concurrently from `build/`, killing
all arms with SIGKILL. Expected outcomes are a nonzero exact-field write with
writer PC (selects `H-HostTransient`), no exact-field write after live controls
(selects `H-ExactFieldUnwritten` for the remaining class), or matching route
metadata without an exact-field/source join (selects `H-RouteStateNotSource`).
