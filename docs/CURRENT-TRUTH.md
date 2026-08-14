# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); detailed session records stay
in the ledger. Reviewed through s1104 (2026-08-14). This file is deliberately
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
- The s1084-s1087 retail oracle runs passed the whole-RDRAM positive control,
  showed all eleven Start presses in PIF reads, and advanced 7,199 VI frames
  while remaining at width 320/origin `0x006dd280`. No read or write hit
  `0x130B30:0x130B31` in s1085 and the full block in s1086. These
  single-source oracle results now select `H-pre-main-loop-state-gate` for the
  established schedule: `0x8003E010` executed once, but `0x8003E07C` did not.
  The s1090 dense bracket reached `0x8006D9B0` once, but none of the post-loop
  PCs `0x8006D9C0`, `0x8006D9D0`, `0x8006D9E0`, `0x8006D9F0`, `0x8006DA10`,
  `0x8006DA30`, `0x8006DA50`, or `0x8006DA70` fired; continuation, gate, and
  later milestones remained silent. The s1091 branch bracket then hit
  `0x8006D9B4` once while `0x8006D9B8` and `0x8006D9BC` stayed silent. This
  selects single-source `H-branch-delay-boundary`; whether the PC callback
  omits a MIPS delay-slot execution or the retail path branches back before
  the later body remains open.

The s1092 retail oracle capture added the statically identified taken target
and nearby loop PCs. Controls remained positive: whole-RDRAM reached 10,015
callbacks, all eleven Start presses were observed in PIF reads, and VI reached
7,204 at width 320/origin `0x006dd280`; the mission-state block was silent.
`0x8006D9B4` hit once and `0x8006D980` hit twice; nearby even loop PCs
`0x8006D988` through `0x8006D9A8` each hit twice, while `0x8006D9B8`,
`0x8006D9BC`, all odd nearby PCs, and all post-loop PCs remained silent. This
selects single-source `H-taken-target`: retail execution reaches the taken
loop target, and the remaining delay-slot distinction is an oracle callback
coverage question rather than an unresolved branch target. The s1093 source
audit resolves that question: the oracle forces `R4300Emulator=0`, so
`run_pure_interpreter` calls `update_debugger(current PC)` before each
top-level instruction, while `DECLARE_JUMP` recursively executes the delay
slot without another debugger update. `--watch-pc` maps each requested PC to
the exact half-open range `[pc, pc+4)`. Thus zero PCs that are delay slots are
callback omissions by construction; non-delay PCs remain valid retail
evidence.

The s1094 ROM/generated audit classifies the full `0x8006D980..0x8006D9BC`
bracket. The generated function and raw ROM agree under an independent
`ROM = VRAM - 0x80000000 + 0xC00` mapping. `0x8006D9B8` is the `bne` delay
slot and can be absent from the oracle callback stream, but `0x8006D9BC` is
the ordinary fall-through `addiu`, not a delay slot. This supersedes the
broader s1093 implication that the remaining zero PCs could all be callback
omissions: the delay-slot explanation remains valid for `9B8`, while `9BC`
requires a branch-taken/runtime explanation.

The s1095 established-schedule retail oracle run passed the whole-RDRAM,
eleven-Start/PIF, and VI controls: 10,000 positive-control callbacks, all
eleven presses, and 7,198 VI frames in 120 seconds at width 320/origin
`0x006dd280`. Execution watches recorded `0x8006D9B0=1`, `0x8006D9B4=1`, and
`0x8006D9BC=0`. This single-source runtime result selects `H-taken-branch`:
the compare's taken path explains the absent ordinary fall-through PC. The
initial attempt was truncated before its 120-second completion and is invalid;
the full rerun is the usable capture.

The s1096 static audit closes the branch-target classification. The preserved
generated snapshot and independently mapped retail ROM agree word-for-word from
`0x8006D980` through `0x8006D9C8`. `0x8006D9B4` is `bne $v0,$zero,0x8006D980`;
the taken target increments `$s0`, executes the six input/frame submission
calls at `0x8006D988`–`0x8006D9AC`, and returns to the compare at
`0x8006D9B0`. The target is therefore a valid loop-back, not an exit or a
generated/ROM mismatch. The non-taken path begins at `0x8006D9B8`'s delay-slot
instruction and continues through the cleanup path at `0x8006D9BC`.

