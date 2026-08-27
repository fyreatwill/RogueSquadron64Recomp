# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history belongs in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact
commands, counts, and probe rows remain in the ledger and scratch artifacts.

Current maintenance marker: Session 2690 (2026-08-27).

## Live result

The qualified port route is `ROGUESQ_LLE_FORCE=1`,
`ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`; `ROGUESQ_SPIN_YIELD=1`
is diagnostic. `ROGUESQ_AUTOPILOT` is the reliable in-process driver.

M5 defaults to the Factor 5 image arm. `ROGUESQ_AUDIO_UCODE=0` selects the
silent `musyx_stub` control. Stock `aspMain` is not the retail contract;
MORT is a separate CPU speech boundary.

The latest qualified M5 evidence is:

- s2671 separated image work from the silent control in the same qualified
  driver: image DMEM/DMA/completion rows were live, while the silent arm had
  no image rows. Both arms retained zero task output fields and zero PCM
  source/consumer payloads in that capture (`H-contract-separated`).
- s2672–s2673 found image-stage and ring destinations but no complete writer,
  legitimate payload, and ordering edge. Retail attribution did not close
  the edge (`H-ring-unmapped`, `H-unmapped-edge`).
- s2675–s2676 audited the live CPU MORT boundary. `0x8009D740` executes from
  `0x8009D73C`; its source-derived 40-byte output at physical
  `0x11C7B0:0x11C7D8` is shared stack storage, with unrelated stack writers
  also present. This strengthens `H-MORT-unmapped` and forbids writeback or
  remap from that overlap. `H-image-edge` remains unproven.
- s2678's corrected retail oracle established the next CPU edge: retail
  `applyVoiceDelayFilter` writes persistent voice object `0x80153420+0x166`
  (physical `0x153586`) from `0x8009D8E4`, and `renderVoiceAudioBlock`
  (`0x8009DB44`, caller `0x8009C4C0`) consumes the same object in both hangar
  origins. The whole-RDRAM control fired 17,295 times; the phase-gated counts
  were 792 filter, 792 delay, and 198 render executions. This resolves the
  CPU-side consumer edge but not renderer-to-PCM/AI publication; no writeback
  or remap follows from it.
- s2679's batched retail capture reached title and both driven hangar origins
  with the whole-RDRAM control (`29,161` writes). `renderVoiceAudioBlock`
  executed 496 times, `audioMixStereoBlock8` 1,984 times, and
  `osAiSetNextBuffer`/`__osAiDeviceBusy` 6,180 times. The candidate port ring
  `0x166450:0x169450` was written 12,288 times, but every sampled writer was
  `rs_memset` at `0x800078EC`, including boot initialization; the capture did
  not join renderer/mixer output to that ring or another AI source. This
  strengthens `H-MORT-unmapped` at the CPU publication boundary and does not
  select `H-image-edge`.
- s2680's same-build AUTOPILOT re-baseline reached title and hangar in both
  port arms. The image arm alone produced 4,764 DMA-range rows and 14,328
  image-stage rows, with task `break_pc=0x1328`; the silent arm produced none.
  Both arms nevertheless had matching task dispatch/return, audio/SP route,
  PCM source/consumer counts (`98/98`) and zero-nonzero PCM payloads
  (`fnv=F59C39C5`, `nz=0`). This selects `H-ContractGap` at the measured
  downstream boundary, rejects `H-RouteOnly` and `H-AudioDegeneracy` there,
  and does not identify a legitimate writer or authorize writeback/remap.
- s2681's positive-controlled retail join reached both hangar origins and kept
  the named renderer/mixer/AI PCs live. The candidate AI-source span
  `0x166450:0x169450` had 3,072 reads but only the known initialization writer
  `0x800078EC`; the adjacent span `0x1B4A00:0x1B5000` had phase-live nonzero
  renderer writes at `0x8009DB2C`. The renderer was not joined to the AI
  source, selecting `H-AI-source-gap` for these candidate ranges (single-source
  retail evidence) and rejecting `H-MORT-PCM` there. The complete publication
  edge remains open; no writeback or remap is authorized.
