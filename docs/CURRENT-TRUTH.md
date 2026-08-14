# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`. Durable history is in
[`docs/PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); do not reopen closed
lineages without a new class-level lead.

Reviewed through s934 (2026-08-13). The active blocker is the authoritative
FULL_SYNC/E9 accounting path after the post-sec2 gate. M5 audio de-stubbing is
closed. M3 work is limited to systematic idiom-class audits.

## User directive

1. Maintenance when this file exceeds 60,000 bytes.
2. A genuinely new M5 audio lead only; the existing M5 campaign is closed.
3. M3 crash work only as whole-idiom audits, not reactive crash chasing.

## Current truth

- Overlay dispatch is sufficiently fixed for mission entry and post-sec2
  outdoor presentation. The original boot/menu overlay hypothesis is closed.
- Product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations are OFF; any new mitigation requires an `ORIGIN:` naming the
  writer and assessing legitimacy.
- Phase-gated port captures reach VI width 1024 with independent
  `emit/raw/dispatch/match` provenance controls. Pre-chain crashes are
  disjoint families and do not classify parser loss.
- s833–s840 established exact producer/consumer task and range identity for
  the late E9-bearing population, including zero synthetic markers in s840.
  s835/s836 and s851/s852 established command-boundary/span accounting as the
  leading explanation for the bridge/parser delta. The one residual extended
  condition remains unclassified; no parser-loss, writer, or legitimacy
  conclusion is established.
- s842–s853 audited the triangle/copy family. Candidate B4/BF rows belonged to
  RDP rather than Factor 5, had non-triangle RDP entries, and matched accepted
  submit ranges. Extended-condition telemetry was added but did not reach the
  residual population. No behavior or mitigation changed.
- s855–s861 audited the recurring dispatcher and guest-PC family. The observed
  bounded slot population was valid; `0x8000834c` is a stale process-wide
  breadcrumb written by `drainMeshReleaseQueue`, not a reliable attribution of
  `getNextSlotNpcTypeId`. Later invalid chains and their writer remain open.
- s862–s877 audited the coalescer idiom and compared port/retail controls.
  Port entry probes observed invalid values (`a0=0/1`, head `0x830A10A0`),
  while retail watches showed only early initialization writers because the
  retail driver remains at VI width 320 despite verified Start pulses. Port
  reaches VI 1024 and late partition writers, but retail late-value comparison
  is phase-unreachable. No value-legitimacy or mitigation conclusion exists.
- s879 audited the retail oracle debugger ABI. Memory breakpoint callbacks carry
  only flags/address and guest PC; the callback fires before the core's
  `mem_write32`, so `DebugMemRead32` there returns the old value. A later
  frontend-thread read can observe current memory but cannot retain writer
  association and is racy. No safe deferred post-write value channel exists.
- s880 audited the remaining local oracle/core and decomp artifacts. The core
  has no existing post-write trace hook: its write breakpoint wrapper calls the
  callback before `mem_write32`, while CPU/memory pointer exports expose only
  current state. The decomp supplies the coalescer symbol and heap globals but
  no coalescer body or writer/value data-flow proof. H-no-independent-route is
  selected; no legitimacy or mitigation conclusion follows.
- s881 audited the top-ranked unguarded-walk candidate,
  `model_animation_offset_convert`. Six table-entry pointer reads
  (`0x80082BFC`, `0x80082C28`, `0x80082C48`, `0x80082C68`, `0x80082C88`,
  `0x80082CA8`) have bounded outer/inner loop control and the expected
  non-null checks. The generated source and companion decomp agree on the
  relative-offset conversion and optional inner pointers, but neither proves
  the caller's raw model blob values legitimate. No guard or behavior change.
- s882 audited `tickAudioChannel`'s program-stream cursor. The complete
  function has one direct cursor dereference at `0x8008BF24`, surrounded by
  cursor load/advance/store operations at `0x8008BF20` and `0x8008BF44–BF4C`.
  Nine semantic `channel+0x4` writer sites in the same function were
  classified, but the function mixes this stream idiom with unrelated channel
  and global-table accesses, and no source/symbol artifact proves the
  legitimacy of the stream pointer. No guard or behavior change.
- s883 audited `stopSongByHandle`'s two parallel linked-list chains. The
  `+0xE78` site at `0x80095960–0x8009597C` and the `+0xE7C` site at
  `0x800959B0–0x800959CC` each load a slot head, null-check it, then follow
  `next` pointers with a null-terminated loop. All 12 generated writes to
  these fields were inventoried: slot initialization, active-track and
  scheduled-event linking, sequence/sweep clearing, and the stop clears.
  The companion symbol artifacts establish the MusyX slot-table role but do
  not prove legitimacy of every linked-list writer/value. No guard or
  behavior change.
- s884 audited `tickSongSequence`'s complete linked-list use. It has four
  guarded chain consumers: voice chains rooted at `+0xE78` and `+0xE7C`
  (`0x80095BAC`/`0x80095BD0`) and cleanup/reaping chains at
  `0x80095C10`/`0x80095C60`; each checks the head and then follows a
  null-terminated `next` field. All same-class field accesses and sibling
  writers were enumerated, including initialization, active/scheduled
  insertion, reaping, and clears. Structural safety is established, but no
  independent evidence proves every writer/value legitimate. No guard or
  behavior change.
- s885 audited `tickAllActiveSongs`'s complete `+0xE7C` linked-list use. The
  single head load is null-checked, and the node loop reads `+0x8` then
  `+0x0`, with the next node revalidated by `validateVoiceHandle`; the shared
  initialization, insertion, reaping, and clear writers were all enumerated.
  Structural safety passed, but writer/value legitimacy remains unproven. No
  guard or behavior change.
- s886 audited `tickScheduledSongEvents`'s complete `+0xE7C` insertion path.
  The head load is null-tested before either non-empty insertion write, and
  the empty-list store is the only other path. Shared initialization, clear,
  and replacement writers were enumerated across the song functions. The
  companion symbols confirm the eight-slot MusyX table, but no independent
  evidence proves every writer/value legitimate. No guard or behavior change.
- s887 audited `tickActiveSongs`'s complete dispatcher. It has one slot-base
  load at `0x80095DC0`, bounded by an eight-iteration counter and an
  `0xEF8` stride, then calls `tickSongSequence` at `0x80095DC8`. It owns no
  linked-list dereference or null-check; the inherited `+0xE78/+0xE7C`
  chains are the already-audited `tickSongSequence` class. `startSongSequence`
  establishes the selected slot pointer at `0x80094918`, while the companion
  symbols independently identify the eight-slot table at `0x80149A00`.
  Dispatcher structure is classified, but inherited writer/value legitimacy
  remains unproven. No guard or behavior change.
- s888 audited `advanceSongRegion`'s complete function. Its outer walk is
  structurally bounded to 64 entries with a 16-byte stride, and its cursor
  reset/advance paths are explicit. The function nevertheless mixes region
  cursors, sequence-table pointers, event records, and per-slot tempo/control
  state. Existing guards cover the shared song-tick table base, but the local
  generated code and companion symbols do not independently prove every raw
  base/offset writer legitimate. H-advance-region-unclassified is selected;
  no guard or behavior change.
- s889 audited `processSongByHandle`'s complete function. It has two separate
  bounded eight-slot scans over the `0x80149A00` MusyX table: one resolves the
  low-31-bit handle from input `+0x0`, and the other resolves input `+0x8`.
  Both use the `0xEF8` stride and `-1` sentinel, but the input-record command
  fields and resolved slot fields feed distinct handler paths. Companion
  symbols confirm the table and dispatch roles, but do not prove the raw input
  record or every downstream writer/value legitimate. No guard or behavior
  change.
- s890 audited `playSongByIdLockCtl`'s complete function. It has a bounded
  positive-count walk over the `0x801529D0` song-bank pointer array, then
  resolves three entry-relative bases and scans `0x84`-byte sub-entries to a
  `0xFFFF` sentinel. The table/count writers and companion symbols establish
  the intended song-bank pipeline, but do not independently prove the dynamic
  count, raw entry pointer, or offset-derived bases legitimate. The function
  mixes bank-entry and sub-entry pointer shapes; no guard or behavior change.
- s891 audited `unloadLastSndFileGroup`'s complete teardown path. It selects
  the previous entry from the `0x801529D0` song-bank pointer array, then walks
  five entry-relative halfword tables to `0xFFFF` sentinels and one
  count-bounded voice-record table gated by entry state `== 1`. The generated
  source and companion symbols establish parser/table roles and loop controls,
  but do not independently prove the selected entry pointer, relative bases,
  or parsed record values legitimate. The function mixes sentinel-table and
  count-bounded record shapes; no guard or behavior change.
- s892 audited `serviceStreamedVoices`' complete streamed-voice service path.
  Its outer scan is bounded by `D_80141AD0`, with 0x18-byte records rooted at
  `0x80152A20`; active records use `+0x0` cursor, `+0x4` callback, `+0x8`
  sample base, `+0xC` count, `+0x10` cursor storage, and `+0x14` user field.
  Forward and wrapped callback branches are structurally classified, and all
  slot-field writers are accounted for in `startStreamedSampleVoice`, service
  cursor stores, initialization, and stop. The function mixes callback,
  sample-buffer, and cursor shapes; raw input/user values and indirect
  callback legitimacy remain unproven. No guard or behavior change.
- s893 audited `flushStreamedVoiceBuffers`' complete function. The outer scan
  is bounded by `D_80141AD0` and 0x18-byte records at `D_80152A20`, with a
  state-1 gate at `+0x0`. The active path loads `+0x8` as a halfword-buffer
  base and `+0xC` as an element/cursor index for `copyFourHalfwordsWriteback`;
  that helper copies four halfwords at `base + index*2` and writes back eight
  bytes. `startStreamedSampleVoice` is the only generated writer for these
  fields and supplies both from dynamic arguments; the reset/stop paths only
  clear state. Structure is bounded, but the buffer/index writer values are
  not independently proven legitimate. No guard or behavior change.
- s894 audited `streamSampleCountToByteSize`'s complete function. It is a
  12-byte pure arithmetic wrapper: the only input transformation is
  `($a0 + 4) << 1`, with no memory access, branch, loop, sentinel, or state
  check. Its only generated callsite is `loadSpeechFile`, which passes the
  immediate `0x10E0` and uses the resulting `0x21C8` as an `rs_malloc` size.
  Generated instructions, the callsite, and companion overlay metadata agree;
  broader audio-buffer legitimacy is outside this function. No guard or
  behavior change.
- s914 audited `loadSpeechFile`'s complete loader. It has two flag gates, one
  optional free of the prior speech-offset buffer, an asset-RAM lookup for the
  speech file, a fixed 4-byte allocation/DMA for its first word, a second
  count-derived allocation/DMA for the offset table, and coherent stores to
  `speechFile`, `numSpeechSamples`, `speechSampleOffsets`, and the two loaded
  flags. The generated caller supplies the preceding asset result and then
  initializes the voice table. Generated code plus companion symbols/docs agree
  on the speech-file layout, but do not independently prove dynamic asset
  pointers, count-derived size, or cleanup ownership legitimate; no guard or
  behavior change.
- s915 audited `initMusyXVoiceTable`'s complete initializer. It has one
  generated caller, initializes exactly one `0x80153420` voice slot with
  `0x1228` stride and zero pointer arguments, clears the active byte at
  `0x80154620`, creates/seeds the capacity-1 queue at `0x80154650`/`0x80154668`,
  allocates `0x21C8` bytes at `0x80154674`, registers callback `0x8009B5A8`,
  sets max voice count `0x800A5121` to 1, and clears `0x80154648`. The control
  flow proves one iteration, not an unbounded slot walk; no speech-file DMA or
  cleanup occurs in this function. Companion symbols and the caller agree on
  ownership and layout, but dynamic allocation/callback legitimacy remains
  unproven; no guard or behavior change.
- s916–s917 audited `shutdownMusyXVoices`' complete teardown. It has one
  direct caller; its first loop calls `stopVoiceSlotSynced(0)` exactly once.
  The second loop scans the same `0x80154620` table at `0x1228` stride until
  an inactive byte is observed, but has no finite slot-count termination: an
  active byte restarts the scan. The companion source confirms the teardown
  role and one-slot shape, while the callee can leave state 3 active, so the
  loop's termination depends on a later state transition. It then clears the
  max-voice-count byte, zeros the matching table slot, and frees the active
  speech/control buffers under their existing gates. Dynamic pointer/value
  legitimacy remains unproven; no guard or behavior change.
- s918 audited `accumulateVoiceSampleOffset`'s complete helper. Its slot
  offset arithmetic is exactly `index * 0x1228`, and it calls
  `consumeVoiceSamples(slotBase, a1+a3)` before adding that amount to slot
  `+0x463C`; there is no loop or local termination hazard. However, the
  stack-sourced index is unchecked, no generated caller was found, and the
  companion artifacts label `0x800A5121` as `speechFileLoaded` while the
  generated init/shutdown lifecycle uses it as a voice-subsystem gate. The
  shape is coherent but dynamic index/value legitimacy remains unproven; no
  guard or behavior change.
- s919 audited `dmaVoiceSampleAndSignal`'s complete helper. It preserves the
  four incoming DMA arguments through `synchronousDmaTransfer`, waits for that
  DMA to complete, then calls `osSendMesg` on incoming `$a3` with message zero
  and blocking mode. It has no global/slot accesses, loop, or local return
  hazard. No generated direct callers or companion body/callsite evidence
  were found, so indirect reachability and dynamic DMA/queue legitimacy remain
  unproven; no mitigation or behavior change.
- s920 audited `initMusyXVoiceSlot`'s complete 0xD4-byte helper. It has no
  loop, indirect call, derived walk, or local termination hazard: it bzeroes
  0x190 bytes at the supplied slot base, initializes the per-slot queue at
  `+0x11AC/+0x11C4`, stores the four pointer/control arguments at `+0x190`,
  `+0x194`, `+0x198`, and `+0x19C`, and clears the documented control fields
  through `+0x11DE`. The two generated callers agree on the slot base and
  helper entry but intentionally use different argument shapes: table init
  passes zero pointers, while voice allocation passes a computed sample
  pointer, slot-derived control values, and callback `0x8009BE08` as the
  stack argument. The companion symbol description agrees on the layout and
  role. The caller split is classified, but dynamic slot/pointer legitimacy
  remains unproven; no guard or behavior change.
- s921 audited `serviceStreamingVoice` (`0x8009BF14`). The generated
  definition is 0x32C bytes; the prior Next entry's 0x13C size was stale.
  It services one active voice record from the caller's
  `0x80153420 + index*0x1228` base. Queue receive at `+0x11AC` is nonblocking
  and gated by `+0x11DC`; the stream path updates
  `+0x11A0/+0x11A4/+0x11C8/+0x11D0`, then invokes the indirect callback at
  `+0x190` with a derived buffer and queue `+0x11AC`. A separate decode path
  calls `decodeAndFillVoiceBlock` using `+0x198` and a block index derived
  from `+0x11D8/+0x19C`, then updates `+0x11A0/+0x11CC/+0x11D8/+0x11A8`.
  Its retry loop decrements the loaded `+0x11DE` count and is locally finite;
  the sole generated caller is `tickMusyXVoices` at `0x8009B644`, whose outer
  loop executes once for the initialized one-voice configuration. Local
  structure is classified, but callback, buffer, divisor, and state-writer
  legitimacy remain unproven; no guard or behavior change.
- s922 audited `consumeVoiceSamples` (`0x8009C240`). The 0x60-byte helper has
  one state-3 gate, conditional `+0x11A8` countdown/state transition, and
  unsigned bounded consumption from `+0x11D8 - +0x11D4` into `+0x11D4`; it
  has no loop, indirect call, queue/global access, or derived pointer walk.
  Its sole generated caller supplies one coherent slot-base plus consumption
  amount shape. Dynamic slot fields and caller-derived amount legitimacy
  remain unproven; no guard or behavior change.
- s924 audited `decodeAndFillVoiceBlock` (`0x8009C904`). It has one direct
  caller, a coherent slot-base plus output-table-pointer shape, masked input
  indexing within the slot's `+0x1A0` block, and exactly four local
  filter/pan iterations. The generated helper has no unbounded loop or
  caller-shape split; dynamic slot pointers, table contents, and decoded
  values remain unproven, so no guard or behavior change.

## Recent evidence ledger

The detailed s820–s877 records are archived in PROJECT-OVERVIEW §29. The
short ledger below preserves the decision points needed for the next unit:

| Sessions | Result |
|---|---|
| s820–s831 | Width-1024 controls and early authoritative joins; ordering and ordinary submit identity passed. |
| s832–s840 | Late bridge/parser deltas persisted; exact ordinary producer/consumer ranges matched; synthetic path was absent. |
| s841–s853 | Copy/triangle reachability was unstable; source and runtime evidence moved ownership from Factor 5 to RDP garbage-shaped entries; residual extended path stayed unobserved. |
| s854–s861 | Late residual and dispatcher crash families were reachability-limited; stale guest-PC breadcrumb was proven by source audit. |
| s862–s871 | Coalescer entry/global idiom inventory and port probes found invalid entry state; writer legitimacy remained unknown. |
| s872–s877 | Retail watches and PIF/VI controls were live, but retail stayed at width 320; port reached late writers. Value comparison remained unavailable. |
| s879–s880 | Oracle ABI and artifact audits found no safe post-write writer/value route; coalescer legitimacy remains unproven and is parked. |
| s881 | `model_animation_offset_convert` array-pointer inventory: 6 sites structurally bounded; raw model-blob writer legitimacy remains unproven, so no mitigation. |
| s882 | `tickAudioChannel` cursor inventory: 1 direct stream dereference, 5 cursor operations, 9 semantic in-function `channel+0x4` writers; shape/writer legitimacy remains unproven, so no mitigation. |
| s883 | `stopSongByHandle` linked-list inventory: 2 parallel chains, 12 generated `+0xE78/+0xE7C` writes classified; writer/value legitimacy remains unproven, so no mitigation. |
| s884 | `tickSongSequence` linked-list inventory: 4 guarded chain consumers and all same-class sibling accesses/writers classified; structural safety passed, writer/value legitimacy remains unproven, so no mitigation. |
| s885 | `tickAllActiveSongs` inventory: 1 guarded `+0xE7C` chain consumer; shared writers classified, writer/value legitimacy remains unproven, so no mitigation. |
| s886 | `tickScheduledSongEvents` inventory: 2 guarded non-empty head uses plus 1 empty-list store; all shared `+0xE7C` writers classified, legitimacy remains unproven, so no mitigation. |
| s887 | `tickActiveSongs` inventory: 1 fixed-table slot-pointer load, bounded 8-slot loop, no direct chain dereference; `tickSongSequence` remains the inherited chain consumer and writer/value legitimacy remains unproven. |
| s888 | `advanceSongRegion` inventory: bounded 64-entry/16-byte walk with explicit cursor reset/advance, but mixed region/event/table pointer shapes and unproven raw writer legitimacy; no mitigation. |
| s889 | `processSongByHandle` inventory: two bounded 8-slot scans resolve input `+0x0` and `+0x8` through the `0xEF8` table; mixed record/slot shapes and writer legitimacy remain unproven; no mitigation. |
| s890 | `playSongByIdLockCtl` inventory: song-bank pointer load plus three entry-relative bases and a sentinel-terminated `0x84` sub-entry scan; dynamic count/raw pointer legitimacy remains unproven; no mitigation. |
| s891 | `unloadLastSndFileGroup` inventory: five sentinel-terminated entry-relative halfword walks plus one state-gated count-bounded voice-record walk; pointer/value legitimacy remains unproven and mixed shapes are retained; no mitigation. |
| s892 | `serviceStreamedVoices` inventory: count-bounded 0x18-byte streamed-voice scan with state gate, cursor comparisons, two callback branches, and writeback; slot-field writers are accounted for, but raw input/user values and callback legitimacy remain unproven; no mitigation. |
| s893 | `flushStreamedVoiceBuffers` inventory: count-bounded 0x18-byte scan with state-1 gate; `+0x8` buffer and `+0xC` element/cursor feed the four-halfword writeback helper; `startStreamedSampleVoice` supplies both dynamically, so structure passes but writer/value legitimacy remains unproven; no mitigation. |
| s894 | `streamSampleCountToByteSize` inventory: 12-byte pure `($a0+4)<<1` wrapper with no memory or control-flow hazards; sole caller passes constant `0x10E0` and allocates `0x21C8`; full classification passed for this function, with broader audio legitimacy out of scope. |
| s914 | `loadSpeechFile` inventory: two loaded-state gates, prior-offset-buffer free, speech asset lookup, fixed 4-byte header DMA, count-derived offset-table allocation/DMA, and coherent speech globals/flags; generated caller and companion speech layout agree, but dynamic pointer/count/cleanup legitimacy remains unproven; no mitigation. |
| s915 | `initMusyXVoiceTable` inventory: one caller and one proven slot initialization at `0x80153420`, capacity-1 control queue creation/seeding, fixed `0x21C8` allocation, callback registration, max-voice-count reset, and active-byte reset; no local speech-file DMA/cleanup and no shape mismatch, while dynamic allocation/callback legitimacy remains unproven; no mitigation. |
| s916 | Initial shutdown inventory said the active-byte wait was bounded to one slot; superseded by s917 after the branch/termination audit found no finite bound. |
| s917 | Re-audit correction: the first shutdown loop is exactly one slot-0 call, but the second active-byte scan has no finite bound and repeats while the slot remains active; `stopVoiceSlotSynced` can leave state 3, so termination depends on an external/later clear. Caller and slot shape still agree; no mitigation. |
| s918 | `accumulateVoiceSampleOffset` inventory: fixed `index*0x1228` slot arithmetic, one `consumeVoiceSamples` call, one `+0x463C` accumulation, no loop, and no generated callers found. The unchecked index and the `0x800A5121` symbol/lifecycle discrepancy leave dynamic legitimacy unresolved; no mitigation. |
| s919 | `dmaVoiceSampleAndSignal` inventory: four incoming DMA arguments pass unchanged to synchronous submit/wait, then `$a3` is used as the message queue for one blocking zero-message signal; no globals, slot fields, loop, or local termination hazard. No generated direct callers or companion body/callsite evidence were found, so indirect reachability and dynamic argument legitimacy remain unresolved; no mitigation. |
| s920 | `initMusyXVoiceSlot` inventory: fixed 0x190-byte clear, per-slot queue creation, four pointer/control stores, and documented control-field resets with no loop or local termination hazard. The two callers share the slot-base contract but use distinct initialization versus active-voice pointer shapes; the split is intentional/classified, while dynamic pointer/value legitimacy remains unproven; no mitigation. |
| s921 | `serviceStreamingVoice` inventory: one caller and finite local retry/refill loops; stream callback and decode/block paths are distinct but coherent roles. Dynamic callback/buffer/state legitimacy remains unproven; no behavior change. |
| s922 | `consumeVoiceSamples` inventory: one state-3 gate, conditional `+0x11A8` countdown/state transition, and unsigned `+0x11D8 - +0x11D4` consumption with `+0x11D4` writeback; no loop, indirect call, queue/global access, or derived pointer walk. Its sole caller supplies one coherent slot-base/amount shape, but dynamic field/value legitimacy remains unproven; no mitigation. |
| s895 | `setVoiceVolumePanLocked` inventory: one gate read, one nonzero handle check, no target dereference/loop, and one mutex-protected modulation call; shape is coherent, but caller-derived handle/parameter writers are not independently proven legitimate; no mitigation. |
| s896 | `stopStreamedVoice` inventory: one audio-enable gate, one computed 24-byte streamed-voice state access, state-1 check/clear, and `silenceVoiceSlot` call; the caller-derived voice index has no independent bound or writer-legitimacy proof, so full classification remains unresolved; no mitigation. |
| s897 | `compute3DSourceSpatialMix` inventory: null-terminated `0x80153418` source-list walk, complete spatial-distance/mix/pan/output access table, and independent node/list writer cross-checks; structure passes but dynamic node/input writer legitimacy remains unproven and shapes are mixed; no mitigation. |
| s898 | `applyVoice3DMixParams` inventory: one coherent voice-entry path with no loop or derived address walk; three explicit output clamps (`0..0x7F`, `0..0x3FFF`) and handle/chain calls are classified, but voice-entry fields and caller-derived inputs lack independent writer/value legitimacy proof; no mitigation. |
| s899 | `tickAndReap3DAudioVoices` inventory: bounded null-terminated doubly-linked-list reap rooted at `0x80153414`; link fields, `+0xA -> +0x8` state copy, and conditional `+0x34` handle dispatch fully enumerated, but dynamic node/head/handle legitimacy remains unproven and shapes are mixed; no mitigation. |
| s900 | `register3DAudioListenerNode` inventory: active-gated doubly-linked insertion at `0x80153418`, four input vector/record shapes, derived orientation helpers, scalar conversion, and all node stores classified; callers agree on one listener-node API shape, but dynamic pointer/input writer legitimacy remains unproven; no mitigation. |
| s901 | `enqueueSoundInPriorityGroup` inventory: count-bounded group scan plus sorted null-terminated queue insertion over `D_80152D70/74/78` and `D_80153290`; structure is coherent, but dynamic record/group/priority inputs, queue-node pointers, and cursor/count writers lack independent legitimacy proof; mixed table/list shape retained, no mitigation. |
| s902 | `enqueueSpatialSoundInPriorityGroup` inventory: bounded group lookup plus sorted linked-list insertion and a 0x20-entry spatial-record pool at `D_80152F00`; the linked-list and pool shapes are coherent within their respective paths, but mixed table/list/pool inputs and writers lack independent legitimacy proof; no mitigation. |
| s903 | `dispatchPrioritizedSoundQueue` inventory: bounded-by-count group walk plus guarded priority/pending linked-list operations and an unchecked `+0x18` voice-record pointer; local shapes are coherent, but dynamic count/node/voice writers and legitimacy remain unproven; no mitigation. |
| s904 | `update3DAudioFrame` inventory: active-list walk rooted at `0x80153414` with guarded unlinking; spatial-mix, priority-queue, voice-handle, and flag-state paths are coherent but mixed, while dynamic list/voice fields and writer legitimacy remain unproven; no mitigation. |
| s905 | `reset3DAudioLists` inventory: two standalone zero stores with a concrete ownership split between the `0x80153414` Factor 5 voice/source list and `0x80153418` MusyX listener/source list; sibling readers, insertion writers, and unlink writers agree, but reset ordering and dynamic writer legitimacy remain unproven; no mitigation. |
| s906 | `normalizeVec3` inventory: one fixed-shape in-place 3-float read/normalize/write path, one caller, and a caller-side zero-vector gate; no local zero-norm check, while input/output value legitimacy remains unproven; no mitigation. |
| s907 | `crossProductVec3` inventory: fixed-shape 3-float cross product with six input reads and three output writes; both generated callers pass matching slices of the same listener-node record, with no loop or derived pointer walk; dynamic input/output writer legitimacy remains unproven; no mitigation. |
| s908 | `invertOrientationMatrix` inventory: fixed-shape 12-float affine inverse with input/output offsets `0x00..0x2C`; two generated callers pass the same stack-temporary-to-record shape and no incompatible aliasing; dynamic matrix values/writers remain unproven; no mitigation. |
| s909 | `findVoiceSlotByAge` inventory: one generated caller and one coherent MusyX table shape (`0x80154620`, stride `0x1228`, active `+0x4620`, age/handle `+0x4644`, counter `0x80154648`); no pointer walk or caller-shape mismatch, but caller-derived index/counter legitimacy remains unproven; no mitigation. |
| s910 | `stopVoiceSlotSynced` inventory: one computed MusyX slot shape (`0x80154620`, stride `0x1228`), active/state reads and writes, shared queue, and `slot+0x3420` stop call; both callers agree on the slot-index contract and no local walk or shape mismatch exists, but caller-derived index/state legitimacy remains unproven; no mitigation. |
| s911 | `setVoiceMixByKey` inventory: one coherent MusyX slot shape with active/key/handle reads, three mix-byte stores, shared queue, and two matching callers; emitted control exits after the first failed candidate, so writer/value legitimacy and the unusual one-candidate behavior remain unproven; no mitigation. |
| s912 | `serviceVoicePoolFrame` inventory: one coherent `0x80154620` voice-slot shape with `0x1228` stride, state/streaming accesses, queue operations, and no pointer/list walk; no generated direct caller was found, and queue/state plus shared-field writer legitimacy remain unproven; no mitigation. |
| s913 | `getVoicePlaybackProgressByKey` inventory: two callers agree on a handle-plus-output-float contract and the helper's `0x80154620`/`0x1228` slot shape; the helper has an explicit `speechFileLoaded` gate but no finite scan bound or sentinel, and its miss path reaches the 32-bit counter wrap. Slot progress reads and queue handoff are classified, but scan termination and dynamic writer/value legitimacy remain unproven; no guard or behavior change. |
| s923 | MusyX per-slot queue inventory: `initMusyXVoiceSlot` creates `slot+0x11AC` with buffer `slot+0x11C4` and capacity 1; `serviceStreamingVoice` has the only generated receive site, gated by `slot+0x11DC`, using nonblocking `osRecvMesg(queue, NULL, 0)` and checking only the return. The two init callers share the slot-base contract and the receive path has no message dereference or queue retry loop; dynamic queue/state writer legitimacy remains unproven, so no guard or behavior change. |
| s924 | `decodeAndFillVoiceBlock` inventory: one direct caller passes the voice slot and `+0x198` block-table entry; the helper masks the bitstream word index to a `0..0xFFC` offset from `slot+0x1A0`, decodes into a fixed stack block, and runs four filter/pan iterations before updating `+0x11C8`. Local control and caller shape are coherent; dynamic pointer/table/value legitimacy remains unproven; no mitigation. |
| s934 | `musyxStoreVoiceAdsrParams` inventory: one caller passes a byte-loaded voice index and a stack ADSR record; the helper computes an `index*0x88` slot and performs four fixed ADSR reads/writes. The base guard covers only KSEG0 range, not index-versus-mixer-count, so derived slot legitimacy remains unproven; no mitigation. |
| s935 | `musyxTriggerVoiceAttack` inventory: the callee masks `$a0` to 16 bits, computes `index*0x88` from mixer base `0x801496F8`, and performs fixed slot accesses through `+0x6C`. The `tickAudioChannel` caller supplies inherited `$s6`, initialized to zero by `tickAllAudioChannels`; the streamed-voice caller supplies a `0x80153420 + 0x1228*k` record pointer through `$s0`. These are distinct contracts, and the latter low-halfword value is not a bounded mixer index. Existing base-only guard does not resolve the mismatch; no mitigation. |
| s928 | `renderVoiceAudioBlock` inventory: one direct caller and one shared voice-record/output contract; four fixed lattice stages, three fixed mix transforms, one fixed compand edge, and no local loop. Nested stereo mixing has eight indirect calls per stage, with targets derived from fixed return-address offsets; dynamic voice/output pointer legitimacy remains unproven; no mitigation. |
| s926 | `applyVoiceDelayFilter` inventory: three direct callers share one voice-base/delay/channel-table/stack-output shape; its 120-halfword shift and 40-halfword mix loops terminate, but the voice base, return-address-derived table read, and output/input ranges lack local bounds or legitimacy proof. Caller-shape mismatch is ruled out; full classification is not. No mitigation. |
| s927 | `runVoiceLatticeFilter` inventory: four callers share matching source/output offsets and counts (13, 14, 13, 120 iterations); the helper has two sequential halfword walks, no helper edge, and fixed termination. Its eight coefficient loads from the caller's voice record are fixed, and all local walks are bounded by the supplied counts. Dynamic pointer/value legitimacy remains unproven; no mitigation. |
| s933 | `musyxSetVoiceAdsrFromTable` inventory: one caller with a matching `(voice-slot, program-pointer)` shape; the ADSR search uses the fixed 8-byte table at `0x80148C68`, count at `0x8013AF0C`, and bounded lower/upper updates. Count writers cap the table at 256 entries, and the selected entry reads four halfwords before a fixed store helper writes slot offsets `+0x28..+0x30`. Dynamic voice-slot, program-pointer, table contents, and count legitimacy remain unproven; no mitigation. |
| s929 | `audioMixStereoBlock8` inventory: one caller and one shared voice-record shape; the selector at `+0x188` swaps two fixed eight-halfword ranges at `+0x168` and `+0x178`, and each of four stages performs exactly eight calls at offsets `0..0xE`. `$t3` resolves only from fixed return-address offsets to `0x8009DD48`, `0x8009DD60`, `0x8009DD70`, and `0x8009DD88`; no data-derived target, unbounded walk, or caller-shape split; dynamic voice-buffer/value legitimacy remains unproven; no mitigation. |

All runtime claims above had positive controls in the relevant capture. A
single-source result is explicitly labelled in the archived session entry;
none authorizes a mitigation.

## s925 — `filterVoiceSampleBlock` remains locally unclassified

This source-only inventory found exactly three direct generated callers, at
`0x8009C540`, `0x8009C88C`, and `0x8009D740`. All three pass the same four-
iteration voice-channel shape: `a0` is a decoded selector, `a1` is a
caller-derived halfword offset, `a2` points at a 13-halfword input/output
block, and `a3` points at a caller-owned stack/output workspace. No caller
shape split was found.

Inside `filterVoiceSampleBlock`, the 13-sample transform reads and rewrites
`a2[0..12]`; a second fixed loop clears 40 halfwords at `a3[0..39]`; and the
final fixed loop copies 13 halfwords to addresses beginning at `a3 + 2*a1`
with a six-byte stride. The latter range is not locally bounded by `a1`, and
neither `a2` nor `a3` is checked. For selectors `a0 <= 7`, the generated
MIPS path also reads a byte through a return-address-derived address before
computing the filter parameters; the source and companion symbols do not
independently establish that table's bounds. All three loops have fixed
termination (13, 40, and 13) and the only helper edge is the
unreachable-on-ordinary-MIPS `bltzal $zero` path to `0x8009D8BC`, which falls
into an emitted `scd` trap rather than a normal callable helper.

This rejects H-filter-voice-classified and H-filter-voice-shape-mismatch as
complete explanations: the callers agree, but local pointer/output bounds
and the selector table path remain unclassified. H-filter-voice-unclassified
is retained. No guard, mitigation, generated-code edit, or game behavior
changed.

ORIGIN: complete generated helper/caller, access-range, loop, and
companion-symbol inventory; no guest value mutation or mitigation.

## s926 — `applyVoiceDelayFilter` remains locally unclassified

Performed the planned source-only M3 idiom inventory of
`applyVoiceDelayFilter` (`0x8009D8C4`) in
`../N64Recomp/RecompiledFuncs/funcs_27.c`. Enumerated the complete generated
body, all direct callers, caller argument setup, access ranges, loop
termination, the unresolved conditional helper edge, and the companion
`main_overlay.txt` mapping. No build, game run, or soak was run.

Exactly three direct callers exist: `updateVoiceChannelParams` at
`0x8009C55C`, and `updateVoiceChannelParamsLarge` at `0x8009C8A8` and
`0x8009D75C`. All pass the same shape: `$a0` is the voice-record base, `$a1`
is a delay/sample value, `$a2` is a halfword channel/table value, and `$a3`
is a caller-owned stack output buffer. No caller-shape split was found.

The helper reads and writes voice state at `$a0+0x166`, then shifts 120
halfwords from `$a0+0x50` down to `$a0`, with a fixed terminating counter. It
derives a table read from `$ra+0x84+2*$a2`, then mixes 40 halfwords from a
`$a0 - 2*$t3 + 0xF0`-based range into `$a0+0xF0` and `$a3`. `$t3` is clamped
to the inclusive range `0x28..0x78`, which bounds the arithmetic offset but
does not prove the voice base, table address, output pointer, or source/output
ranges valid. The `bltzal $zero` path is never taken on ordinary MIPS; its
emitted unresolved branch/trap does not provide a normal helper call or a
termination hazard.

### Result

H-apply-delay-shape-mismatch is ruled out. H-apply-delay-classified is not
supported because the pointer/table accesses and derived ranges remain
unclassified; H-apply-delay-unclassified remains active. The generated source
and companion symbol mapping are two artifact lines agreeing on function
identity and call structure, but this remains a single-source static result:
no independent runtime writer/value evidence was claimed. No guard,
mitigation, generated-code edit, or game behavior changed.

ORIGIN: complete generated helper/caller, access-range, loop, unresolved-edge,
and companion-symbol inventory; no guest value mutation or mitigation.

## Superseded interpretation

The s916 claim that the shutdown active-byte scan was a bounded one-slot wait
is superseded by s917. The generated branch is `bne count,1` around a scan
whose active case does not increment the count; only an inactive byte advances
the count to one. The companion one-slot description establishes intended
shape, not a local termination bound. No runtime conclusion follows.

## s930 — `audioCompandS16` is structurally classified

Performed the planned source-only M3 idiom inventory of `audioCompandS16`
(`0x8009DD7C`) in `../N64Recomp/RecompiledFuncs/funcs_27.c`. Enumerated all
four generated references, entry/target shapes, the complete helper's sign
and region paths, arithmetic bounds, clamp, sign restoration, and return mask.
Cross-checked `main_overlay.txt`. No build, game run, or soak was run.

Three references are fixed tail-call entries from
`audioMixSampleS16_1_3` (`0x8009DD3C`), `audioMixSampleS16_1_1`
(`0x8009DD54`), and `audioMixSampleS16_3_1` (`0x8009DD64`); their weighted
mix arithmetic falls into the common helper. The fourth is the overlap-style
`bltzal $zero` site in `renderVoiceAudioBlock` at `0x8009DC10`, which the
generated C represents as a fixed helper edge; its condition is false for
ordinary MIPS `$zero`, so it is not independently reachable in that
representation. No data-derived target or caller-shape split exists.

The helper records sign and takes magnitude, then selects fixed regions at
`0x2B33` and `0x4E66`: double below the first, `x+0x2B33` below the second,
and `x>>2+0x6600` otherwise. It clamps the positive result to `0x7FFF`,
restores sign, and masks to 16 bits. There is no loop, indirect call, pointer
access, or local termination hazard. Dynamic input legitimacy remains
unproven. H-compand-shape-mismatch is ruled out and H-compand-classified is
supported structurally, while the broader H-compand-unclassified remains
open. No guard, mitigation, generated-code edit, or game behavior changed.

ORIGIN: complete generated helper/reference, target, arithmetic-bound,
termination, and companion-symbol inventory; no guest value mutation or
mitigation.

## s932 — `musyxInitVoiceFromSample` remains structurally unclassified

Performed the planned source-only M3 idiom inventory of
`musyxInitVoiceFromSample` (`0x80092128`) in
`../N64Recomp/RecompiledFuncs/funcs_24.c`. Enumerated both generated callers,
their argument setup, the complete callee, the existing base-pointer guard,
all descriptor reads, all slot writes, derived ranges, and the companion
`main_overlay.txt` mapping. No build, game run, soak, guard, or behavior
change was made.

The two callers agree on the helper contract `(voiceIdx, sampleDesc,
adsrFlag)`. `func_8008A4A0` passes an 8-bit voice index from `$s5+0xBD`, a
descriptor pointer from `0x8014ACA0`, and an ADSR flag selected from `$s5+0x67`
and `$s5+0x24`. `startStreamedSampleVoice` at `0x80097FE8` passes the result
of `stopVoiceByKey` (rejecting only `-1`), a stack-built descriptor at
`$sp+0x18`, and flag `1`. No caller-shape mismatch was found.

The callee computes `((voiceIdx & 0xFFFF) * 0x88)` and adds it to the global
voice-array base at `0x801496F8`. The existing guard checks only that base is
in KSEG0; it does not bound the masked index, and the second base reload has
the same missing index proof. The slot initialization writes offsets
`0x00..0x4A`, with an 8-byte store at `+0x08`; later descriptor-derived
fields write through `+0x6D`. The optional ADSR path also touches the slot's
`+0x28..+0x30` fields and sets a flag at `+0x02`. All descriptor reads are
fixed offsets `+0x04`, `+0x08`, `+0x0C`, `+0x10`, `+0x14`, and byte `+0x18`,
but neither descriptor pointer validity nor descriptor contents are checked.
There are no helper calls, loops, or local termination hazards.

H-voice-init-shape-mismatch is ruled out. H-voice-init-classified is not
supported because the index is only truncated, not bounded to the intended
voice count, and the descriptor pointer/value contract is not independently
proven. H-voice-init-unclassified remains selected. This is a single-source
static result: generated code and the companion symbol comment agree on the
function identity and 0x88 voice-slot role, but no independent runtime
writer/value evidence was claimed.

ORIGIN: complete generated caller/callee, access-range, guard-coverage, and
companion-symbol inventory; no guest value mutation or mitigation.

## s933 — `musyxSetVoiceAdsrFromTable` is structurally classified

Performed the planned source-only M3 idiom inventory of
`musyxSetVoiceAdsrFromTable` (`0x8008A8C4`) in
`../N64Recomp/RecompiledFuncs/funcs_22.c`. Enumerated the sole generated
caller, its register setup, the complete binary-search body, all table and
slot accesses, the count-management writers, the helper edge, and the
companion `main_overlay.txt` mapping. No build, game run, soak, guard, or
behavior change was made.

The only caller is the SoundMacro dispatcher at `0x8008C398`; it passes the
voice-slot base in `$a0` and the program pointer `0x8013ACC0` in `$a1`. No
caller-shape split was found. The callee reads the ADSR id from `$a1+0`,
stores its byte-shifted form at `0x8013AC5C`, and searches the fixed 8-byte
records rooted at `0x80148C68`. The active count is loaded from
`0x8013AF0C`; the search initializes lower bound 1 and upper bound `count+1`,
probes index `((lower+upper)>>1)-1`, and updates one bound until the signed
comparison returns zero or the interval closes. With a legitimate positive
count, every probe index is within `[0,count-1]`, so each probe reads only the
record's `+4` halfword. The zero-count path skips table access.

The count-management family was checked in `funcs_21.c`: insertion and
removal operate under the Factor 5 mutex, scan with the count, and reject
insertion at the `0x100` cap; their count stores therefore support the
256-entry bound used by the search. A successful match is passed to
`musyxStoreVoiceAdsrParams`, which has the existing voice-array-base guard and
writes the four selected halfwords to slot offsets `+0x28`, `+0x2A`, `+0x2C`,
and `+0x30`; the caller-derived voice-slot base and the program pointer are
not independently validated here.

H-adsr-table-shape-mismatch is ruled out. H-adsr-table-classified is supported
for caller shape, table stride, search termination, and local access ranges.
The broader H-adsr-table-unclassified remains open for dynamic legitimacy of
the voice slot, program pointer, table contents, and count state. This is a
single-source static result: generated code, count-management code, and
companion symbol metadata agree on the structure, but no independent runtime
writer/value evidence was claimed. No guard, mitigation, generated-code edit,
or game behavior changed.

ORIGIN: complete generated caller/callee, count-writer, access-range,
termination, helper-edge, and companion-symbol inventory; no guest value
mutation or mitigation.

## Ranked backlog

1. Do not use the process-wide `0x8000834c` breadcrumb to select a helper crash
   site; require a new independently phase-gated caller/state boundary.
2. Continue M3 only as complete idiom inventories with every site classified
   and proof/guard per site. Queue passive breadcrumbs as soaks.
3. M4 correctness: outdoor `baseFixed=-32768` zero shade, attribution S=0
   triangles, then I4 `sample=64x128`, each with independent controls.
4. Retain the regeneration delete-before-regen rule and audit fixup counts if
   a reproducible omission appears.

## s927 — `runVoiceLatticeFilter` is structurally classified

Performed the planned source-only M3 idiom inventory of
`runVoiceLatticeFilter` (`0x8009D980`) in
`../N64Recomp/RecompiledFuncs/funcs_27.c`. Enumerated the complete generated
body, every direct caller, caller register setup, memory access ranges,
termination, and the companion `main_overlay.txt` mapping. No build, game run,
or soak was run.

The helper has no direct or indirect helper call. Each iteration reads one
halfword from `$t1`, advances `$t1` by two, computes the lattice update from
the eight coefficient registers `$s0..$s7` and four packed state/input
registers `$t6..$t9`, then writes one halfword through `$t0` and advances `$t0`
by two. The eight coefficients are loaded by `renderVoiceAudioBlock` from
`$a0+0x140..$0x15C`, a fixed eight-word record range.

Exactly four generated callsites occur in `renderVoiceAudioBlock`. They pass
matching source/output offsets `(0, 0)`, `(0x1A, 0x1A)`, `(0x36, 0x36)`, and
`(0x50, 0x50)`, with loop counts `0xC`, `0xD`, `0xC`, and `0x77`. Because the
MIPS loop tests `t3 > 0` before decrementing, these produce 13, 14, 13, and
120 iterations respectively. Thus both halfword walks have fixed, bounded
ranges in every caller; no caller-shape split or local termination hazard was
found. The caller and companion symbol artifacts agree on identity and
structure.

### Result

H-lattice-shape-mismatch and the local-control portion of
H-lattice-unclassified are ruled out. H-lattice-classified is supported for
caller shape, fixed coefficient access, local access ranges, and termination.
This remains a single-source static classification: the dynamic `$t0`/`$t1`
pointer origins, the eight coefficient values, and the packed state values
are not independently proven legitimate. No guard, mitigation, generated
code edit, or game behavior changed.

ORIGIN: complete generated helper/caller, register setup, access-range,
termination, and companion-symbol inventory; no guest value mutation or
mitigation.

## s928 — `renderVoiceAudioBlock` is structurally classified

Performed the planned source-only M3 idiom inventory of
`renderVoiceAudioBlock` (`0x8009DB44`) in
`../N64Recomp/RecompiledFuncs/funcs_27.c`. Enumerated its complete generated
body, the sole direct caller, every nested helper edge, memory access range,
and termination. Cross-checked the companion `main_overlay.txt` mapping and
the generated symbol table. No build, game run, or soak was run.

`updateVoiceChannelParams` at `0x8009C4C0` is the only generated caller. It
passes the same voice-record base through `$a0`, caller-derived source and
destination buffers through `$a1/$a2`, and the caller's output/control value
through `$a3`; no second caller shape exists. The render body loads and later
restores eight coefficient words at `$a0+0x140..0x15C`, reads and restores a
halfword at `$a0+0x164`, and performs four fixed stages at source/output
offsets `0`, `0x1A`, `0x36`, and `0x50`. The nested lattice counts are
`0xC, 0xD, 0xC, 0x77`, producing 13, 14, 13, and 120 bounded iterations.

The three arithmetic mix helpers and the compander have no memory access or
loop. Each of the four `audioMixStereoBlock8` calls has eight bounded sample
steps, and its `$t3` indirect target is formed from a fixed `$ra` offset at
the callsite; the four offsets select the documented mix/compand entry paths,
not a guest-data-derived function pointer. The generated body has no
unbounded control path or caller-shape split.

### What it showed

H-render-shape-mismatch is ruled out. H-render-classified is supported for
caller shape, local accesses, nested edge identity, and termination. The
broader H-render-unclassified remains open only for dynamic legitimacy of
the voice-record base, source/output pointers, coefficient/state values, and
the data consumed by the nested stereo mixer. This is a single-source static
classification supported by generated code plus companion symbol artifacts;
no independent runtime writer/value evidence was claimed. No guard,
mitigation, generated-code edit, or game behavior changed.

ORIGIN: complete generated helper/caller, nested-edge, access-range,
termination, and companion-symbol inventory; no guest value mutation or
mitigation.

## s929 — `audioMixStereoBlock8` is structurally classified

Performed the planned source-only M3 idiom inventory of
`audioMixStereoBlock8` (`0x8009DC98`) in
`../N64Recomp/RecompiledFuncs/funcs_27.c`. Enumerated every generated
caller, the caller's `$a0`/`$t3` setup, all sample accesses, the four indirect
target paths, and local termination. Cross-checked the companion
`main_overlay.txt` mapping and all four target helper bodies. No build, game
run, or soak was run.

`renderVoiceAudioBlock` at `0x8009DB44` is the only generated caller. Its four
callsites derive `$t3` from fixed `$ra` offsets and resolve to
`0x8009DD48`, `0x8009DD60`, `0x8009DD70`, and `0x8009DD88`. These are fixed
interior continuation points in the three weighted-mix/compand helper paths,
not guest-data-derived function pointers. The helper reads the selector at
`$a0+0x188`; one branch uses `$a0+0x168` as `$t0` and `$a0+0x178` as `$t1`,
and the other swaps them. Each path then reads exactly eight halfword pairs at
offsets `0, 2, 4, 6, 8, 0xA, 0xC, 0xE`, covering the two fixed ranges
`$a0+0x168..0x176` and `$a0+0x178..0x186`. There is no loop or other
termination path in the generated helper.

H-stereo-shape-mismatch and the local-control portion of
H-stereo-unclassified are ruled out. H-stereo-classified is supported for
caller shape, fixed target derivation, access ranges, and termination. The
broader H-stereo-unclassified remains open only for dynamic legitimacy of the
voice-record base, selector, and sample values. This is a single-source static
classification supported by generated code plus companion symbol artifacts;
no independent runtime writer/value evidence was claimed. No guard,
mitigation, generated-code edit, or game behavior changed.

ORIGIN: complete generated caller/target, register-derivation, access-range,
termination, and companion-symbol inventory; no guest value mutation or
mitigation.

## s934 — `musyxStoreVoiceAdsrParams` remains structurally unresolved

Performed the planned source-only M3 idiom inventory of
`musyxStoreVoiceAdsrParams` (`0x800922C4`) in
`../N64Recomp/RecompiledFuncs/funcs_24.c`. Enumerated the complete helper,
the sole generated caller, caller register setup, voice-array base and count
globals, all ADSR record reads, all slot writes, existing guard coverage, and
the companion `main_overlay.txt` mapping. No build, game run, soak, guard, or
behavior change was made.

The only caller is `musyxSetVoiceAdsrFromTable` at `0x8008A9DC`. It loads the
voice index from `$s5+0x67` with `lbu`, so the register setup supplies a
`0..255` value without a local check against the mixer voice count at
`0x80149700`; the companion and allocator path describe the array as a
0x88-stride mixer voice table whose setup count is capped at `0x20`. It passes
`$a1 = $sp+0x10`, where the caller has just written four byte-swapped ADSR
halfwords from the matched table record. No second caller or caller-shape
split exists.

The callee loads the heap-array base pointer from `0x801496F8`, and the
existing guard rejects only values outside `0x80000000..0x807FFFFF`. It then
computes `index * 0x88` and writes halfwords at slot offsets `+0x28`, `+0x2A`,
`+0x30`, plus the converted sustain float at `+0x2C`. The record reads are
the fixed offsets `+0`, `+2`, `+4`, and `+6`; there are no helper calls, loops,
or local termination hazards. The stack record is locally coherent, but the
derived slot can escape the allocated voice array when the byte index is not
otherwise constrained.

H-adsr-store-shape-mismatch is ruled out. H-adsr-store-classified is supported
for fixed record and slot access shapes only, not for full safety: the base
guard does not establish index bounds, and no independent writer/value proof
establishes that `$s5+0x67` is always below the active voice count.
H-adsr-store-unclassified remains selected. This is a single-source static
result from generated code, allocator/count code, and companion symbol
metadata; no independent runtime writer/value evidence was claimed. No
mitigation, generated-code edit, or game behavior changed.

ORIGIN: complete generated caller/callee, index arithmetic, base/count,
access-range, guard-coverage, termination, and companion-symbol inventory;
no guest value mutation or mitigation.

## s935 — `musyxTriggerVoiceAttack` has a caller-contract mismatch

Performed the planned source-only M3 idiom audit of `musyxTriggerVoiceAttack`
(`0x8009231C`) in `../N64Recomp/RecompiledFuncs/funcs_24.c`. Enumerated the
complete callee, both generated callers, register setup, voice-array base and
stride, slot accesses, existing guard, helper edges, and the companion symbol
mapping. No build, game run, soak, guard, or behavior change was made.

The callee has no helper calls or loops. It masks `$a0` to 16 bits, computes
`base + (index * 0x88)`, reads slot `+0x28`, then writes `+0x6C`, `+0x60`,
`+0x68`, `+0x5C`, `+0x64`, `+0x0`, and `+0x58`. All accesses fit a nominal
0x88-byte record and local termination is fixed. Its existing guard checks
only that the base loaded from `0x801496F8` is in KSEG0; it does not check the
masked index against the mixer count.

The callers do not share one contract. `tickAudioChannel` at `0x8008CE7C`
passes `$s6`; `tickAllAudioChannels` initializes `$s6` to zero and no later
write establishes a per-channel mixer index before this call. The other caller
is `startStreamedSampleVoice` at `0x80098194`, which passes its `$s0`; its sole
caller `serviceVoicePoolFrame` sets that value to
`0x80153420 + 0x1228*k`, a Factor 5 voice-record pointer. The attack helper
then masks that pointer and interprets the low halfword as a mixer index (for
`k=0`, `0x3420`), which is not bounded by the 0x20 mixer voice count and can
escape the allocated mixer array. The mismatch is therefore established, but
the intended writer/translation and runtime legitimacy are not.

H-voice-attack-classified is rejected. H-voice-attack-shape-mismatch is
selected, with H-voice-attack-unclassified still open for the intended
pointer-to-index contract and its writers. This is a single-source static
result from generated code and companion symbol metadata; no independent
runtime writer/value evidence was claimed. No mitigation, generated-code edit,
or game behavior changed.

ORIGIN: complete generated caller/callee, register derivation, pointer/index
contract comparison, access-range, guard-coverage, termination, and
companion-symbol inventory; no guest value mutation or mitigation.

## Next work unit

HYPOTHESIS-ID: m3-audio-voice-stop-contract

Audit the complete `musyxStopVoice` idiom at `0x80092368` in
`../N64Recomp/RecompiledFuncs/funcs_24.c`, including every generated caller,
the relationship between pointer/index arguments, voice-slot arithmetic,
state writes, existing guard coverage, and sibling callers in the same audio
paths. Source-only; do not add a guard, change game behavior, build, or run a
soak.

Competing hypotheses:

- H-voice-stop-unclassified: a caller supplies an invalid voice index/base,
  or the stop target escapes its intended mixer record.
- H-voice-stop-classified: callers agree on a bounded mixer index and the
  existing guards cover the base/index contract.
- H-voice-stop-shape-mismatch: callers use pointer and index contracts that
  must be translated or are distinct; record the exact split and stop.

Discriminating measurement: enumerate every reference and caller register
setup, inspect the complete callee and all state/slot accesses, derive every
address range and termination path, classify every helper edge, and
cross-check `main_overlay.txt` plus the two caller chains identified in s935.
Any pointer/index split, uncovered derived access, or unproven termination
path rejects classification.

Exact command: `rg -n -C 12 "musyxStopVoice|80092368|92368" ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/main_overlay.txt`, then inspect the complete helper and every caller. No game build or soak is planned.

## Closed and parked

- M5 audio (legacy campaign) is CLOSED; a new lead is required. See
  `docs/M5-AUDIO-PLAN.md` and PROJECT-OVERVIEW §§9–12.
- Hangar-exit to sec2 is CLOSED except the backlog item above; see
  PROJECT-OVERVIEW §27.
- Earlier idiom campaigns, duplicate-symbol work, missing-function inventory,
  old ucode/DMA experiments, and rendering dead ends are archived in
  PROJECT-OVERVIEW §§13–26.
- Parked items include intermittent regeneration omission, isolated
  animation/frameStart SIGBUS reports, the M3 DoD gate, and M4 band-row
  coverage.

## Ground truth and method rules

- Before runtime instrumentation, consult `tools/oracle/README.md` and
  `docs/F5-UCODE-REFERENCE.md`; arm a positive whole-RDRAM control first.
- Gate animating comparisons on `PROBE_PHASE_WIDTH` and
  `PROBE_KEYS_FROM_PHASE=1`; scope counters and budgets to the phase.
- Batch instrumentation into one build/run. Require two independent evidence
  lines before promoting a conclusion.
- Launch from `build/` with the ROM present, use SIGKILL, and use capture paths
  whose final component does not begin with `.`. Queue repeat soaks.
- Generated diagnostics belong in fixup scripts. Regeneration order is
  `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then CMake.

## Build and patch cautions

Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
`git reset --hard`. If editing under `lib/`, export patches with
`./submodule-patches/export.sh`. Ignore the benign `wmain/main` warning;
prefix environment-led commands with `env`; do not hand-edit generated game
logic; use `patches/` overrides. No emojis in code or documentation.