## Retail oracle boundary

The retail oracle reaches only the width-320 attract path under the tested
Start, A, Z, hold, cadence, first-input, and 120-second schedules. The whole-
RDRAM callback control, input-edge controls, and VI callback/poll agreement
are positive. It does not reach the 512 hangar-origin phase, so no freelist
watch or hangar conclusion is valid. The local config-order explanation and
the tested timing/input-shape explanations are closed.

Static audits classify the width-320 handoff as state-shaped:

- `mainGameLoop` gates `menuOverlayInit` on byte `0x80130B30`, which is
  `D_80130B10+0x20` in the mission-state block, not `gGameSettings+0x20`.
  `runIdleFramesAndLoadSaveData` has a direct generated writer at
  `0x8006DAB8` that stores constant `1`; `resetGameSettingsAndMissionStats`
  clears the containing 0x28-byte block first. Static ownership is therefore
  `H-gate-writer`; runtime reachability/value and any later raw alias remain
  open.
- The s1081 bounded path audit found one generated caller of
  `runIdleFramesAndLoadSaveData`: `mainGameLoop` at `0x8003E010`. Its 32-frame
  loop and all save-load/pending-save branches rejoin the common tail; after
  `resetGameSettingsAndMissionStats` clears `D_80130B10`, the unconditional
  `0x8006DAB8` store writes `1` to `0x80130B30` before return. The companion
  symbol annotation independently records reset-before-save-load ordering.
  This selects static `H-writer-reached` and rules out a generated
  caller/early-exit path that leaves the reset zero. Runtime execution, later
  clobbers, and overlay/alias reachability remain open.
- The s1082 post-return alias census found 67 generated `MEM_B(0x20, ...)`
  sites, but no concrete write to `0x80130B30` after
  `runIdleFramesAndLoadSaveData` returns and before the `mainGameLoop` read at
  `0x8003E07C`. The only exact generated target is the known
  `0x8006DAB8` store inside that callee; intervening main-loop writes target
  unrelated globals, and the companion tree has no assignment to the target
  byte. This selects static `H-no-later-clobber`; overlay-loader/DMA ownership
  remains outside this generated/companion source census.
- The s1083 loader audit found that all three `loadOverlay` cases DMA overlay
  code to `0x800A5130` and clear BSS at `0x8010B6D0`, `0x800CD520`, or
  `0x800B0940`; none can target `0x80130B30`. The host PI path forwards the
  descriptor's DRAM destination unchanged. This selects static
  `H-loader-no-alias`; runtime execution/value remains open.
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

The s1075 generated caller/raw-dispatch audit found one direct call, at
`funcs_34.c:11137-11140`: `func_800C5B44` invokes the actual handler entry
`menuControllerInput` at `0x800B47D0` with `a0 = 0`, proving index 0 for that
path. No other generated or raw `0x800B47C4/0x800B47D0` references exist;
`0x800B47C4` is only the 12-byte `fake_func` splat trampoline registered in
the menu overlay. This rules out a generated caller selecting index 2, but
does not classify an untyped guest entry into the companion's nominal
`func_800B47C4` path.

The s1076 oracle design audit found one phase-gated discriminator that keeps
the closed eleven-Start schedule: combine the whole-RDRAM, PIF, and VI
callback/poll controls with physical write watches on controller edge storage
(`0x13A960..0x13A970`) and the selector/state family
(`0x130B40..0x130B58`). Edge writes without selector writes select a state
gate; both write classes without hangar-origin 512 select a downstream state
gate; absent edge writes with positive PIF selects an execution/alias boundary;
selector writes plus `0x6abxxx` 512 solves the route. This is a design result,
not runtime evidence.

The s1077 retail run passed all positive controls: the whole-RDRAM watch reached
its 10,000-hit cap, PIF traces showed the injected Start bit at all eleven
scheduled presses, and VI callback/poll traces agreed while advancing 7,199
frames. Neither controller-edge storage (`0x13A960..0x13A970`) nor selector/
state storage (`0x130B40..0x130B58`) was written. VI remained width 320 with
origin `0x006dd280` through 120 seconds. This is a single-source oracle result
with independent control and target-watch lines: it selects the
`H-oracle-route-open` branch, because positive PIF delivery does not reach the
expected edge-storage writer. Another input schedule is not discriminating;
the missing observation is a read watch or guest execution breakpoint on the
consumer/alias path.