- s2682's static audit separated the apparent address pair. `0x8009DB2C` is
  the final halfword store in `runVoiceLatticeFilter` (`0x8009D980`), writing
  caller-provided `a2 + 2*i` across four fixed renderer stages. `0x8002A0B8`
  and `0x8002A0D8` are loop-body stores in generic `bzero` (`0x8002A080`),
  used for voice-slot, ring-buffer, and stack-temporary clearing. Neither
  identifies an AI publication writer or destination; this selects
  `H-unresolved-address` for the proposed join and forbids a runtime watch or
  writeback based on these sites.
- s2683's static pointer audit recovered the service contract: named
  `dmaVoiceSampleAndSignal` transfers stream input from
  `slot+0x194+offset` into slot storage at `slot+0x1A0+aligned-offset` and
  signals the slot queue. `consumeVoiceSamples` only advances slot cursors;
  `updateVoiceChannelParams` consumes caller-provided filter/delay arrays;
  and `renderVoiceAudioBlock` keeps mixed output in the voice object at
  `+0x140`/stage offsets. No audited path joins that output to the AI-source
  span or names an ordered publication copy, selecting `H-unresolved-address`
  and keeping runtime watches, writeback, and remap unauthorized.

Retail is the independent witness for game-side memory claims. A narrow null
is unevaluable unless the whole-RDRAM positive control fires first and the
target phase is reached. The current corrected oracle reaches attract, title
(`1024 @ 0x00790400`), and hangar (`512 @ 0x006AB400`), not a mission.

s2684's generated-symbol sweep found only two remaining true `func_`
placeholders in the generated snapshot (`0x8000040C` and `0x800927B0`), and
the companion map intentionally leaves both address-named. The tracked rename
tool now accepts a bounded sibling-symbol batch, applies only exact semantic
matches, and rejects duplicate destinations; this run preserved both
ambiguous names rather than inventing identities.

s2685 reran the bounded companion-driven batch after making its membership
check linear in the generated placeholder set. The tool reported zero renamed
references in zero files; both remaining placeholders and all eight known
non-placeholder mappings were already synchronized. The initial unoptimized
invocation exceeded the practical run window while repeatedly rescanning the
snapshot, then the fixed version completed successfully. This closes the
current sweep lead without selecting a rename; future regeneration may expose
new exact matches.

s2686 completed the prescribed static M5 caller/consumer audit. The normal
`updateVoiceChannelParams` path and both loops in the large path pass
stack-built filter and delay arrays to `filterVoiceSampleBlock` and
`applyVoiceDelayFilter`; those helpers write only the temporary arrays and the
voice object's `+0x166` delay field. The normal path then calls
`renderVoiceAudioBlock` with the same voice object. The renderer reads eight
words from `voice+0x140`, combines them through its internal mix/companding
helpers, and writes eight words back to `voice+0x140`; its indirect calls are
only the eight internal mix-function dispatches. No caller-owned destination,
PCM-source span, AI call, queue signal, or ordered publication copy appears in
this path. This selects `H-unresolved-address` for the audited boundary and
rules out `H-publish-caller` and `H-service-boundary` at these sites (static
source evidence only); no runtime watch, writeback, remap, or mitigation is
authorized.

s2687 audited `initN64RspMixer` and the adjacent callback/state words. The
initializer writes five callback slots: `0x801499D0=0x8001A058`
(`postViThreadCommand`), `0x801499D4=0x8000569C`
(`submitDmaRequestBatch`), `0x801499D8=0x80007910`
(`registerSiCallback`), `0x801499DC=0x8000794C`
(`findAndZeroTableSlotMatching`), and `0x801499E0=0x8000591C`
(`getAssetRamAddress`). The requested `D0..E0` range is five words; the
adjacent `E4..EC` words are not initialized by this routine and are used as
separate audio allocator/list state in generated callers. The named
consumers use `D4` only for the initializer's callback re-arm, `D8` in
`waitForMusyXAudioTaskDone` and `shutdownAudioEngine`, and `E0` in
`relocateSndPointer`; their arguments are scheduler/pointer values, not the
voice object's `+0x140` mixed words. No callback writer, PCM destination,
queue publication, or AI ordering edge is identified. This selects
`H-unresolved-address` for the mixer boundary, rules out `H-mixer-publish`
and `H-service-boundary` at these sites, and remains static source evidence;
no runtime watch, writeback, remap, or mitigation is authorized.

