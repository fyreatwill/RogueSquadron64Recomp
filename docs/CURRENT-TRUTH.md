# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history belongs in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact
commands, counts, and probe rows remain in the ledger and scratch artifacts.

Current maintenance marker: Session 2718 (2026-08-27).

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

s2694 completed the prescribed static audit of every named direct caller of
`musyxRenderVoiceSamples` and its immediate consumers. There is one direct
caller, `musyxMixActiveVoices` at `0x80090F00`, reached from three
`musyxSynthFrame` loop sites. The render kernel writes through caller-provided
`$a3` into the per-frame output block and mutates voice-local state; after the
call, the caller only advances cursors, clears/sets voice status, and updates
loop bookkeeping. No named payload copy, AI call, queue/service signal, or
ordering edge joins this output to the AI worker's separate `0x801496B0`
allocation. This selects `H-unresolved-address`, rules out
`H-caller-publishes` and `H-service-boundary` for the audited chain (static
source evidence), and authorizes no runtime watch, writeback, remap, or
mitigation.

s2695 completed the post-mix output-block handoff audit. The three
`musyxMixActiveVoices` calls in `musyxSynthFrame` hand the render kernel's
per-frame `$a3` block back only through the mixer, whose post-call work is
cursor/status bookkeeping. Named post-mix consumers are
`flushStreamedVoiceBuffers`, `osRecvMesg`/`yieldFromSpThread`, the indirect
callback at `0x80091684`, `serviceStreamedVoices`, timing, and
`factor5QueueSignal`; none receives or copies the synth output into the AI
worker's `0x801496B0` source. The only concrete copy is
`copyFourHalfwordsWriteback`, a four-halfword descriptor-local streamed-voice
copy followed by cache writeback. This selects `H-consumer-only` for the
named post-mix chain and retains `H-unresolved-address` for the complete
publication edge (static evidence); the unresolved callback is the next
bounded source-read target. No runtime watch, writeback, remap, or mitigation
is authorized. Detailed table: `scratch/agent/s2695_mort_postmix_boundary/audit.md`.

s2717 performed the mandatory M4 revisit after the last 15 ledger titles were
all sweep-scoped. A single retail-oracle run passed the whole-RDRAM control
(`533,653` writes), reached title `1024` and hangar `512`, and added
phase-qualified post-store value samples to the previously grounded
`0x167000:0x169B00` and `0x179800:0x179B00` ranges. The first range was
dominated by pointer-like structured values from `0x80015BC8` (title and
hangar) and `0x8000F3A0` (hangar); the second mixed zeroes and varied small
values across several hangar writers. This selects `H-allocator-churn` for
these broad candidate ranges, retains `H-phase-specific-source` as a
non-merge warning, and does not identify the M4 accumulator source/table
index. No port instrumentation, writeback, remap, or mitigation is
authorized. Detailed table: `scratch/agent/s2717_m4_retail_record/audit.md`.

s2697 completed the named DMA-service consumer audit. `sendServiceMessage`
only resolves a registered worker queue, annotates the message header, and
enqueues the wakeup. `piDmaWorker` ignores that message body, consumes the
20-byte PI ring entries at `0x801112B0`, and passes their device address, DRAM
address, and size unchanged to `osPiStartDma`; completion only marks the ring
entry and signals its return queue. The host PI bridge likewise performs only
generic `do_dma`. No stage reads the synth output block, writes the AI worker's
`0x801496B0` allocation, calls `osAiSetNextBuffer`, or supplies an ordering edge
between them. This selects `H-service-unrelated` and rejects
`H-service-publishes`/`H-service-indirect` for this named path (static source
evidence); the MORT-to-PCM publication edge remains unresolved. No runtime
watch, writeback, remap, or mitigation is authorized. Detailed table:
`scratch/agent/s2697_mort_dma_service_boundary/audit.md`.

