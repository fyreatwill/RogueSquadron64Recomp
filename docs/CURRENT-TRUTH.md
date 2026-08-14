# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); detailed session records stay
in the ledger. Reviewed through s1073 (2026-08-14). This file is deliberately
compact and records only live conclusions, boundaries, and next work.

## Current state

- Overlay dispatch is sufficiently fixed for mission entry and post-sec2
  outdoor presentation. The original boot/menu explanation is closed.
- Product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations are OFF. Any new mitigation requires an `ORIGIN:` naming the
  writer and assessing whether the value is legitimate.
- Phase-gated port captures can reach VI width 1024 with independent
  emit/raw/dispatch/match controls. Pre-chain crashes are disjoint families;
  they do not classify parser loss.
- Ordinary late E9 producer/consumer identity is established. Synthetic
  FULL_SYNC was absent in the decisive capture. Remaining deltas are
  boundary/span-shaped and the residual extended condition is unclassified.
- The recurring `slotDispatcherIter+872` SIGBUS is the generated prologue
  spill of guest `$sp` at `funcs_8.c:22810`. All 144 direct callers have
  balanced frame shapes; statically addressed indirect targets are balanced;
  `0x8010B350` is compiled data with no generated writer. The general runtime
  caller-frame corruption mechanism remains open. A
  `ROGUESQ_LOG_SLOT_SP_GUARD=1` register dump is landed and binary-verified;
  two phase-positive no-event soaks did not classify the +872 site.
- M5 audio de-stubbing is closed. Do not reopen it without a genuinely new
  lead. Audio remains stubbed; the legacy audio audits are archived in the
  project overview.

## Retail oracle boundary

The retail oracle reaches only the width-320 attract path under the tested
Start, A, Z, hold, cadence, first-input, and 120-second schedules. The whole-
RDRAM callback control, input-edge controls, and VI callback/poll agreement
are positive. It does not reach the 512 hangar-origin phase, so no freelist
watch or hangar conclusion is valid. The local config-order explanation and
the tested timing/input-shape explanations are closed.

Static audits classify the width-320 handoff as state-shaped:

- `mainGameLoop` gates `menuOverlayInit` on `gGameSettings+0x20`; the direct
  generated writer is the constant `0x7F` reset in
  `resetMixerVolumesAndFlags`.
- `menuOverlayInit` dispatches the halfword at `0x800CFF50`; its eight
  generated callers pass `{9,2,2,3,3,8,3,3}` and use state/asset/unlock/
  counter predicates, with no local controller, timer, or demo read.
- Selector 9 calls `runMenuModelViewerScreen(0)` and writes selector 12.
  Selector 0 calls `runHangarMenuFromOverlay`; its result and exact zero
  stores are state-shaped, not direct input/demo transitions.
- The case-0 argument is byte `0x80130B40`. Generated stores are reset,
  menu/asset, save/setup, fixed-flag, or cinematic-state shaped.
- `0x80130B54` is the demo-id byte within that global. The complete generated
  alias sweep found only `cycleIdleDemoId`'s modulo-six increment and its
  internal clear. Its two callers are state/overlay paths.
- `dLevelByDemoId` at `0x800CD404` is immutable ROM-backed `.ovl.menu` data;
  ROM offset `0x1345A4` contains `00 05 07 0A 0B 11 00 00`. Overlay DMA is
  the loader; no generated population writer was found.

The s1070 bounded non-generated source audit found no host/runtime or patch
access, no overlay-loader/data write, and no direct companion access to
`0x80130B54`. The s1071 companion audit found a pointer-mediated write in
`func_800C1D3C.c:389-390`: `&D_80130B40 + 4*arg0->rest01[3]`, then XOR-write
through `->unkC`. The containing field is `+0x14` when
`arg0->rest01[3] == 2`, so `H-pointer-write` is selected. This is static
source evidence only: the runtime value of that index and whether this branch
executes remain open. The same function's indexed `->unkC` read and
`func_800C6728`'s indexed reads do not add another writer.

The s1072 caller/initializer audit found one typed initialization of
`rest01[3]`: `func_800C0084.c:793` assigns zero during HUD initialization.
No later typed write, copy, or typed caller argument establishes a value of 2;
the HUD handler is reached through the indirect raw-address dispatch documented
in s433. Raw guest writes to the corresponding struct offset remain outside the
companion field model, so this selects `H-index-open`, not `H-index-other`.

