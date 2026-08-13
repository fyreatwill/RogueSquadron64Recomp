# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`. Durable history is in
[`docs/PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); do not reopen closed
lineages without a new class-level lead.

Reviewed through s882 (2026-08-13). The active blocker is the authoritative
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

The `tickAudioChannel` cursor inventory is shape-rejected as a whole-function
idiom and leaves the stream-pointer writer/legitimacy unproven. Do not add a
guard or change game behavior. Continue M3 with the next bounded pointer-chain
candidate, `stopSongByHandle`.

Competing hypotheses:

- H-next-class-unclassified: the next candidate has at least one pointer site
  without a proof of safety or a concrete writer/legitimacy explanation.
- H-next-class-fully-classified: every site in the next candidate is already
  proven safe, dead, or covered by an existing justified patch.
- H-next-inventory-shape-mismatch: the next ranked candidate does not define
  one coherent pointer idiom; stop rather than mixing shapes.

Discriminating measurement: a complete site table for the next coherent idiom,
including source address, checks, and writer/legitimacy basis for every hit.
Any omitted site or unproven writer rejects full classification.

Exact commands used: use `rg` to enumerate the next candidate in the external
generated tree and bounded `sed` windows around every site plus its decomp or
named-symbol counterpart. No game build or soak is planned.

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