s2698 audited the complete host AI boundary. `osAiSetNextBuffer_recomp`
forwards the game RDRAM pointer and byte count unchanged to
`ultramodern::queue_audio_buffer`; the runtime converts that pointer with
`TO_PTR`, derives the sample count, and passes the exact host span plus the
original RDRAM address to the registered callback. The main callback queues
that span directly into SDL with the corrected byte length. No host copy from
another source, RDRAM destination, payload transform, queue drop/defer path,
or completion callback exists; `osAiGetStatus_recomp` reports zero and the
length query only observes SDL queue depth. This selects `H-host-preserves`
and rejects `H-host-remaps`/`H-host-gates` at the named host boundary (static
source evidence). The MORT-to-PCM publication edge remains upstream and
unresolved; no runtime watch, writeback, remap, or mitigation is authorized.
Detailed table: `scratch/agent/s2698_mort_host_ai_boundary/audit.md`.

Detailed table: `scratch/agent/s2698_mort_host_ai_boundary/audit.md`.

s2699 pivoted to the generated-symbol-renaming sweep as the mandated bounded
engineering change. The tracked rename tool previously rejected companion
symbol lines with trailing `//` metadata, so it silently selected zero
mappings. Its parser now accepts that documented suffix and still fails closed
on duplicate destinations. Against the current external generated snapshot it
selected zero semantic renames: the 244 address-named entries are either
`func_`/`fake_func_` in the companion map or already synchronized human names.
This is a tool-validation result, not evidence for renaming the protected
ambiguous functions `0x8000040C` or `0x800927B0`.

s2700 audited every in-tree use of the audio queue at `0x80149990`, including
`factor5QueueSignal` (`0x800920D0`) and its direct mutex helpers. The queue is
created with capacity one and seeded with a zero token; acquire/block receive
and release/signal send only that token. The synth caller invokes signal after
its timing/state work. No message payload, receiver, or immediate consumer
reads rendered output, touches `0x801496B0`, calls `osAiSetNextBuffer`, or
names another PCM destination. This selects `H-queue-services` and rejects
`H-queue-publishes` and `H-queue-unresolved` for this queue (static generated
source evidence). The MORT-to-PCM publication edge remains unresolved; no
runtime watch, writeback, remap, or mitigation is authorized. Detailed table:
`scratch/agent/s2700_m5_queue_boundary/audit.md`.

s2702 audited every generated-source writer and alias of the AI worker
allocation at `0x801496B0`. `runAiAudioStreamPlaybackLoop` allocates `0x3000`,
stores the base in the global, derives sixteen `+0x300` aliases, clears the
whole span, and submits those aliases to AI. No generated scalar store, copy,
transform, DMA destination, or rendered-output source writes the span; the
other `-0x6950` matches are voice-table reads or unrelated object-relative
fields. The adjacent `serviceAudioOutputBuffers` body is only a load, and no
direct generated caller or named payload producer was found. This selects
`H-ai-clear-only` for the named generated surface and rejects
`H-ai-stream-writer`/`H-ai-render-writer`; an indirect or external producer is
not established. No runtime watch, writeback, remap, or mitigation is
authorized. Detailed table: `scratch/agent/s2702_m5_ai_source_writers/audit.md`.

s2701 completed the bounded queue-publication audit requested for the M5 CPU
boundary. `0x80149990` is a capacity-one recursive-mutex/token queue with
storage at `0x801499A8`; initialization, mutex acquire/release, and the
`musyxSynthFrame` block/signal pair all pass a zero message or a null receive
destination. The token is never interpreted as audio data. The only direct
block and signal caller is `musyxSynthFrame` (`0x8009123C`), and the separate
AI worker queue is at `0x80149670` while its cleared buffer allocation is
`0x801496B0`. No queue site reads rendered output, writes that allocation,
calls `osAiSetNextBuffer`, or names another PCM destination. This selects
`H-queue-services` and rejects `H-queue-publishes` and `H-queue-unresolved`
for this boundary (static generated-source evidence); the MORT-to-PCM edge
remains unresolved and no runtime watch, writeback, remap, or mitigation is
authorized. Detailed table: `scratch/agent/s2700_m5_queue_boundary/audit.md`.