The s1078 retail read-watch run added physical reads on
`0x13A960..0x13A970` and `0x130B40..0x130B58` to the same eleven-Start
schedule. Whole-RDRAM callbacks reached the 10,000-hit cap, PIF traces showed
all eleven injected Start edges, and VI callback/poll traces agreed for 7,198
frames. Neither target range was read, and VI remained width 320 at
`0x006dd280`. Under the predeclared discriminator this selects
`H-consumer-not-reached`: positive PIF delivery does not reach the expected
consumer reads before the attract loop. This is a single-source retail-oracle
result with independent positive-control lines; it does not identify which
state gate prevents the consumer path.

The s1079 static consumer-boundary audit enumerated 55 generated direct calls to
`getControllerNewButtonsPressed` across 16 generated function names (including
the duplicate `static_5_800AF6AC` copy). The menu/controller handler
has exactly one generated direct caller: `menuOverlayInit` at `0x800C5B44`, which
passes `a0=0`; `0x800B47C4` is only the preceding `fake_func` splat trampoline.
No raw generated, companion, or patch dispatch target for `0x80079F50`,
`0x800B47C4`, or `0x800B47D0` was found. `mainGameLoop` conditionally enters
`menuOverlayInit` through the state/asset byte at its `0x8003E07C` gate, and
`menuOverlayInit` then selects its handler through the selector jump table at
`0x800C5A7C`. This selects `H-gate-state` at static-source level; the runtime
value/ownership of the gate remains open.

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
| s1074 | Complete generated raw `MEM_B(0X14, ctx->rN)` census found 31 stores. Only the two `cycleIdleDemoId` stores use the fixed selector base; the other 29 use object/argument/stack-derived bases. No additional generated writer reaches `0x80130B54`; the non-generated/index-mediated boundary remains open. |
| s1075 | The only generated call to the actual `menuControllerInput` entry passes `a0=0`, selecting masked index 0; no raw dispatch entry targets `0x800B47C4/0x800B47D0`. The generated caller class is non-2, while an untyped guest-entry possibility remains single-source open. |
| s1076 | Designed a same-run retail discriminator joining controller-edge writes, selector/state writes, PIF reads, whole-RDRAM callbacks, and VI phase transitions. No run was performed; the route remains open pending this measurement. |
| s1077 | Ran the eleven-Start discriminator: whole-RDRAM, PIF, and VI controls were positive; both target write ranges were silent and VI stayed width 320 at `0x006dd280`. Selected the execution/alias observation boundary; another schedule is not justified. |
| s1078 | Added physical read watches for the controller-edge and selector/state ranges. Whole-RDRAM, eleven PIF Start edges, and VI callback/poll controls were positive; both reads were silent and VI stayed width 320 at `0x006dd280`. Selected `H-consumer-not-reached`; the blocking state gate remains open. |
| s1079 | Enumerated 55 generated controller-consumer calls across 16 generated function names (one duplicate copy) and one direct `menuControllerInput` caller (`menuOverlayInit`, `a0=0`); no raw target dispatch exists. `mainGameLoop`'s state/asset gate at `0x8003E07C` precedes the menu selector jump table. Selected static `H-gate-state`; runtime gate ownership/value remains open. |
| s1080 | Bounded static gate audit identified `s4=0x80130B10`, so `0x8003E07C` reads `0x80130B30` (`D_80130B10+0x20`). `runIdleFramesAndLoadSaveData` stores constant `1` at `0x8006DAB8`; the reset routine clears the 0x28-byte containing block. Generated and companion evidence selects static `H-gate-writer`; runtime execution/value remains open. |
| s1081 | Bounded audit found the sole generated caller at `mainGameLoop:0x8003E010`; all save-loop branches rejoin the common tail, and the unconditional `0x8006DAB8` store writes `1` after reset. Companion ordering annotation agrees. Selects static `H-writer-reached`; later clobbers and runtime reachability remain open. |
| s1082 | Complete post-return generated/companion alias census found 67 offset-`0x20` byte stores but no concrete `0x80130B30` writer after `runIdleFramesAndLoadSaveData` and before the `0x8003E07C` gate read. The only exact target is the known in-callee `0x8006DAB8` store; main-loop writes are unrelated. Selects static `H-no-later-clobber`; loader/DMA ownership remains outside the source census. |
| s1083 | Bounded `loadOverlay`/DMA audit found fixed overlay code destination `0x800A5130` and BSS clears at `0x8010B6D0`, `0x800CD520`, and `0x800B0940`; host PI forwards these destinations and does not synthesize a target write. Selects static `H-loader-no-alias`; runtime gate value/reachability remains open. |
| s1084 | Retail oracle with whole-RDRAM control, eleven Start/PIF controls, and `0x130B30:0x130B31` write watch reached 7,199 VI frames but stayed at width 320/origin `0x006dd280`; target writes were zero. Selects single-source `H-gate-not-reached`; the blocking gate is still unresolved. |
| s1085 | Repeated the established retail oracle schedule with the same controls and a physical read/write watch on `0x130B30:0x130B31`; whole-RDRAM reached 10,000 hits, all eleven PIF Start presses arrived, VI reached 7,199 at width 320, and the target watch had zero hits. This independently selects single-source `H-gate-not-reached`; the gate read itself was not reached. |
| s1086 | Repeated the established oracle schedule with a physical read/write watch on the full `0x130B10:0x130B58` mission-state block. Whole-RDRAM reached 10,000 hits, all eleven PIF Start presses arrived, VI reached 7,199 at width 320/origin `0x006dd280`, and the full block had zero hits. This selects single-source `H-gate-not-reached` and rules out any access to this state object on the tested retail route. |
| s1087 | Added guest-PC execution watches to the oracle and ran the established schedule. Whole-RDRAM reached 10,000 callbacks, all eleven PIF Start presses arrived, and VI reached 7,198 at width 320/origin `0x006dd280`; `0x8003E010` hit once, `0x8003E07C` hit zero times, and the mission-state block remained silent. This selects single-source `H-pre-main-loop-state-gate`: the preceding transition executes, but the gate read is not reached. |
| s1088 | Ran the bracketed retail execution capture with entry `0x8006D900`, continuation `0x8003E018`, and gate `0x8003E07C`. Whole-RDRAM reached 10,001 callbacks, all eleven PIF Start presses arrived, and VI reached 7,197 at width 320/origin `0x006dd280`; hits were `1/0/0`, and the mission-state block was silent. Selects single-source `H-callee-does-not-return`; the exact internal loop/subcall boundary remains open. |
| s1089 | Ran the established eleven-Start retail-oracle capture with whole-RDRAM, mission-state, VI, PIF, entry/continuation/gate, and four internal milestone watches. Controls were positive: whole-RDRAM reached 10,002 callbacks, PIF delivered all eleven presses, and VI reached 7,205 at width 320/origin `0x006dd280`. PC hits were `0x8006D900=1`, `0x8006D9B0=1`, and `0x8006DA7C=0`, `0x8006DAB8=0`, `0x8006DAF0=0`, `0x8003E018=0`, `0x8003E07C=0`; the mission-state block was silent. Selects single-source `H-save-tail-boundary`: the callee reaches the first internal milestone but not the save/load-tail milestones. It rules out callee non-entry and a failed positive-control/watch setup, but does not identify the subcall or loop body that blocks before `0x8006DA7C`. |
| s1090 | Rebuilt the retail oracle after increasing watch capacity from 16 to 24 (the planned 17-watch discriminator otherwise failed before emulation), then ran the established eleven-Start capture with whole-RDRAM, mission-state, VI, PIF, entry/continuation/gate, four milestones, and eight post-loop bracket PCs. Controls were positive: whole-RDRAM reached 10,002 callbacks, PIF delivered all eleven presses, and VI reached 7,199 at width 320/origin `0x006dd280`; the mission-state block was silent. Hits were `0x8006D900=1`, `0x8006D9B0=1`, all eight post-loop PCs `=0`, `0x8006DA7C=0`, `0x8006DAB8=0`, `0x8006DAF0=0`, `0x8003E018=0`, and `0x8003E07C=0`. Selects single-source `H-loop-exit-path`: the callee reaches the loop-boundary compare but not `0x8006D9C0`; the exact branch/delay-slot boundary remains open. |
| s1091 | Ran the established eleven-Start retail-oracle capture with whole-RDRAM, mission-state, VI, PIF, entry/continuation/gate, four milestones, eight post-loop PCs, and three branch-region PCs. Controls were positive: whole-RDRAM reached 10,003 callbacks, PIF delivered all eleven presses, and VI reached 7,204 at width 320/origin `0x006dd280`; the mission-state block was silent. Hits were `0x8006D900=1`, `0x8006D9B0=1`, `0x8006D9B4=1`, while `0x8006D9B8=0`, `0x8006D9BC=0`, all eight post-loop PCs `=0`, `0x8006DA7C=0`, `0x8006DAB8=0`, `0x8006DAF0=0`, `0x8003E018=0`, and `0x8003E07C=0`. Selects single-source `H-branch-delay-boundary`; the remaining distinction is oracle delay-slot callback behavior versus a taken branch target. |

