# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); audio inventory
and the incremental de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 3749 (2026-10-02).

## Current state

The native port boots through attribution, N64 logo, intro cinematic, star
flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar VI 512
(`0x006AB400`) on the validated real-audio/LLE/spin-yield/autopilot route.
Hangar geometry and color artifacts remain. The real Factor 5 image task is
the qualified audio arm; `ROGUESQ_AUDIO_UCODE=0` selects the silent `Broke`
control. Audio is not production-complete.

The latest independent retail/port boundary is source payload, not rendering:
retail title snapshots contain nonzero bytes in both source subranges (105/256
and 168/408), while hangar snapshots are zero (the exact FNV values are in
the evidence note). The qualified real-port source-DMA joins remain zero
(`FNV=0x762B22A5`) in the same measured span. The port's expected source
descriptor is `0x1798B0 -> DMEM 0xCB0`; its final observed writer is the
legitimate zero-valued `0x800078EC` fill before the image DMA. Exact retail
byte positions are now exported, but layout parity is still not testable at a
zero-valued port payload. See
[M5-S3736-EXACT-RETAIL-BYTE-JOIN.md](M5-S3736-EXACT-RETAIL-BYTE-JOIN.md).

## Next steps

Work only the first applicable item. This is one monotonic backlog.

1. **M5 route-state interpretation.** s3748's macOS ARM64 native page-fault
   watch fired its positive control in both qualified port arms, reached title
   and hangar, and saw no exact-field host write at `0x128C92` or
   `0x128CD0..0x128CD3`. The arbitrary host-writer class is closed for that
   capture. Resolve `H-RouteStateNotSource`: determine whether the exact fields
   are control metadata rather than the image source, using a phase-scoped
   read/use-to-source-DMA join. Do not alter `0x800078EC`. See
   [M5-S3748-HOST-WRITER-FAULT-WATCH.md](M5-S3748-HOST-WRITER-FAULT-WATCH.md).
2. **M3 parked audit — `rs_zcfree` incoming `$a0` at `0x80005268`.** Only
   start if M5 is unavailable or closed. Audit the complete idiom class,
   identify the writer and legitimacy, and land a guard only for a concrete
   invalid writer. Closed `rs_free` audits are archived in PROJECT-OVERVIEW §56.
3. **Generated-symbol renaming sweep.** Only after M5 is closed and M3 has no
   new discriminator. Keep the campaign slug
   `generated-symbol-renaming-sweep` and work one bounded region per session.

## Live hypothesis table