The s1073 audit of `controller_stuff/func_800B47C4.c` found the computed-base
writer: `temp_s1 = arg0 & 0xFF` at line 597, `sp138 = &D_80130B40 +
4*temp_s1` at line 640, and `sp138->unkC ^= ...` at line 1007. The companion
tree has no typed caller or initializer for this function, so it cannot prove
`temp_s1 == 2` or a non-2 value. This selects `H-temp-s1-open`; the
pointer-mediated `+0x14` writer remains possible but its runtime index and
branch execution are unclassified.

## M4 zero-shade boundary

The independent Factor 5 command reference and same-combiner/white-shade
evidence refute RT64 shade lane/order as the cause. The VTXCOLOR payload is
nonzero, while decoded shade is the fixed `0xFFFF8000` RGB /
`0x00008000` alpha sentinel. Task/root-DL and child-consumer-DL joins are
live but do not identify an individual replacement source.

The retail ROM instruction audit shows color stores at `0x1424`, `0x1428`,
and `0x1468`, but the shaded emitter at `0x1740` reads geometry/vector data
for `+0x18` and does not read color `+0x10`. Generated output preserves this
sequence; fixup does not remove a color read. VGE selects an existing lane;
it cannot synthesize the sentinel. The missing-lighting/vector numeric origin
before `vmadh v6,v4,v0` remains unresolved. The accumulator/VGE capture recipe
is closed after controlled nulls; resume only with a new discriminator or
independent ground truth. No mitigation is authorized.

## Evidence ledger

Details are in `PORTING-STATE.md`; durable summaries are in
`PROJECT-OVERVIEW.md`.

| Sessions | Durable result |
|---|---|
| s820–s880 | Post-sec2 accounting, breadcrumb, coalescer, and oracle routes were classified or parked. |
| s881–s951 | Complete M3 idiom inventories closed the audio channel-field thread. |
| s952–s983 | Dispatcher stack-spill family was localized; oracle callback work was repaired later. |
| s984–s1013 | Shade decode/source/emission audits moved M4 to the accumulator numeric-origin boundary. |
| s1014–s1038 | M4 probe phase/build controls were repaired; controlled captures remained null and the recipe closed. |
| s1039–s1047 | Retail input, cadence, timing, and callback controls were positive; attract remained width 320. |
| s1048–s1056 | Width-320 caller and selector dispatch were state-shaped; selector-0 upstream remained open. |
| s1057–s1062 | Hangar return and selector-0 argument paths were state/table-shaped with non-generated boundaries. |
| s1063–s1065 | Demo-id writer and immutable `dLevelByDemoId` ROM ownership were classified in generated/data paths. |
| s1066–s1068 | `cycleIdleDemoId` callers, clear form, and all generated aliases were audited; non-generated ownership remains. |
| s1069 | Maintenance compaction; no experiment or runtime conclusion. |
| s1070 | Non-generated host/patch/overlay search found no selector access; companion struct confirms `demoId` at +0x14. Pointer-mediated ownership remained open. |
| s1071 | Companion audit found a computed-base XOR write at `func_800C1D3C.c:389-390` that aliases +0x14 when `rest01[3]==2`; selects `H-pointer-write` (static, index value unclassified). |
| s1072 | Caller/initializer audit found the HUD constructor's zero initialization at `func_800C0084.c:793`, but no typed proof of the runtime index; `H-index-open` remains. |
| s1073 | `func_800B47C4` masks an external `arg0` into `temp_s1` before its computed-base XOR write; no companion caller proves the index, so `H-temp-s1-open` remains. |

## Ranked next steps

1. Audit raw generated stores to `0x80130B54` / `D_80130B40+0x14` that are not
   represented as named-field accesses, classifying each writer and whether
   its base/index can reach the selector byte. Keep the result static and
   source-bounded; do not build unless the source boundary becomes
   insufficient.
2. Keep the retail oracle parked until a new, falsifiable phase-path
   discriminator can reach the 512 hangar-origin phase. Do not arm the
   freelist watch from width-320 evidence.
3. Keep M4 parked unless an independent ground-truth path or a new complete
   pre/post accumulator discriminator becomes available.
4. Re-evaluate the isolated animation/frameStart SIGBUS and regeneration
   omission only when a reproducible lead appears; preserve delete-before-
   regen ordering and audit fixup counts.

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
- A null result is worthless without a positive control in the same run.
  Before any mitigation, name the writer and assess legitimacy with an
  `ORIGIN:` line.

## Closed and parked

M5 audio, overlay boot/menu, old ucode/DMA experiments, rendering dead ends,
earlier idiom campaigns, duplicate-symbol work, and the M3 audio class are
closed or archived in `PROJECT-OVERVIEW.md`. The slot-SP guard, M4 capture
recipe, and retail width-320 schedules are parked as described above.