s2703 audited every generated and host registration/call edge for the AI
worker. `initAudioSubsystem` directly creates thread object `0x801494B0` with
entry `0x8008ED70` (`runAiAudioStreamPlaybackLoop`), argument zero, and
priority `0x7A`, then starts it. The host `osCreateThread` bridge preserves
that entry through the native thread launch. `serviceAudioOutputBuffers`
(`0x8008ED6C`) has only its one-instruction load and no caller, callback-table
edge, service-worker registration, or return; overlay metadata is dispatch
registration only. No indirect target or named payload writer reaches the AI
aliases before `osAiSetNextBuffer`. This selects `H-ai-no-indirect-producer`
and rejects `H-ai-service-produces`, `H-ai-external-producer`, and
`H-ai-dead-registration` at this audited generated/host surface (static source
evidence). The MORT-to-PCM edge remains unresolved; no runtime watch,
writeback, remap, or mitigation is authorized. Detailed table:
`scratch/agent/s2703_m5_ai_indirect_path/audit.md`.

s2704 continued the generated-symbol sweep after the required last-15-title
check did not trigger a revisit. The rename tool now accepts an explicit
half-open address interval and prints a per-candidate decision table; fixed
renames are filtered to that same interval. The bounded
`0x8008ED6C..0x80091C80` region contained 19 companion candidates, all already
synchronized: zero selected renames, zero changed generated files, zero
ambiguous/fake candidates, and no parser or duplicate-destination rejection.
This selects `H-already-synchronized` and rules out `H-exact-matches` for this
region, without naming the protected placeholders or resolving MORT-to-PCM.
No build, run, runtime watch, writeback, remap, or mitigation was needed.

s2705 continued the generated-symbol sweep after the required last-15-title
check did not trigger a revisit. The bounded `0x80091C80..0x80095000` region
contained companion candidates but no exact unsynchronized semantic rename:
the tool selected zero renames in zero generated files, classified semantic
candidates as already synchronized, and preserved address-only and fake
entries as ambiguous-or-fake. There was no parser or duplicate-name rejection.
This selects `H-already-synchronized` for the region and rules out
`H-exact-matches` there; it does not resolve the MORT-to-PCM publication edge.
The external generated worktree had pre-existing changes in three files; this
run did not modify them. No build or game run was needed.

s2706 continued the generated-symbol sweep after the required last-15-title
check did not trigger the revisit rule. The bounded `0x80095000..0x80098000`
region produced 45 companion candidates. Zero references were renamed in
zero generated files: semantic entries were already synchronized, while
`0x8009711C` and `0x80097D58` remained ambiguous-or-fake address-only
entries. There was no parser or duplicate-destination rejection. Independent
spot-checks found the expected human names in generated output and the two
fake entries preserved in the companion map. This selects
`H-already-synchronized` for the region and rules out `H-exact-matches` there;
it does not resolve the MORT-to-PCM edge. No build or game run was needed, and
the external generated worktree was not modified.

s2707 continued the generated-symbol sweep after the required last-15-title
check did not trigger the revisit rule. The bounded `0x80098000..0x8009B000`
region contained 29 companion candidates. Zero references were renamed in
zero generated files: 27 semantic entries were already synchronized, while
`0x80099C4C` and `0x80099FDC` were classified ambiguous-or-fake and preserved.
There was no parser or duplicate-destination rejection. This selects
`H-already-synchronized` for the semantic candidates in this region and rules
out `H-exact-matches` there; it does not resolve the MORT-to-PCM publication
edge. No build or game run was needed, and the external generated worktree
was not modified.

s2708 continued the generated-symbol sweep after the required last-15-title
check did not trigger a revisit. The bounded `0x8009B000..0x8009E000` region
contained 41 companion candidates: 35 semantic entries were already
synchronized, while six address-only/fake entries (`0x8009C2C8`, `0x8009D7CC`,
`0x8009DE60`, `0x8009DEB4`, `0x8009DEC0`, and `0x8009DED0`) were preserved as
ambiguous-or-fake. Zero references changed in zero generated files, and the
tool exited successfully without parser or duplicate-destination rejection.
This selects `H-already-synchronized` for the semantic candidates in this
region and rules out `H-exact-matches`; no build or game run was needed.

s2709 continued the generated-symbol sweep after the required last-15-title
check did not trigger the revisit rule. The bounded `0x8009E000..0x800A1000`
region contained 44 companion candidates: five semantic entries were already
synchronized, while 39 address-only/fake entries were preserved as
ambiguous-or-fake. Zero references changed in zero generated files, and the
tool exited successfully without parser or duplicate-destination rejection.
This selects `H-already-synchronized` for the semantic candidates in this
region and rules out `H-exact-matches`; no build or game run was needed.