| Hypothesis | Status |
|---|---|
| `H-RetailOnlyProducer` | Selected at s3737 for the measured hangar source boundary; retail exact positions/FNV and writer-family join are now exported. |
| `H-RetailWriterEarlier` | Selected at s3737: retail title source bytes have earlier writer PCs absent from the qualified port source path. |
| `H-PortEarlierWriterAbsent` | Selected at s3738 for the measured scalar-store class: title has only legitimate zero-fill `0x800078EC`; hangar has no target-span scalar store. |
| `H-PortWriterUnlogged` | Refuted at s3738 for the generated scalar-store witness; its positive control fired and no other target-span writer appeared. |
| `H-PortWriterLegitimateClear` | Refuted at s3738 for the measured port span: no nonzero port store preceded the zero DMA payload. |
| `H-PortFamilyNeverEntered` | Refuted at s3739 for the measured family-entry hook: both families execute in the port. |
| `H-PortFamilyEnteredWrongArgs` | Refined at s3739: families touch the target span, but value/setup provenance remains open. |
| `H-FamilyCallEdgeDropsValue` | Refuted at s3740 for the measured call/entry edges: caller and entry arguments matched in both arms. |
| `H-FamilyValueSetupAbsent` | Refuted for the measured candidate setup families; the missing qualified-route edge is elsewhere or parallel. |
| `H-RouteHandoffValueAbsent` | Selected at s3741 for the measured route edge: route-preparation source fields and the `0x8000C628` handoff value fields were zero in title and hangar, followed by zero source DMA. |
| `H-RouteHandoffDropsValue` | Refuted at s3741 for the measured edge: no nonzero predecessor value was observed before the zero handoff. |
| `H-RouteHandoffAfterClear` | Refuted at s3741 for the measured edge: the handoff was already zero before the zero source DMA; no later-clear ordering was shown. |
| `H-EarlierWriterAbsent` | Selected at s3742 for the measured scalar-store class: 512 target-phase rows per arm were all zero-valued neighboring writes, with no nonzero exact-field writer. |
| `H-EarlierWriterClears` | Refuted at s3742 for the measured scalar-store class: no earlier nonzero writer was observed before the zero route state. |
| `H-RouteStateNotSource` | Open after s3742: exact route fields had no scalar writer, so an uninstrumented/non-scalar producer versus control metadata remains unresolved. |
| `H-ExactFieldUnwritten` | Selected at s3743 for generated scalar stores using literal `+0x22/+0x60`: oracle and qualified real/silent port arms had zero exact-field rows in title/hangar. |
| `H-ExactFieldNonScalar` | Refined at s3744: generated non-literal stores and RSP DMA had no exact rows; arbitrary host-side writes remain open. |
| `H-HostExactWriter` | Selected only for transient/unattributed activity after s3745: the 1 ms poll saw no persistent exact-field change, but has no writer-PC attribution. |
| `H-ExactFieldUnwritten` | Selected at s3746 for the censused central host-write APIs; no target-phase exact rows appeared after every invoked API passed its control. |
| `H-HostTransient` | Refuted at s3746 for PI ROM, PI SRAM, zmemcpy, and RSP DMEM-to-RDRAM host writes; arbitrary direct host pointer writes remain open. |
| `H-HostLiteralDirectWriter` | Refuted at s3747 by a 61-file source census: target literals occur only in diagnostics, not production host writers. Computed-pointer/generic-macro ownership remains open. |
| `H-HostExactWriter` | Refuted at s3748 for the qualified port capture: native macOS ARM64 page-fault control fired in both arms, but no phase-gated exact-field host fault occurred. |
| `H-ExactFieldUnwritten` | Selected at s3748 for the remaining arbitrary native host-write class; route-state/source interpretation remains open. |
| `H-PortFamilyWritesThenClear` | Refuted at s3739 for the qualified hangar source path: all real source-range writer payloads remained zero. |
| `H-PortSourceClearOrdering` | Selected at s3731 across `0x1797B0..0x179A48`; target-phase stores and later payloads were zero under the known fill. |
| `H-UninstrumentedPortProducer` | Refuted at s3731 for the full measured span. |
| `H-SourceLayoutMismatch` | Still unevaluable as a parity claim: the port payload is zero, although both source descriptors are aligned. |
| `H-ImageProducerZero` | Selected at s3728 for 1,804 joined hangar image rows. |
| `H-GuestContractDownstream` | Open: port callback ownership is split, but retail host-side parity and exact payload contract remain unjoined. |
| `H-AudioDrainNotConsumed` | Open after s3715; queue state is not directly joined to image-stage consumption. |
| `H-RetailHostCallbackParity` | Open; the oracle exposes guest execution/writes, not host callback/thread ownership. |
| `H-DMEMProducerAbsent` | Closed at s3699: the apparent gap was an RDRAM-to-DMEM DMA writer. |
| `H-ClearTooEarly` | Selected at s3706 for the measured source object; this is an explanation of the observed zero payload, not permission for a mitigation. |

## Evidence ledger — live boundary only

- **3736 — exact retail byte join:** the oracle exported exact phase-gated
  byte positions and FNV for both source subranges. Retail title was
  nonzero (105/256 and 168/408); retail hangar was zero (256/256 and 408/408
  zero). The same-iteration real and silent port arms reached both phases;
  real source-DMA payload remained zero. This closes the export gap and keeps
  the boundary at the retail-versus-port writer family, not layout.
- **3734 — prior retail/port byte-layout join:** retail target-phase samples
  were nonzero in both source subranges; 1,819 qualified real-port joins had
  zero source-DMEM/output/destination payloads. Session 3736 added the exact
  retail positions/FNV that were missing here.
