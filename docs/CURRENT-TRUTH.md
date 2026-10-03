# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); audio inventory
and the incremental de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 3740 (2026-10-02).

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

1. **M5 qualified-route predecessor/handoff census.** s3740 showed the
   candidate `0x80007640` and `0x8001E230` call/entry arguments match and are
   shared setup activity in real and silent arms; neither is the missing
   qualified-route producer. Join the first real-audio route edge after this
   setup to its task/RSP handoff and source-DMA row. Keep the legitimate
   `0x800078EC` fill unchanged. See
   [M5-S3740-FAMILY-VALUE-PROVENANCE.md](M5-S3740-FAMILY-VALUE-PROVENANCE.md).
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

Sessions 1–3737 remain in the append-only ledger. Use bounded `grep`/`sed`
windows for `PORTING-STATE.md`, never read it whole.