s2688 audited the next downstream boundary. `renderVoiceAudioBlock` is called
from `updateVoiceChannelParams` at `0x8009C4C0`, reads eight words from
`voice+0x140`, and writes the mixed words back to that same object at
`0x8009DC38..0x8009DC54`; no caller-owned PCM destination or publication call
appears after it. `audioMixStereoBlock8` only reads the voice sample fields and
returns packed results in registers to the enclosing renderer. The named AI
worker at `0x8008ED70` independently allocates sixteen `0x300`-byte buffers
within a `0x3000` region, clears them, and submits the base/current buffer to
`osAiSetNextBuffer` with length `0x300`; its only visible post-submit ordering
is the message receive loop. No named writer or direct copy joins that ring to
`voice+0x140`. This selects `H-unresolved-address` for the downstream consumer
table (static source evidence), rules out `H-direct-publish` and
`H-service-boundary` at the audited sites, and authorizes no runtime watch,
writeback, remap, or mitigation.

s2689 audited the named AI-ring producers. `setupSongRenderBuffers` has only
one direct caller, `acquireSampleStreamBlock` (`0x80091944`), and passes the
channel count, source stream pointer, and channel index into setup. It allocates
channel metadata and then calls `buildSongDecodeBufferRing`; that helper
allocates a descriptor array and a separate `count*0x100` byte area, links each
descriptor to successive `0x100` chunks, and initializes descriptor links and
cursors. Neither helper copies sample or rendered-voice payload. The AI worker's
separate `0x3000` allocation at `0x801496B0`, cleared before submission, remains
without a named producer or source relation. The complete producer table
therefore selects `H-unresolved-address`, rules out `H-ring-producer` and
`H-service-boundary` for these helpers/caller, and authorizes no runtime watch,
writeback, remap, or mitigation.

s2690 audited `initSampleStreamBlockCache` and its only direct named caller,
`setupSongRenderBuffers` (`0x8008F2FC`). The caller derives the cache-block
count from the song-rate calculation, calls `buildSongDecodeBufferRing`, then
passes that count to the initializer; it supplies no MORT/rendered payload
pointer. The initializer allocates a `count*0xC00` byte region and a
`count*0x18` descriptor region, invalidates the first allocation, and links
descriptors to successive `0x600` blocks while initializing next/previous
links, sizes, cursors, and list heads. Its only named calls are `rs_malloc` and
`osInvalDCache`; there is no data copy/transform, queue or service signal, AI
call, or source relation. This selects `H-unresolved-address`, rules out
`H-cache-producer` and `H-service-boundary` for this boundary (static source
evidence), and leaves no legitimate writer or destination for a runtime watch,
writeback, remap, or mitigation.

s2691 audited every direct named caller and immediate consumer of
`acquireSampleStreamBlock`. There is one caller, `musyxRenderVoiceSamples`
(`0x800902DC`): it passes the stream/cache pointer at `s1+0x34`, stores the
returned block pointer at `s0+0x40`, later reads that field as a cursor/length
input, and copies `s0+0x40` to `s1+0x40` at `0x80090B68`. The acquire helper
only reaps or links block descriptors, sets state/owner fields, and returns
`node+0x8`; it contains no payload copy or transform, queue/service signal,
AI call, or publication ordering. This selects `H-unresolved-address` for
the acquire boundary and rules out `H-acquire-publisher` and
`H-service-boundary` at the audited sites (static source evidence). No
runtime watch, writeback, remap, or mitigation is authorized.

s2692 implemented the M5 Step 6 runtime change: startup now defaults the
host-injected `ROGUESQ_DRAIN_INLOOP_TICK` to `0` only when unset, while an
explicit `=1` preserves the tick-on rollback/control arm. The Debug target
built successfully. Concurrent same-build tick-off and tick-on probes both
stopped at VI width `640` and timed out before the required title width
`1024`, so the A/B discriminator had no positive phase control and selects no
hypothesis. The change remains unvalidated; no audio or route conclusion is
drawn.