- **3737 — retail writer-family join:** after rebuilding a stale executable,
  the oracle again passed controls and reached both target phases. Retail
  title source bytes were written by `0x80007670`/`0x8001E2C0` families before
  the later `0x800078EC` clear; the real port reached hangar but its 512
  source writer rows and 4,082 image joins were all zero-valued. The silent
  arm emitted no source/image rows. This selects `H-RetailWriterEarlier` and
  moves the boundary to a port-side all-store census. See
  [M5-S3737-RETAIL-WRITER-FAMILY-JOIN.md](M5-S3737-RETAIL-WRITER-FAMILY-JOIN.md).
- **3738 — phase-scoped port writer census:** the oracle positive control and
  both target phases fired. The real port arm recorded 664 title-span scalar
  stores, all zero-valued `0x800078EC` byte stores, and no target-span scalar
  store after the hangar gate; silent emitted no source-DMA rows. This selects
  `H-PortEarlierWriterAbsent` for the measured scalar-store class and names
  `0x800078EC` as a legitimate zero-fill writer, not a mitigation target. See
  [M5-S3738-PORT-WRITER-CENSUS.md](M5-S3738-PORT-WRITER-CENSUS.md).
- **3739 — port family entry/setup census:** both `0x80007670` and
  `0x8001E2C0` executed and touched the measured source span, but the entries
  were shared pre-route setup and the qualified real source writer still had
  512 zero-payload rows. This refutes missing family entry and a nonzero
  family-write-then-clear path; value/setup provenance remains the boundary.
  See [M5-S3739-PORT-ENTRY-SETUP-CENSUS.md](M5-S3739-PORT-ENTRY-SETUP-CENSUS.md).
- **3740 — family value/call-edge provenance:** the fixed phase-scoped capture
  passed the oracle control and both phases. Real and silent arms had matching
  nonzero `rs_strncpy` caller/entry arguments in setup buffers; the texture-LUT
  family also matched at title setup. Neither candidate reached the qualified
  source span. Real still had 512 zero-payload source writes; silent had none.
  This refutes a call-edge value drop for the measured families and moves the
  boundary to the qualified-route predecessor/handoff. See
  [M5-S3740-FAMILY-VALUE-PROVENANCE.md](M5-S3740-FAMILY-VALUE-PROVENANCE.md).
- **3741 — qualified-route predecessor/handoff census:** the fixed oracle
  passed its whole-RDRAM control and reached title and hangar. In both target
  phases, route preparation at `0x80019CD8` had zero source fields and the
  `0x8000C628` handoff had zero value arguments. The real arm then emitted 512
  zero source-DMA rows; silent emitted none. This selects absent value at the
  measured handoff and rules out a nonzero-to-zero drop or later clear there.
  See [M5-S3741-ROUTE-HANDOFF-CENSUS.md](M5-S3741-ROUTE-HANDOFF-CENSUS.md).
- **3742 — all-generated-store route writer census:** the independent oracle
  passed its whole-RDRAM control and its title route-PC watch. The real and
  silent port arms both passed the writer-hook control and reached title and
  hangar. Their 512 target-phase route-span rows were all zero-valued writes
  from `0x8001A06C/74` and `0x8001C21C/24` to neighboring fields; no nonzero
  exact-field writer appeared. This selects absent earlier writer for the
  measured scalar-store class, while leaving non-scalar ownership versus
  metadata open. See [M5-S3742-ROUTE-VALUE-WRITER-CENSUS.md](M5-S3742-ROUTE-VALUE-WRITER-CENSUS.md).
- **3743 — exact route-field ownership:** the oracle control and both target
  phases fired; exact physical watches had no target-phase writes. A 379-site
  generated `+0x22/+0x60` witness passed controls in both arms; the qualified
  real-alone run reached title/hangar and had zero exact rows beside 512
  neighboring zero rows. This selects absent writer for that scalar class and
  leaves non-scalar/host ownership open. See
  [M5-S3743-EXACT-ROUTE-FIELD-OWNERSHIP.md](M5-S3743-EXACT-ROUTE-FIELD-OWNERSHIP.md).
- **3744 — non-scalar/DMA exact-route census:** retail passed the whole-RDRAM
  control and reached title/hangar; `0x128C92` had no writes and
  `0x128CD0..D3` had five writes from `0x8001BB14`. The qualified port passed
  both controls and both target phases; generated scalar/non-literal stores
  and RSP DMA had zero exact rows, while 512 neighboring rows were legitimate
  zero stores. Arbitrary host-side writes remain open. See
  [M5-S3744-NONSCALAR-HOST-EXACT-ROUTE.md](M5-S3744-NONSCALAR-HOST-EXACT-ROUTE.md).
