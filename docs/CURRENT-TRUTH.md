# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`. Durable history is in
[`docs/PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); do not reopen closed
lineages without a new class-level lead.

Reviewed through s912 (2026-08-13). The active blocker is the authoritative
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

All runtime claims above had positive controls in the relevant capture. A
single-source result is explicitly labelled in the archived session entry;
none authorizes a mitigation.

## Ranked backlog

1. Do not use the process-wide `0x8000834c` breadcrumb to select a helper crash
   site; require a new independently phase-gated caller/state boundary.
2. Continue M3 only as complete idiom inventories with every site classified
   and proof/guard per site. Queue passive breadcrumbs as soaks.
3. M4 correctness: outdoor `baseFixed=-32768` zero shade, attribution S=0
   triangles, then I4 `sample=64x128`, each with independent controls.
4. Retain the regeneration delete-before-regen rule and audit fixup counts if
   a reproducible omission appears.

## Next work unit

HYPOTHESIS-ID: m3-idiom-inventory-next

Audit the next adjacent audio function, `getVoicePlaybackProgressByKey`
(`0x8009B8A8`), as a complete generated function. Do not add a guard or
change game behavior.

Competing hypotheses:

- H-voice-progress-unclassified: the helper has an unchecked or
  aliasing-sensitive slot/table access whose writer/initialization obligation
  cannot be classified from the function and sibling writers.
- H-voice-progress-fully-classified: all slot/table reads and writes are
  bounded by the function's controls, and its callers agree on the same
  layout.
- H-voice-progress-shape-mismatch: callers use incompatible layouts or the
  helper's output aliases a state structure; record the exact split and stop.

Discriminating measurement: a complete site table for
`getVoicePlaybackProgressByKey`,
every slot/list load/store and control operation, all generated callers, and the
companion symbol/decomp basis. Any omitted access or incompatible caller shape
rejects full classification.

Exact commands: use `rg` to enumerate `serviceVoicePoolFrame` and its callsites in
`../N64Recomp/RecompiledFuncs/funcs_26.c`, then bounded `sed` windows and the
companion `rogue_squadron64` symbol/decomp files. No game build or soak is
planned.

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