| s1092 | The initial planned run was rejected by the oracle's 24-watch capacity; increasing the front-end capacity to 64 and rerunning the same capture passed controls: whole-RDRAM 10,015 callbacks, eleven PIF Start presses, and 7,204 VI frames at width 320/origin `0x006dd280`. `0x8006D9B4` hit once, `0x8006D980` twice, and nearby even loop PCs `0x8006D988`–`0x8006D9A8` twice each; `0x8006D9B8`, `0x8006D9BC`, odd nearby PCs, and post-loop PCs were zero. Selects single-source `H-taken-target`; delay-slot callback coverage remained open pending source audit. |
| s1093 | Audited the retail oracle source. `R4300Emulator=0` selects `run_pure_interpreter`, whose loop calls `update_debugger` before each top-level instruction; `DECLARE_JUMP` recursively executes the delay slot without another debugger update. `--watch-pc` uses `[pc,pc+4)`, so zero PCs that are delay slots are callback omissions by construction. This established the callback arm for delay slots, while non-delay PCs remained unresolved. |
| s1094 | Static ROM/generated audit classified every PC from `0x8006D980..0x8006D9BC`. The independent ROM mapping matched all generated words; `0x8006D9B8` is the `bne` delay slot, but `0x8006D9BC` is ordinary fall-through code. Selects `H-nondelay-missing` for the zero `9BC` watch and leaves only the runtime taken-vs-fall-through question. |
| s1095 | Full established-schedule retail oracle rerun passed controls: whole-RDRAM 10,000 callbacks, eleven PIF Start presses, and 7,198 VI frames at width 320/origin `0x006dd280`. Execution hits were `0x8006D9B0=1`, `0x8006D9B4=1`, and `0x8006D9BC=0`. Single-source runtime result selects `H-taken-branch`; the initial truncated attempt was invalid. |
| s1096 | Bounded static audit used the preserved generated snapshot and retail ROM. All words `0x8006D980..0x8006D9C8` matched under `ROM = VRAM - 0x80000000 + 0xC00`; the `0x8006D9B4` target increments `$s0`, runs the six frame/input calls, and loops back to `0x8006D9B0`. Selects `H-target-loop`, rules out `H-target-exit` and `H-static-mismatch`; no runtime code or mitigation changed. |
| s1097 | Bounded generated/companion audit found one normal `submitGfxFrame` epilogue and explicit continuations at all nine caller sites, but also reachable blocking `osRecvMesg(..., MQ_BLOCK)` calls at `0x8000C0B4` and `0x8000C2B8`. Selects `H-submit-nonreturn` as a legitimate wait boundary while retaining the independent fact that the audited idle-loop invocation returned once; no build, runtime code, or mitigation changed. |
| s1098 | Bounded queue-contract audit maps `0x8000C0B4` to `D_8011A818` and `0x8000C2B8` to `D_8011A7E8`; both are `osRecvMesg(..., BLOCK)`. Generated/companion evidence identifies consumers but no matching in-tree producer for either wait: the first is an external SP-completion boundary, and the second depends on host DP forwarding documented in the architecture notes. Selects `H-queue-unmatched`; no build, runtime code, or mitigation changed. |
| s1099 | Bounded host/runtime audit found that HLE and LLE SP completion plus HLE DP completion all enqueue through `events_context.sp/.dp`, populated dynamically by `osSetEventMesg`; no host producer hard-codes either guest queue. The exact `0x8011A818`/`0x8011A7E8` registration mapping is unresolved and becomes the next runtime-trace discriminator. No build, run, or mitigation changed. |
| s1100 | Batched phase-gated host trace passed VI-1024 and 413 positive E9 provenance rows. SP registered and completed on `0x8011A420` with message `0x80128C70`; DP registered and completed on `0x8011A408` with message `0`. Both pairs fired repeatedly and matched internally, but neither target is the blocking consumer pair `0x8011A818`/`0x8011A7E8`. Selects wrong-target/unwired SP and DP routes, rules out missing host completion calls, and supersedes s1099's unresolved registration mapping. |
| s1101 | Bounded generated-source audit enumerated all five `osSetEventMesg` calls. SP event 4 registers `D_8011A420`, which is directly created with count 8; the same scheduler then separately creates/uses `D_8011A818`. DP event 9 registers `D_8011A408`, directly created with count 1; its handler separately creates `D_8011A7E8`, the blocking `waitForPostSwapAck` queue. The two address pairs differ by `0x3F8` and `0x3E0`, have separate data symbols, and no pointer-mediated alias was found. Selects static `H-real-mismatch`/role-separation, while the non-generated producer or forwarding boundary remains open; no build or runtime code changed. |
| s1102 | Complete static census of 44 generated `osSendMesg` and 2 `osJamMesg` sites found direct sends to both blocking queues: `spTaskSchedulerThread` at `0x80019F1C` computes `0x80120000-0x57E8 = 0x8011A818`, and `dpInterruptHandlerThread` at `0x8001C3CC` computes `0x80120000-0x5818 = 0x8011A7E8`. All other sites are unrelated fixed queues or computed object/argument queues. Host completion remains dynamic through `events_context.sp/.dp` and has no hard-coded target. This selects static `H-game-producer`/role-separation and rules out `H-host-boundary` and `H-unwired` for producer existence; execution reachability and lifecycle gating remain open. No build, runtime code, or queue behavior changed. |
| s1103 | Bounded producer/consumer branch audit found both direct sends are conditionally gated within their persistent producer loops: SP `0x80019F1C` is reached only through task-state branches at `0x80019ED4/0x80019EE4` (with an alternate gated send at `0x80019F40`), and DP `0x8001C3D8` requires nonzero flag byte `0x8011A89D`. The blocking consumers are likewise conditional at `0x8000C0A4` (SP) and `0x8000C2A8` (DP). This selects `H-producer-gated`, rules out unconditional reachability and lifecycle absence, and leaves gate ownership/value open. No build, runtime code, or queue behavior changed. |
| s1104 | Complete generated gate census separates the roles. `0x8011A89D/0x8011A89E` are set to 1 by `setPostSwapPendingFlags` and consumed/cleared by submit/advance paths. The SP producer’s `0x80019ED4/0x80019EE4` reads are through `s2 = (0x8011A89C + 3)`, i.e. `0x8011A89F/0x8011A8A0`; the same producer clears those bytes after its sends, and no generated nonzero writer was found. `dpInterruptHandlerThread` reads through `s0 = 0x8011A408`, so `0x8011A89D` is not its direct fixed-address flag in this generated snapshot. This selects static `H-sp-gate-stale-or-external-writer` while ruling out the `H-8011A89D-is-DP-gate` role assignment; non-generated ownership and runtime values remain open. No build, runtime code, or queue behavior changed. |

## Ranked next steps

1. Audit non-generated/companion ownership of SP bytes `0x8011A89F/0x8011A8A0`
   and the DP handler byte/object at `0x8011A408`; distinguish an external
   nonzero writer from a genuinely stale producer gate without changing queue
   behavior.
2. If ownership remains open, run one phase-gated value/PC capture for the
   producer gates and both blocking consumers, with positive controls, before
   changing any queue or gate behavior.
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
