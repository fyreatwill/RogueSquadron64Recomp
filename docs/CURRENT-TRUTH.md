# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`. Durable history is in
[`docs/PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); do not reopen closed
lineages without a new class-level lead.

Reviewed through s946 (2026-08-13). The active blocker is authoritative
FULL_SYNC/E9 accounting after the post-sec2 gate. M5 audio de-stubbing is
closed; M3 work is limited to systematic idiom-class audits.

## User directive

1. Run maintenance when this file exceeds 60,000 bytes.
2. Pursue only a genuinely new M5 audio lead; the existing campaign is closed.
3. Do M3 crash work only as complete idiom-class audits, not reactive chases.

## Current truth

- Overlay dispatch is sufficiently fixed for mission entry and post-sec2
  outdoor presentation; the original boot/menu hypothesis is closed.
- Product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations are OFF. Any new mitigation requires an `ORIGIN:` naming the
  writer and assessing legitimacy.
- Phase-gated port captures reach VI width 1024 with independent
  `emit/raw/dispatch/match` controls. Pre-chain crashes are disjoint families
  and do not classify parser loss.
- s833–s840 established exact ordinary producer/consumer task and range
  identity for late E9-bearing work, including zero synthetic markers. The
  remaining bridge/parser delta is best explained by command-boundary/span
  accounting, but the residual extended condition remains unclassified.
- s842–s853 moved candidate B4/BF ownership from Factor 5 to RDP garbage-shaped
  entries; no mitigation or legitimacy conclusion followed.
- s855–s861 showed that `0x8000834c` is a stale process-wide breadcrumb from
  `drainMeshReleaseQueue`, not attribution for `getNextSlotNpcTypeId`.
- s862–s880 found invalid port coalescer entry state, but retail remains at VI
  width 320 and the oracle has no safe post-write writer/value channel. The
  coalescer line is parked.
- s881–s938 completed a long sequence of static idiom inventories. Local
  bounds, caller shapes, and termination were classified where stated, but
  dynamic writer/value legitimacy remains unproven. s935 found a pointer/index
  mismatch in `musyxTriggerVoiceAttack`; s937 found that `musyxStopVoice` has
  one direct caller that passes constant zero, but no independent proof of
  global base/count lifecycle or register-indirect callers. s938 found one
  direct `stopVoiceByKey` caller and a bounded allocator-produced index, but
  the path uses `stopVoiceMarkRetrigger` rather than `musyxStopVoice`; active
  list pointer and base/count legitimacy remain unproven. s940 found that
  `D_8013D880` is a 32-entry `0x17C`-stride record array and that count writers
  clamp to `0..0x20`; reset/release/stop paths use `-1` for the `+0x64` handle
  sentinel and note-on constructs the handle. The four
  `stopVoicesByHandle` callers agree on linked-list node `+0x8` handles, but
  node `+0xC` index provenance and runtime value legitimacy remain unproven.
- s941 found four generated sorted-list insertion/reuse writers for node
  `+0xC`; each copies the owning voice record's `+0x64`. Unlink/reuse preserves
  the list contract, but the complete `+0x64` writer set and possible indirect
  paths do not prove every copied value is an in-range `0..31` slot index.
- s942 separated the remaining generated `+0x64` stores: reset/release/stop
  paths write the `-1` sentinel, the `tickAudioChannel` path writes `$s1` after
  reachable initialization to `-1`, and neighboring channel/fade functions
  write unrelated state fields. The sorted-node copies remain structurally
  coherent, but indirect callers/writers and the complete handle-to-slot value
  lifecycle remain unproven. H-stop-voices-by-handle-index-unclassified
  remains selected.
  H-stop-voices-by-handle-index-unclassified remains selected; no mismatch or
  mitigation conclusion followed.
- s943 audited the allocator and all four sorted-node `+0xC` writers. No
  direct generated call to `allocVoiceHandleNode` was found; the only nearby
  `jalr` is a generic comparator callback and is not proven to target it. The
  allocator at `0x80086524` and duplicated insertion/reuse bodies at
  `0x80086E40`, `0x8008738C`, and `0x800877E0` each copy a voice-record
  `+0x64` into the node. List links and handle fields are coherent, but the
  complete indirect dispatch and handle-to-slot value lifecycle remain
  unproven. H-stop-voices-by-handle-index-unclassified remains selected.
- M5 audio de-stubbing is closed. Do not reopen it without a genuinely new
  lead. M4 correctness remains parked behind the active blocker.
- s944 audited `startNoteOnVoice`: there are exactly four direct callers and no
  generated-source or companion-symbol register-indirect reference. Its return
  is the sorted-list handle counter, not the voice slot; the allocated slot is
  packed into the low byte of the voice record's composite `+0x64` handle at
  `0x80087294`. The four sorted-node `+0xC` copies preserve that full-handle
  contract, and `stopVoicesByHandle` extracts the low byte as the slot before
  validating the full handle. Runtime legitimacy of all record pointers and
  the complete indirect handle lifecycle remains unproven.
- s945 traced all four node `+0xC` copy sources. The three inline bodies at
  `0x80086E40`, `0x8008738C`, and `0x800877E0` derive the source from the
  `0x8013D880 + slot*0x17C` voice table. The standalone allocator body at
  `0x80086524` receives its source through `$a0`, but has no direct generated
  caller; the only nearby `jalr` is an unrelated comparator callback. The
  three inline sites are structurally valid; standalone reachability and any
  indirect allocator edge remain unclassified.
- s946 exhaustively searched generated audio sources, overlay metadata, and
  companion symbols for `allocVoiceHandleNode` reachability. There are no
  direct references outside its definition/registration and no audio-overlay
  `jalr` candidate besides the generic comparator callback at `0x80085C70`.
  That callback receives its target from the caller stack and is documented as
  a comparator; no caller or assignment targets the allocator. This selects
  standalone-dead at the static call-graph level, but runtime function-pointer
  reachability and handle-value legitimacy remain unproven.

## Recent evidence ledger

The detailed session records are in `PORTING-STATE.md`; durable campaign
history is in PROJECT-OVERVIEW §§27–30.

| Sessions | Result |
|---|---|
| s820–s840 | Width-1024 controls passed; ordinary producer/consumer identity matched; synthetic path absent. |
| s841–s853 | Copy/triangle candidates were RDP-owned; residual extended path remained unobserved. |
| s854–s880 | Breadcrumb, coalescer, retail-oracle, and independent-writer routes were classified or parked; no legitimacy conclusion. |
| s881–s924 | Complete M3 inventories covered model/audio/song/MusyX idioms; no behavior or mitigation changes. |
| s925–s937 | Audio filter/mixer/voice idioms were audited; see PROJECT-OVERVIEW §30. s935 rejected a shared attack-helper contract; s937 structurally passed `musyxStopVoice` but left runtime index/base legitimacy open. |
| s936 | Maintenance pass: compacted this file and migrated durable s925–s935 outcomes to PROJECT-OVERVIEW. No experiment ran. |
| s938 | `stopVoiceByKey` has one direct streamed-voice caller and coherent local index arithmetic; base/count and active-list legitimacy remain open. |
| s939 | `stopVoicesByHandle` has four direct callers in two song-list walks; handle lookup and termination are coherent, but the node `+0xC` to 8-bit voice-index contract and voice-table lifecycle remain unproven. |
| s940 | `D_8013D880`/`0x80141AD0` inventory found compatible 32-slot bounds and `-1` handle clearing across reset/release/stop paths, but did not prove node `+0xC` index provenance or runtime value legitimacy. |
| s941 | Four node `+0xC` insertion/reuse writers all copy voice `+0x64`; list links and sentinels are coherent, but complete `+0x64` provenance and indirect paths remain unclassified. |
| s942 | Classified generated `+0x64` stores by domain; voice paths are sentinel/constructed-handle or `$s1` initialized to `-1`, but indirect provenance and runtime slot legitimacy remain unproven. |
| s943 | Exhaustive source audit found the allocator plus three duplicated sorted-node insertion/reuse writers; no direct allocator call and no proven indirect edge were found, while pointer/value lifecycle remains unclassified. |
| s944 | Four direct `startNoteOnVoice` callers were found; the return is a list handle, while voice `+0x64` is a composite handle with the allocated slot in its low byte. Node `+0xC` and `stopVoicesByHandle` agree structurally; indirect pointer/lifecycle legitimacy remains open. |
| s945 | Three inline node-copy sites derive `0x8013D880 + slot*0x17C` voice records. The standalone allocator copy has no direct generated caller and receives `$a0` without a proven dispatch edge; the structural contract remains single-source and incomplete. |
| s946 | Exhaustive generated-source/overlay/companion search found no direct allocator reference and only the unrelated generic comparator `jalr`; static standalone reachability is selected dead, while runtime pointer/value legitimacy remains unproven. |

All runtime claims in the ledger had positive controls in the relevant
capture. Static single-source results are labelled as such in the session
entries and do not authorize mitigations.

## Ranked backlog

1. Continue the active M3 campaign by exhaustively classifying the remaining
   `+0x64` handle writers and any indirect audio dispatch, using the s946
   result that standalone `allocVoiceHandleNode` has no generated caller or
   allocator-targeted `jalr` as a static baseline.
2. Do not use the process-wide `0x8000834c` breadcrumb to select a crash site;
   require an independently phase-gated caller/state boundary.
3. M4 correctness: outdoor `baseFixed=-32768` zero shade, attribution S=0
   triangles, then I4 `sample=64x128`, each with independent controls.
4. Retain the regeneration delete-before-regen rule and audit fixup counts if
   a reproducible omission appears.

## Next work unit

HYPOTHESIS-ID: m3-audio-stop-voices-by-handle-contract

Audit every remaining generated writer of voice-record handle field `+0x64`
and classify whether it constructs a composite handle, writes the `-1`
sentinel, copies an already validated handle, or has unresolved provenance.
Include register-indirect audio-overlay edges and companion-symbol names.
Source-only; do not add a guard, change game behavior, build, or run a soak.

Competing hypotheses:

- H-stop-voices-by-handle-index-valid: all live `+0x64` writers preserve the
  composite-handle/sentinel contract established by note-on and stop paths.
- H-stop-voices-by-handle-index-unclassified: a candidate indirect edge or
  writer remains unresolved.
- H-stop-voices-by-handle-index-mismatch: a reachable standalone edge supplies
  a non-voice record or incompatible handle/state value.

Discriminating measurement: exhaustive `+0x64` store inventory, source/value
flow at each writer, all audio-overlay `jalr` setup, and companion-symbol
cross-check. Sentinel/constructed/copied valid values at every writer select
valid; an incompatible writer selects mismatch; unresolved source or target
selects unclassified.

Exact command: `rg -n -C 8 "0x64|0X64|64\\(" ../N64Recomp/RecompiledFuncs/funcs_21.c ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_23.c; rg -n -C 6 "jalr|80086450|allocVoiceHandleNode|80086FC4|startNoteOnVoice" ../N64Recomp/RecompiledFuncs ../rogue_squadron64/symbol_files/main_overlay.txt`, then classify every writer and edge. No game build or soak is planned.

## Closed and parked

- M5 audio (legacy campaign) is CLOSED; see `docs/M5-AUDIO-PLAN.md` and
  PROJECT-OVERVIEW §§9–12.
- Hangar-exit to sec2 is CLOSED except for the active accounting/backlog work;
  see PROJECT-OVERVIEW §27–28.
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