s2693 reran the validation with the in-process AUTOPILOT route after the first
external-key recipe again stalled at VI 640. The retail whole-RDRAM control
passed (`10000` callbacks), with title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400` reached. In the phase-qualified silent-control arms,
tick-off and tick-on each had a clean drain return (`v0=1`, one iteration),
matching voice-filter gate totals (`tickn=5`, `jaln=5`, `exitn=5`), and no
crash/abort. PCM source/consumer rows were live but all sampled payloads had
`nz=0` in both arms. This single-source same-build A/B selects
`H-retail-equivalent` for the exercised drain call: the injected tick was not
needed for route or clean drain return. It does not resolve the MORT-to-PCM
publication edge or prove behavior beyond this call shape.

## Next steps

This is one monotonic sequence; #1 is the next campaign priority.

1. **M5 CPU-side MORT PCM publication.** The renderer-to-AI candidate join
   separates the live renderer span from the AI-source span but does not name
   the missing copy/publication edge. The s2682 audit shows the watched sites
   are a renderer filter output and generic `bzero`, not the missing copy.
   s2683 shows the named DMA callback is stream-to-slot, not renderer-to-AI.
   s2686 found no publication edge in the update/renderer path, s2687 found no
   publication edge in the mixer callback/state boundary, s2688 found no join
   in the named AI worker, s2689 found that the named ring setup helpers only
   allocate/link metadata and zeroed decode storage, and s2690 found the same
   for the cache initializer. The acquire audit found only descriptor
   ownership/cursor propagation. The next useful work must audit named callers
   of `musyxRenderVoiceSamples` and immediate post-call consumers of its
   voice-object fields for a named stream/cache-to-AI publication relation,
   without repeating these initializer, setup, renderer, mixer, or AI-submit
   body audits.
2. **M5 image task contract edge.** Implement only after a named legitimate
   image writer and destination/order relation is independently established;
   s2680 authorizes no writeback or remap.
3. **Generated-symbol renaming sweep — parked pending regenerated matches.**
   Preserve `0x8000040C` and `0x800927B0` until companion/source evidence
   supplies defensible names; do not rename by inferred implementation shape.
4. **M3 crash work — parked.** Resume only as a complete idiom-class audit
   with a named discriminator; passive recurrence belongs in the soak queue.
5. **Hangar visual artifact — parked.** H2 and consumer-mode H1 are refuted;
   H3 is unavailable because the oracle cannot screenshot the LLE path.
6. **M4 accumulator origin — parked.** One phase-6 producer/consumer join is
   established; broader slot coverage is lower priority than M5.

## Durable boundaries

### Route, rendering, and Factor 5

Factor 5 uses custom GBI mappings documented in
[`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md). Do not infer stream
semantics from standard F3DEX. Keep the qualified LLE route and existing
defensive runtime guards until a named writer explains any bad value.

### M5 audio and image output

The Factor 5 image task and CPU MORT speech path are separate contracts. A
`Broke` return proves task completion only, not PCM correctness. A valid
publication edge needs a named writer, destination, legitimate payload
polarity, and ordering through service/slot/MORT, PCM source, PCM consumer,
and image completion where applicable. No writeback, gate bypass, forced
slot state, output remap, or mitigation is authorized without an `ORIGIN:`
line naming the writer and stating whether its value is legitimate.

### Safety and evidence

- Ask the retail oracle for ground truth before adding port instrumentation.
- Batch every discriminator in one build and one phase-gated run; include a
  positive control in the same run.
- Regenerate in order: `make_elf.py`, N64Recomp, fixup scripts, then CMake.
  Never hand-edit generated game functions for behavior changes.
- Kill runs with SIGKILL and run from `build/` with the ROM present.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. If `lib/` changes, export its patches in the same
  iteration.

## Superseded conclusions

The old overlay/menu explanation, intrinsic 640 flakiness, missing-input and
wait-return claims, global-zero image-DMA explanation, route-wide PCM gap,
and force-zero default policy are superseded at their measured scopes. They
were believable before qualified routes, same-build controls, or independent
retail attribution existed. Detailed failed experiments remain in
`PORTING-STATE.md` and the archive below.

Static boundary-only symbol classifications remain non-renames when companion
symbols, source/m2c, callers, and local semantics do not supply a defensible
name. Stable companion duplicate-prefix and preamble mappings belong in
`tools/rename/build_redefs.py`.

## Archived durable progression

The detailed s2621–s2676 results were compacted into
[`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md) during Session 2677. The ledger
retains every exact session entry and scratch artifact. The current decision
chain is: task-field census unresolved; image/silent separation qualified;
image ring/stage destinations not a publication edge; named retail utility
writers not a MORT edge; and the live MORT filter output is shared temporary
stack storage. The next legitimate discriminator is the sample-stream cache
boundary; the named ring setup path is metadata-only.
