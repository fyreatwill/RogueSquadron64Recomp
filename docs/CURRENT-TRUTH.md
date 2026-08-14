# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`docs/PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); detailed session records
remain in the ledger. This file was compacted in the s1004 maintenance pass
from 60,345 bytes / 642 lines. It is intentionally a current-state document,
not a second ledger.

Reviewed through s1006 (2026-08-14). The active investigation is M4
zero-shade source-to-consumer association. M5 audio de-stubbing is closed.
M3 work is limited to complete idiom-class audits. The retail-oracle callback
thread is blocked on directory access and is not the current work unit.

## Current truth

- Overlay dispatch is sufficiently fixed for mission entry and post-sec2
  outdoor presentation; the original boot/menu hypothesis is closed.
- Product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations are OFF. Any new mitigation requires an `ORIGIN:` naming the
  writer and assessing legitimacy.
- Phase-gated port captures reach VI width 1024 with independent
  `emit/raw/dispatch/match` controls. Pre-chain crashes are disjoint families
  and do not classify parser loss.
- Ordinary late E9 producer/consumer identity is established; synthetic
  FULL_SYNC was absent in the decisive capture. Remaining accounting deltas
  are boundary/span-shaped and the residual extended condition is unclassified.
- The recurring `slotDispatcherIter+872` SIGBUS is the generated prologue
  spill of guest `$sp` at `funcs_8.c:22810`. All 144 direct callers have
  balanced frame shapes; statically addressed indirect targets are balanced;
  `0x8010B350` is compiled data with no generated writer. The general runtime
  caller-frame corruption mechanism remains open, but no static lead is queued.
- M5 audio de-stubbing is closed. Do not reopen it without a genuinely new
  lead. The legacy audio idiom audits and their structural limitations are in
  PROJECT-OVERVIEW §§9–12 and §30.
- Retail oracle work is blocked: `/Users/williambuckley/Documents/Tools/rs64-oracle`
  is outside the permitted directory set. s982 localized its corrected-core
  failure to dereferencing `r4300_pc(r4300)` in `read_with_bp_checks` before
  callback entry. No retail phase conclusion or recomp mitigation follows.

## M4 zero-shade evidence

The independent F5 command-reference audit and same-combiner/white-shade A/B
evidence agree that RT64's shade decode lane order is not the cause. Phase-6
VTXCOLOR payloads are nonzero while decoded shade is exact ZERO. The observed
source population is mixed: some payload addresses have exact generated CPU
writes, including later phase-6 sources, while other nonzero sources have no
generated-store overlap. The instrumented DMEM-to-RDRAM DMA path had no overlap
with sampled target ranges. Page-fault census and static PC classification do
not identify a single target-byte writer. No mitigation is authorized from
these facts.

The provenance campaign now establishes:

- F5 payload rows carry task serial, root DL, command address, and task-global
  VTXCOLOR ordinal.
- RT64 shade and zero-shade rows carry task/DL-local ordinals and DL starts.
- F5 root DL is not the RT64 consumer DL. Zero-shade rows repeat on child DLs
  within one task, so the observed association is child-DL-shaped.
- s1003 added accepted DPC first/last ranges and aggregate physical bounds.
  In a valid capture, zero-shade task 193 had root `0x73E7C8`, bounds
  `[0x4B7800,0x4C9318)`, and consumer DLs `0x4B7930`, `0x4B7BE8`, and
  `0x4B8B28`, all inside those bounds. This selects only
  `H-dpc-range-contains-consumer`; it does not identify the F5 update feeding
  an individual replacement.

- s1005 added accepted submit serial/range fields directly to RT64 shade rows.
  The valid VI-1024 capture produced positive and zero rows with nonzero
  serials and ranges. Zero-shade task 194 used serial 49346 and consumer range
  `[0x4B7990,0x4B7C88)`, while its accepted F5 task bounds were
  `[0x4B7800,0x4B7EA0)`. The consumer range begins at the child DL and is
  contained by the task bounds; it does not identify an individual F5 VTXCOLOR
  source update. This selects `H-child-range-only`. No mitigation follows.

- s1006 added a diagnostic join at RT64's actual triangle parse site. The
  valid VI-1024 capture produced 25 join rows, including positive and
  zero-shade rows, with task, child DL, shade ordinal, submit serial/range,
  and F5 state. Zero-shade task 193 rows on child DLs `0x4B7930` and
  `0x4B7BE8` repeatedly carried the same last F5 state (`ord=30`, source
  `0x7403A8`). The rows are live and stable but still task/child-DL-shaped;
  they do not identify the individual update feeding a replacement. This
  selects `H-child-range-only`. No mitigation follows.

All runtime claims above had positive controls in their relevant captures.
Static single-source claims are explicitly described as such in the ledger.

## Recent evidence ledger

Details are in `PORTING-STATE.md`; durable summaries are in
`PROJECT-OVERVIEW.md` §31.