- **3745 — host-side exact-route poll:** both qualified port arms passed
  controls and reached title/hangar. The portable 1 ms poll saw one initial
  exact snapshot and no later field transition in either arm; its B50 live
  RDRAM control fired five times per arm. Generated scalar/non-literal and
  RSP-DMA exact rows stayed zero. This selects the persistent-write null but
  leaves transient write-and-clear and writer-PC attribution open. See
  [M5-S3745-HOST-EXACT-ROUTE-POLL.md](M5-S3745-HOST-EXACT-ROUTE-POLL.md).
- **3746 — central host-write API census:** retail's whole-RDRAM control fired
  10,010 times and its exact-field watch found five early writes to
  `0x128CD0..D3` from `0x8001BB14`, but none to `0x128C92`. The port census
  passed per-API controls for PI ROM, RSP DMA, PI SRAM, and zmemcpy in the
  qualified silent arm and found zero target-phase exact rows; the qualified
  real arm likewise found zero. This selects absent writer for the censused
  host API class while leaving arbitrary direct host writes and
  `H-RouteStateNotSource` open. See
  [M5-S3746-HOST-WRITE-API-CENSUS.md](M5-S3746-HOST-WRITE-API-CENSUS.md).
- **3747 — remaining host RDRAM source census:** a repeatable 61-file scan
  found 11 target-literal occurrences, all in existing diagnostics, and no
  literal-target production host writer. Direct `rdram[...] =` sites were
  diagnostic fill markers; generic `MEM_*` writers are the already-censused
  APIs or runtime setup paths. This refutes only the literal-direct-writer
  class; it does not provide writer-PC attribution for computed pointers or
  external libraries. See
  [M5-S3747-HOST-RDRAM-WRITE-CENSUS.md](M5-S3747-HOST-RDRAM-WRITE-CENSUS.md).
- **3748 — native host writer-PC watch:** a single macOS ARM64 build added an
  `mprotect` watch for the exact route fields. Real and silent port arms both
  reached title/hangar and both fired the native page-fault positive control;
  neither produced an exact-field fault row. Retail independently passed the
  whole-RDRAM control, reached both phases, and observed the known
  `0x128CD0` guest write from `0x8001BB14`. This closes the remaining
  arbitrary native host-writer class for the qualified port capture while
  leaving route-state-versus-source interpretation open. See
  [M5-S3748-HOST-WRITER-FAULT-WATCH.md](M5-S3748-HOST-WRITER-FAULT-WATCH.md).
- **3733 — retail source payload:** both retail target halves were nonzero;
  the full writer census named `0x80007670`, `0x8001E2C0`, and `0x8001F...`.
  The candidate port output watch had no target samples.
- **3732 — port image boundary:** a fixed real-audio capture reached title and
  hangar and fired controls; 1,903 sampled phase-5 joins had zero source-DMEM,
  output, and destination payloads. A prior paired capture was invalid, not
  evidence.
- **3731 — full-span producer census:** 78 nonzero stores occurred before the
  target route, but all 280 target-phase extension rows and later source
  payloads were zero; the known `0x800078EC` fill remained final.
- **3730 — source-layout join:** 512 source-range rows and 2,456 image-DMA
  joins used the expected descriptor; source, output, and post-write payloads
  were zero. Retail independently retained nonzero source content.
- **3728 — image payload:** 1,804 joined hangar rows had zero stage-3 source
  DMEM/output; 268 PCM consumers were also zero. This refuted a writeback or
  consumer gap at the qualified port boundary.
- **3725/3727 — route qualification:** paired real/silent arms reached both
  target phases and passed controls; only real audio produced image/source/DMA
  and image-stage rows. Silent remains the same-build control.
- **3690–3708 — source ownership and clear boundary:** input identity was
  earlier/equal, input/source/DMEM payloads matched, the expected source range
  was used, and the same `0x801797B0`/`0x298` object was legitimately cleared
  before later zero DMAs. These results move the boundary upstream; they do
  not authorize a clear suppression.

Detailed notes remain in the linked `M5-S37xx-*.md` files and the append-only
ledger. Do not repeat a boundary whose discriminator is already closed.