The s2710 generated-symbol sweep covered `0x800A1000..0x800A4000` and
found eight companion candidates: seven address-only/fake entries were
preserved as ambiguous-or-fake, while `junk_800A1784` was already
synchronized. Zero references changed in zero generated files; the tool
exited successfully without parser or duplicate-destination rejection.
This selects `H-already-synchronized`/`H-ambiguous-or-fake` for the region
and rules out `H-exact-matches` there. No build or game run was needed.

s2711 continued the generated-symbol sweep across `0x800A4000..0x800A7000`.
The complete decision table selected zero renames: semantic companion names
were already synchronized and address-only/fake entries were preserved. The
tracked rename tool was hardened to fail closed when one generated address is
given conflicting semantic companion names, instead of allowing the last
symbol file to win. Syntax validation and the bounded rerun passed; no
generated file changed, so no build or game run was warranted. This selects
`H-already-synchronized`/`H-ambiguous-or-fake` for the region and rules out
`H-exact-matches` there.

Session 2718 completed a bounded generated-symbol rename batch in the shared
external snapshot. The three placeholder functions at `0x800927B0`,
`0x80092A54`, and `0x80092CF0` are called exclusively by the already named
point-table, LUT, and constant resamplers respectively, and each emits the
packed interpolated sample word consumed by its caller. They are now named
`interpolatePointTableSamplesToPackedWord`,
`interpolateLutSamplesToPackedWord`, and
`interpolateConstantSamplesToPackedWord` in the regeneration-safe rename map,
companion symbols, and generated snapshot. The fourth true placeholder,
`0x8000040C`, remains protected because no semantic mapping exists. The
post-change bounded rerun selected zero stale references in zero files and
confirmed all three mappings are synchronized.

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
   ownership/cursor propagation. The caller audit found only the mixer caller
   and cursor/status updates. s2695 audited the post-mix chain: named
   consumers are state/service/timing operations, and the only concrete copy
   is descriptor-local `copyFourHalfwordsWriteback`; the indirect callback at
   `0x80091684` is now resolved to `submitDmaRequestBatch`, whose named
   consumer is the generic PI DMA service. s2697 audited `sendServiceMessage`,
   `piDmaWorker`, and the host PI bridge: they carry only descriptor fields,
   generic ROM-to-DRAM DMA, and completion messages, with no synth-output or
   AI-source publication. s2698 audited the host AI bridge and found exact
   pointer preservation into SDL, with no host remap or gate. s2701 audited
   the complete `0x80149990` queue and found a zero-token mutex service with
   no payload or AI join. s2702 found only allocation/alias setup, a full
   clear, and AI submissions for the generated `0x801496B0` surface; no named
   rendered or stream writer exists. s2703 audited the full generated/host
   indirect registration path: the AI loop is a direct thread entry, the
   adjacent one-instruction symbol has no caller or callback edge, and no
   opaque producer is reachable. Next: pivot to the next independently
   bounded CPU publication surface only if a new source/consumer relation can
   be named; do not repeat thread, queue/service, renderer, mixer, allocation,
   or host audits. Do not add a runtime watch until a legitimate destination
   and ordering edge are named. The s2717 M4 revisit independently classified
   the two existing retail candidate ranges as broad structured/allocator
   activity rather than a clean accumulator record; it did not change the M5
   publication priority.
