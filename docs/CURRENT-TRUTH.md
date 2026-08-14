# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`. Durable history is in
[`docs/PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); do not reopen closed
lineages without a new class-level lead.

Reviewed through s942 (2026-08-13). The active blocker is authoritative
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
- M5 audio de-stubbing is closed. Do not reopen it without a genuinely new
  lead. M4 correctness remains parked behind the active blocker.

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

All runtime claims in the ledger had positive controls in the relevant
capture. Static single-source results are labelled as such in the session
entries and do not authorize mitigations.

## Ranked backlog

1. Continue the active M3 campaign with a bounded audit of every callsite and
   register-indirect edge feeding `allocVoiceHandleNode` and the four node
   `+0xC` copies. Separate voice-record pointers from channel/fade structures,
   and prove whether the copied `+0x64` value is a slot index at each edge.
2. Do not use the process-wide `0x8000834c` breadcrumb to select a crash site;
   require an independently phase-gated caller/state boundary.
3. M4 correctness: outdoor `baseFixed=-32768` zero shade, attribution S=0
   triangles, then I4 `sample=64x128`, each with independent controls.
4. Retain the regeneration delete-before-regen rule and audit fixup counts if
   a reproducible omission appears.

## Next work unit

HYPOTHESIS-ID: m3-audio-stop-voices-by-handle-contract

Audit every direct and register-indirect callsite feeding
`allocVoiceHandleNode` and the four sorted handle-list node `+0xC` copies
consumed by `stopVoicesByHandle` at `0x8008DA98`. Prove the voice-record
pointer, slot-index, and handle-value domains at each edge; classify unresolved
edges as unproven. Cross-check companion decomp evidence. Source-only; do not
add a guard, change game behavior, build, or run a soak.

Competing hypotheses:

- H-stop-voices-by-handle-index-valid: every `+0x64` value copied into node
  `+0xC` is a bounded 32-slot index, with compatible allocator and reuse paths.
- H-stop-voices-by-handle-index-unclassified: one or more `+0x64` writers,
  indirect paths, or value domains remain unproven.
- H-stop-voices-by-handle-index-mismatch: a writer or caller uses an
  incompatible handle/state value, index domain, or node layout.

Discriminating measurement: an exhaustive generated-source inventory of every
`allocVoiceHandleNode` call, register-indirect dispatch edge, voice-record
pointer derivation, node `+0xC` copy, and list termination, plus a decomp-symbol
cross-check. A proven bounded index at every reachable copy selects valid; a
non-index value selects mismatch; an unresolved edge selects unclassified.

Exact command: `rg -n -C 8 "allocVoiceHandleNode|80086450|80086534|80086FC4|8008DA98|0x18\\)|0x64\\(|0xC\\(" ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/main_overlay.txt`, then classify each callsite and edge. No game build or soak is planned.

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