Session 3749 did not produce route-state evidence. A broad generated-load
transformer was abandoned after nested `S32(...)` expressions caused an
unterminated macro invocation; the regeneration recovery pass also stopped at
the existing `s3556 entry anchor count=0` fixup gate. Treat the route-state
read/use question as unevaluable, with no runtime conclusion.

## Durable operating rules

Factor 5 uses [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. Interpreter
limits, null-GBI guards, and similar defenses are safety mechanisms, not
explanations. Overlay dispatch is sufficient for the validated route.

MusyX/MORT audio remains partially stubbed. MusyX task data cannot be sent to
stock `aspMain`; the silent arm returns `Broke`. Never infer audio behavior
from a route that fails to reach the target phase.

Every instrument needs an independent ground-truth request, a same-run
positive control, a phase-scoped budget, and two evidence lines before its
result becomes current truth. Phase-gate animated comparisons on VI
transitions. Batch A/B arms in one build/run. A counter proving a branch ran
is not a positive control.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
CMake`. Never hand-edit generated functions for behavior changes. If `lib/`
changes, run `./submodule-patches/export.sh` and commit refreshed patches.
Never run submodule update, checkout, clean, or hard reset commands. Kill runs
with SIGKILL and run from `build/`. A mitigation-shaped change needs an
`ORIGIN:` line naming the writer and stating whether its value is legitimate.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed.

The s3579–s3584 retail-versus-port stored-value inference at `0x800078EC` is
unsupported: retail executes a byte store while the oracle had read an
aligned word containing neighboring bytes. Scalar samples measured zero
bytes with zero mismatches.

The request-only SP-yield/viewer-stall chain describes only the old diagnostic
arm. The old interpretation of the cinematic pool as an audio-slot pool was
superseded by the MusyX voice-table measurement. The claim that `0x8002BEEC`
is the retail JAL dispatch to `0x800078EC` remains route-dependent and
unreconciled.

## Evidence index

- [M5-S3734-RETAIL-PORT-BYTE-LAYOUT-JOIN.md](M5-S3734-RETAIL-PORT-BYTE-LAYOUT-JOIN.md)
- [M5-S3741-ROUTE-HANDOFF-CENSUS.md](M5-S3741-ROUTE-HANDOFF-CENSUS.md)
- [M5-S3743-EXACT-ROUTE-FIELD-OWNERSHIP.md](M5-S3743-EXACT-ROUTE-FIELD-OWNERSHIP.md)
- [M5-S3745-HOST-EXACT-ROUTE-POLL.md](M5-S3745-HOST-EXACT-ROUTE-POLL.md)
- [M5-S3746-HOST-WRITE-API-CENSUS.md](M5-S3746-HOST-WRITE-API-CENSUS.md)
- [M5-S3736-EXACT-RETAIL-BYTE-JOIN.md](M5-S3736-EXACT-RETAIL-BYTE-JOIN.md)
- [M5-S3733-RETAIL-SOURCE-PAYLOAD.md](M5-S3733-RETAIL-SOURCE-PAYLOAD.md)
- [M5-S3732-IMAGE-PAYLOAD-BOUNDARY.md](M5-S3732-IMAGE-PAYLOAD-BOUNDARY.md)
- [M5-S3731-FULL-SPAN-PRODUCER.md](M5-S3731-FULL-SPAN-PRODUCER.md)
- [M5-S3730-SOURCE-LAYOUT-JOIN.md](M5-S3730-SOURCE-LAYOUT-JOIN.md)
- [M5-S3728-IMAGE-PAYLOAD-BOUNDARY.md](M5-S3728-IMAGE-PAYLOAD-BOUNDARY.md)
- [M5-S3725-STEP1-CONTROL-VALID.md](M5-S3725-STEP1-CONTROL-VALID.md)
- [M5-S3699-DMEM-DMA-COVERAGE.md](M5-S3699-DMEM-DMA-COVERAGE.md)
- [M5-S3706-WRITER-SETUP-REQUALIFICATION.md](M5-S3706-WRITER-SETUP-REQUALIFICATION.md)
- [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md)

Sessions 1–3746 remain in the append-only ledger. Use bounded `grep`/`sed`
windows for `PORTING-STATE.md`, never read it whole.