| Sessions | Durable result |
|---|---|
| s820–s880 | Post-sec2 accounting, breadcrumb, coalescer, and oracle routes were classified or parked; no legitimacy conclusion. |
| s881–s951 | Complete M3 idiom inventories closed the audio channel-field thread; no mitigation. |
| s952–s983 | Dispatcher stack-spill family was localized; oracle callback work became blocked after s982. |
| s984 | F5/RT64 shade decode layout audit refuted lane/order defect; upstream shade-state or lighting remains. |
| s985–s990 | Payload/source census, DMA census, page-fault census, and host-PC mapping ruled out the instrumented DMA path and a universal direct-writer explanation. |
| s991–s995 | Regeneration-owned generated-store instrumentation established generated ownership for some rows and bounded values, not a universal writer. |
| s996–s999 | Source ownership is mixed; task-scoped provenance showed the zero-shade source-to-replacement join was still missing. |
| s1000–s1001 | F5 ordinals reset at RT64 DL boundaries; root-DL identity does not join to child consumer DLs. |
| s1002 | Root-DL validation retries were invalid before VI-1024; no conclusion changed. |
| s1003 | Accepted DPC bounds contained all observed repeated RT64 consumer DLs in a valid capture; individual source mapping remains open. |
| s1005 | RT64 shade rows carried accepted serial/range fields; consumer ranges were child-DL-shaped and did not identify an individual F5 source update. |
| s1006 | RT64 triangle-parse join rows carried the live last F5 state, but repeated zero-shade child DLs shared one task-level state; individual source mapping remains open. |

## Ranked backlog

1. Continue the M4 source-to-consumer join by correlating ordered F5 VTXCOLOR
   state with emitted RDP triangle consumers; the accepted range alone is
   child-DL-shaped.
2. Keep the `slotDispatcherIter+872` runtime `$sp` corruption family parked
   until an independent runtime boundary is available; do not perform another
   static sweep without a new idiom class.
3. Once directory access is restored, resume the blocked oracle callback audit
   exactly as documented in the archived s983 work unit. Do not self-grant
   access or infer a retail phase result.
4. Preserve regeneration delete-before-regen ordering and audit fixup counts
   if a reproducible omission appears.

## Next work unit (s1007)

HYPOTHESIS-ID: m4-zero-shade-source-consumer-join

Add one bounded event-order trace that records every F5 VTXCOLOR update as a
task-local sequence and records that sequence at each RT64 triangle parse,
alongside the existing shade serial/range rows. Preserve existing join rows.
Do not add a mitigation or hand-edit generated files.

Competing hypotheses and the discriminating measurement:

- `H-triangle-source-join`: ordered F5 VTXCOLOR events and emitted triangle
  rows identify the source update feeding a zero-shade replacement.
- `H-child-range-only`: the consumer remains associated only with its child DL.
- `H-triangle-source-missing`: the event stream is not live at triangle
  emission or has no usable ordered join.

The discriminating table must key task, F5 root DL, F5 update ordinal/source,
triangle emission order, submit serial/range, RT64 DL, and shade ordinal. It is
invalid unless positive controls, root identity, triangle rows, range-bearing
shade rows, and zero-shade rows all fire in the VI-1024-gated phase.

Exact launch recipe:

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VTX_GENERATED_WRITES=1 ROGUESQ_LOG_VTX_WRITE_FAULT=1 ROGUESQ_LOG_F5_STATE=1 ROGUESQ_LOG_SHADE_RAW=1 ROGUESQ_LOG_TRI_WRITER=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a' zsh tools/probe.sh scratch/agent/s1007_f5_event_order_20260814 180 3`

An individual F5 source appearing immediately before the consumer triangle
selects `H-triangle-source-join`; only child-DL association selects
`H-child-range-only`; absent/unstable state selects `H-triangle-source-missing`.
If controls fail, record the run as invalid and make no causal selection.

## Method and safety rules

- Before runtime instrumentation, consult `tools/oracle/README.md` and
  `docs/F5-UCODE-REFERENCE.md`; arm a whole-RDRAM positive control.
- Gate animated comparisons on VI transitions; scope counters and log budgets
  to the phase; batch all instrumentation into one build/run.
- Use SIGKILL, launch from `build/`, and use capture paths whose final
  component does not begin with `.`. Queue repeat soaks rather than babysit.
- Diagnostics in generated code belong in fixup scripts. Regeneration order is
  `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then CMake.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. Changes under `lib/` require patch export.

## Closed and parked

M5 audio, overlay boot/menu, old ucode/DMA experiments, rendering dead ends,
earlier idiom campaigns, duplicate-symbol work, and the M3 audio class are
closed or archived in PROJECT-OVERVIEW. Parked items include intermittent
regeneration omission, isolated animation/frameStart SIGBUS reports, the M3
DoD gate, and M4 band-row coverage.
