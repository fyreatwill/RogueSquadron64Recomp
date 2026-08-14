# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`. Durable history is in
[`docs/PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); do not reopen closed
lineages without a new class-level lead.

Reviewed through s936 (2026-08-13). The active blocker is authoritative
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
- s881–s935 completed a long sequence of static idiom inventories. Local
  bounds, caller shapes, and termination were classified where stated, but
  dynamic writer/value legitimacy remains unproven. The latest finding is the
  s935 pointer/index contract mismatch in `musyxTriggerVoiceAttack`.
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
| s925–s935 | Audio filter/mixer/voice idioms were audited; see PROJECT-OVERVIEW §30. The latest result rejects a single shared voice-index contract. |
| s936 | Maintenance pass: compacted this file and migrated durable s925–s935 outcomes to PROJECT-OVERVIEW. No experiment ran. |

All runtime claims in the ledger had positive controls in the relevant
capture. Static single-source results are labelled as such in the session
entries and do not authorize mitigations.

## Ranked backlog

1. Continue the active M3 campaign with the complete `musyxStopVoice` idiom
   audit below; require every reference, caller contract, access range, and
   termination path to be classified.
2. Do not use the process-wide `0x8000834c` breadcrumb to select a crash site;
   require an independently phase-gated caller/state boundary.
3. M4 correctness: outdoor `baseFixed=-32768` zero shade, attribution S=0
   triangles, then I4 `sample=64x128`, each with independent controls.
4. Retain the regeneration delete-before-regen rule and audit fixup counts if
   a reproducible omission appears.

## Next work unit

HYPOTHESIS-ID: m3-audio-voice-stop-contract

Audit the complete `musyxStopVoice` idiom at `0x80092368` in
`../N64Recomp/RecompiledFuncs/funcs_24.c`, including every generated caller,
the relationship between pointer/index arguments, voice-slot arithmetic,
state writes, existing guard coverage, and sibling callers in the same audio
paths. Source-only; do not add a guard, change game behavior, build, or run a
soak.

Competing hypotheses:

- H-voice-stop-unclassified: a caller supplies an invalid voice index/base, or
  the stop target escapes its intended mixer record.
- H-voice-stop-classified: callers agree on a bounded mixer index and existing
  guards cover the base/index contract.
- H-voice-stop-shape-mismatch: callers use pointer and index contracts that
  must be translated or are distinct; record the exact split and stop.

Discriminating measurement: enumerate every reference and caller register
setup, inspect the complete callee and all state/slot accesses, derive every
address range and termination path, classify every helper edge, and
cross-check `main_overlay.txt` plus the two caller chains identified in s935.
Any pointer/index split, uncovered derived access, or unproven termination
path rejects classification.

Exact command:
`rg -n -C 12 "musyxStopVoice|80092368|92368" ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/main_overlay.txt`,
then inspect the complete helper and every caller. No game build or soak is
planned.

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