2. **Generated-symbol renaming sweep.** s2718 renamed the three exact
   resampling helpers at `0x800927B0..0x80092CF0`; preserve the unresolved
   `0x8000040C` placeholder. Continue with one adjacent bounded region only
   when exact companion/source evidence exists. s2704 found all 19 candidates in
   `0x8008ED6C..0x80091C80` already synchronized, s2705 found no exact
   rename in `0x80091C80..0x80095000`, and s2706 found no exact rename in
   `0x80095000..0x80098000`, s2707 found no exact rename in
   `0x80098000..0x8009B000`, and s2708 found no exact rename in
   `0x8009B000..0x8009E000`, and s2709 found no exact rename in
   `0x8009E000..0x800A1000`, while s2710 found no exact rename in
   `0x800A1000..0x800A4000`, and s2711 found no exact rename in
   `0x800A4000..0x800A7000`. The tracked tool now rejects conflicting
   semantic names for one generated address rather than choosing by file
   order. Continue with one adjacent bounded region only while exact
   companion/source evidence remains available. s2712 covered
   `0x800A7000..0x800AA000` and found zero exact renames: semantic candidates
   were already synchronized and address-only/fake entries were preserved;
   there was no parser or duplicate-destination rejection. This rules out
   `H-exact-matches` for that region and retains
   `H-already-synchronized`/`H-ambiguous-or-fake`;
   preserve address-only or fake fragments and do not infer names from
   implementation shape alone. s2714 covered `0x800AD000..0x800B0000` and
   again selected zero renames: semantic candidates were already
   synchronized and fake/address-only entries were preserved, with no parser
   or duplicate-destination rejection. This rules out `H-exact-matches` for
   that region. s2715 covered `0x800B0000..0x800B3000`: 23 candidates were
   already synchronized and three were preserved as ambiguous-or-fake; zero
   references changed in zero files, with no parser or duplicate-destination
   rejection. s2716 covered `0x800B3000..0x800B6000`: 46 candidates were
   already synchronized and three were preserved as ambiguous-or-fake; zero
   references changed in zero files, with no parser or duplicate-destination
   rejection. This rules out `H-exact-matches` for that region; continue with
   the next adjacent bounded region.
3. **M5 image task contract edge.** Implement only after a named legitimate
   image writer and destination/order relation is independently established;
   s2680 authorizes no writeback or remap.
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

s2696 resolved and audited the indirect callback. `musyxSynthFrame` loads
`0x801499DC` at `0x80091670`; `initN64RspMixer:0x800918F0` initializes that
slot to `submitDmaRequestBatch` (`0x8000569C`). The callback copies request
descriptor fields into the PI DMA ring at `0x801112B0`, updates head/tail
state, and signals `sendServiceMessage`; it does not read the synth `$a3`
output block, touch the AI worker's `0x801496B0` allocation, or call
`osAiSetNextBuffer`. `findAndZeroTableSlotMatching` is a separate direct call
at `0x8009BD28`. This rejects `H-callback-publishes` for the MORT-to-PCM edge
and selects `H-callback-unrelated` for that edge (static source evidence);
generic DMA service remains the next unresolved consumer. No runtime watch,
writeback, remap, or mitigation is authorized. Detailed table:
`scratch/agent/s2696_mort_callback_boundary/audit.md`.

s2713 continued the generated-symbol sweep after the required last-15-title
check did not trigger. The bounded `0x800AA000..0x800AD000` region contained
26 companion candidates: 24 semantic entries were already synchronized and
two address-only/fake entries (`0x800AA6CC` and `0x800AAADC`) were preserved
as ambiguous-or-fake. Zero references changed in zero generated files, and
the tool exited successfully without parser or duplicate-destination
rejection. This selects `H-already-synchronized`/`H-ambiguous-or-fake` for
the region and rules out `H-exact-matches` there; no build or game run was
warranted.

s2714 continued the generated-symbol sweep after the required last-15-title
check did not trigger. The bounded `0x800AD000..0x800B0000` region selected
zero renames in zero generated files: unique semantic candidates were already
synchronized, while fake/address-only entries were preserved as
ambiguous-or-fake. The tool exited successfully with no parser or
duplicate-destination rejection. This selects
`H-already-synchronized`/`H-ambiguous-or-fake` for the region and rules out
`H-exact-matches` there; no build or game run was warranted. The complete
decision table is in `scratch/agent/s2714_generated_symbol_sweep/decision-table.txt`.

s2716 continued the generated-symbol sweep after the required last-15-title
check did not trigger. The bounded `0x800B3000..0x800B6000` region contained
49 companion candidates: 46 semantic entries were already synchronized and
three address-only/fake entries were preserved as ambiguous-or-fake. Zero
references changed in zero generated files, and the tool exited successfully
without parser or duplicate-destination rejection. This selects
`H-already-synchronized`/`H-ambiguous-or-fake` for the region and rules out
`H-exact-matches`; no build or game run was warranted. The complete decision
table is in `scratch/agent/s2716_generated_symbol_sweep/decision-table.txt`.
