# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
background is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact run
recipes and historical evidence remain in the append-only ledger.

Current maintenance marker: Session 3106 (2026-08-28).

Session 3106 ran a new independent retail mode-entry capture. The whole-RDRAM
positive control fired 10,000 writes, retail reached title 1024 at
`0x00790400` and hangar 512 at `0x006AB400`, and the `osViSetMode` watch at
`0x800352D0` fired 17 times. Its predecessor histogram was only
`0x8001B8DC` (13), `0x8001BB54` (2), and `0x8001B720` (2), but no watched row
was captured at the 17.2s 640→1024 transition; the mode dump also produced no
rows because it is limited to the 640-width path. This selects H-Unevaluable
for the exact transition writer, not H-ApplyPending or H-OtherCallsite.
Evidence: `scratch/agent/s3106_m5_retail_mode_writer/AUDIT.md`.

ORIGIN: qualification-only retail callsite attribution. No port, audio,
route, selector, wait, voice, or mitigation behavior changed.

Session 3105 statically audited both surviving retail `osViSwapBuffer`
predecessors. `0x8001BE24` is in `bufferArbiterProducerMark` and `0x80019B14`
is in `viRetraceHandlerThread`; each selects/loads a framebuffer pointer and
calls `osViSwapBuffer`, with no `osViSetMode` or VI-descriptor decision in its
body. Generated names, registrations, project symbols, and the companion map
agree, so no overlay alias was found. The mode writer is upstream in
`advanceVideoFrame → swapBufferWithViMode → osViSetMode`, with additional
direct callers in the video update/init paths. This selects
H-SharedSwapPath and closes the two-caller static boundary without identifying
the absent retail 1024 writer. Evidence:
`scratch/agent/s3105_external_retail_wrapper_chain/AUDIT.md`.

ORIGIN: static qualification of existing retail handoff callers. No runtime,
audio, route, selector, wait, voice, or mitigation behavior changed.

Session 3104 ran the independent retail oracle with a whole-RDRAM positive
control and the validated Start schedule. The control fired 10,000 writes;
retail reached title origin `0x00790400` (634 VI rows) and hangar origin
`0x006AB400` (2,447 VI rows). `osViSwapBuffer` execution had only the two
known predecessors, `0x8001BE24` (4,098) and `0x80019B14` (155), with no new
post-boot predecessor. This rejects H-NoTarget for the recipe but does not
distinguish the external-callsite and wrapper-chain hypotheses. It is
single-source oracle evidence; no port instrumentation was justified.
Evidence: `scratch/agent/s3104_external_retail_entry_boundary/AUDIT.md`.

ORIGIN: qualification-only retail handoff attribution. No audio, route,
selector, wait, voice, or mitigation behavior changed.

Session 3103 revalidated the bounded six-surface candidate at `0x800B75C4`
with a new control-flow discriminator. The live generated tree has a real
`beq` from `findLockOnTarget` to `L_800B75C4`, whose three instructions are
executed before the separate `playerYwingInit` prologue. The record therefore
cannot be renamed as `data_gap_*`; the companion map and redefs still supply
no independent semantic preamble identity, so `fake_func_800B75C4` remains.
All four remaining project `fake_func_*` entries now have bounded audits, so
the current sweep has no unaudited candidate. Evidence:
`scratch/agent/s3103_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only control-flow classification. No runtime, route, audio,
mitigation, or generated instruction behavior changed.

Session 3102 completed the bounded six-surface audit at `0x800B42BC`. The
companion map, generated body, callers, header/registration, project TOML,
and rename tooling show a 4-byte orphan load between the complete
`advancePitchTowardTarget` epilogue and `playerXwingInit` prologue. It has no
callers or return sequence, so H-Fragment selected and the entry is now
synchronized as `data_gap_800B42BC`. Evidence:
`scratch/agent/s3102_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification and regeneration-safe symbol metadata. No
runtime, route, audio, mitigation, or generated instruction behavior changed.

Session 3101 completed the bounded six-surface audit at `0x800AF6A8`. The
companion map retains only the fake marker, while the active generated body
is an explicit trap-filled invalid-data record with no callable prologue,
return, caller, or semantic identity. The adjacent positive-control entry
`handleCraftSelectInput` at `0x800AF6AC` remains intact. The record is now
synchronized as `data_gap_800AF6A8` across the generated body, header, overlay
registration, project TOML, and rename tooling. Evidence:
`scratch/agent/s3101_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification and regeneration-safe symbol metadata. No
runtime, route, audio, mitigation, or generated instruction behavior changed.

Session 3100 completed the bounded six-surface audit at `0x800AE3E4`. The
12-byte mission record is an instruction-only fragment with no callable
prologue, return, generated caller, or exact companion identity. Its final
word overlaps the independently named menu-overlay entry
`tickEasedCameraKeyframeBlend` at `0x800AE3EC`, so neither a semantic rename
nor a `data_gap_*` classification is safe. The placeholder is preserved and
the sweep advances to the next unresolved project placeholder. Evidence:
`scratch/agent/s3100_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only boundary classification and regeneration-safe metadata.
No runtime, route, audio, mitigation, or generated instruction behavior
changed.

Session 3099 completed the bounded six-surface audit at `0x80072CE8`. The
companion map explicitly names the two-instruction entry fragment
`initWaterSprayParticlesPreamble`; the active generated body, header, and
overlay registration already agree, with the project TOML as the only stale
surface. It is now synchronized under that exact name. The next unresolved
project placeholder is `fake_func_800AE3E4`. Evidence:
`scratch/agent/s3099_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification and regeneration-safe symbol metadata. No
runtime, route, audio, mitigation, or generated instruction behavior changed.

Session 3098 completed the bounded six-surface audit at `0x8006B704`. The
companion map, generated body, callers, header, overlay registration, project
TOML, and rename tooling agree that this is a 12-byte non-callable instruction
fragment between `getLevelTimeLimit` and `loadCraftShadowTextures`; it is now
synchronized as `data_gap_8006B704`. The next unresolved project placeholder
is the first remaining `fake_func_*` entry after this address. Evidence:
`scratch/agent/s3098_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification and regeneration-safe symbol metadata. No
runtime, route, audio, mitigation, or generated instruction behavior changed.

Session 3097 completed the bounded six-surface audit at `0x80055A2C`. The
companion map explicitly names the one-instruction entry fragment
`initVoiceSubtitleSystemPreamble`; the active generated body, header, and
overlay registration already agree, with no generated callers or independent
lookup. The project TOML was the only stale surface and now uses the same
regeneration-safe name. The next unresolved project placeholder is
`fake_func_8006B704`. Evidence:
`scratch/agent/s3097_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification and regeneration-safe symbol metadata. No
runtime, route, audio, mitigation, or generated instruction behavior changed.

Session 3096 completed the bounded six-surface audit at `0x800457CC`. The
companion map, generated body, callers, header, overlay registration, and
rename tooling agree that this is a 4-byte non-callable fragment before
`initGridLayerFromLevelData`; the project TOML was the only stale surface and
now uses `data_gap_800457CC`. The next unresolved project placeholder is
`fake_func_80055A2C`. Evidence:
`scratch/agent/s3096_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification and regeneration-safe symbol metadata. No
runtime, route, audio, mitigation, or generated instruction behavior changed.

Session 3095 completed the bounded six-surface audit at `0x80041EEC`. The
companion map, generated body, callers, header, overlay registration, rename
mapping, and project TOML agree that this is a 4-byte non-callable record
before `allocAndInitDoublyLinkedNodePool12`; the project TOML was the only
stale surface and now uses `data_gap_80041EEC`. The next unresolved project
placeholder is `fake_func_800457CC`. Evidence:
`scratch/agent/s3095_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification and regeneration-safe symbol metadata. No
runtime, route, audio, mitigation, or generated instruction behavior changed.

Session 3094 ran the independent M5 VI-mode publication/consumer handoff
capture after rebuilding Debug. Retail passed the whole-RDRAM positive control
(18,896 callbacks), reached title `1024 @ 0x00790400` and hangar `512 @
0x006AB400`, and the watched retail mode/caller/ProducerMark PCs fired. The
port selector control fired, recorded four `osViSetMode` calls and 512 VI
context rows, but remained at VI-640: it published `0x80128E40` then
`0x80128DF0` at width 640, with no title/hangar rows. This rejects a missing
publication wrapper and the observed 640 consumer as the cause, but leaves
the absent 1024 writer and ordering unevaluable. After three upstream route
probes without a target-phase discriminator, the next work unit pivots to the
bounded generated-symbol sweep. Evidence: `scratch/agent/s3094_m5_vi_mode_publication/AUDIT.md`.

ORIGIN: qualification-only publication/consumer attribution. No audio,
route, selector, wait, voice, or mitigation behavior changed.

Session 3093 ran the M5 Step 1 image-vs-silent qualification after rebuilding
the Debug target. The independent retail oracle passed the whole-RDRAM
positive control (`10000` callbacks), reached title `1024 @ 0x00790400` and
hangar `512 @ 0x006AB400`. The same-build port arms both positively
dispatched 78 audio tasks (silent `real_ucode=0`, image `real_ucode=1`) but
both stopped at VI-640 `0x0066A500`; neither produced target-phase task,
DMA, service, slot, voice, or PCM rows. This rejects an audio-arm-specific
route difference but leaves the Step 1 audio contract unevaluable. The next
M5 discriminator moves upstream to VI-mode publication/consumer handoff.
Evidence: `scratch/agent/s3093_m5_step1_qualification/AUDIT.md`.

ORIGIN: qualification-only A/B. No audio behavior, gate, wait, voice guard,
or output destination changed.

Session 3092 ran the M5 ProducerMark handoff discriminator after an
independent retail preflight. Retail passed the whole-RDRAM control, reached
title/hangar, and executed `0x8001BCE4` with dominant predecessor
`0x8000C628`. The port positive controls fired and the new regeneration-safe
handoff table observed 45 entry/exit pairs plus 40 explicit dominant
`0x8000C628` callsite rows, but the port still stopped at VI-640
`0x0066A500`. This refutes H-MissingCaller (a missing dominant ProducerMark
call); target predicate and ordering remain unevaluable because the port never
reached the target phase. The route investigation moves upstream to VI-mode
publication, with the discriminating next angle being the writer/consumer
handoff upstream of ProducerMark.
Evidence: `scratch/agent/s3092_m5_route_handoff/AUDIT.md`.

ORIGIN: diagnostic-only handoff attribution. No game state, audio route, or
mitigation behavior changed.

Session 3091 ran the M5 VI selector-writer attribution after first restoring
the independent oracle core. Retail passed its whole-RDRAM positive control
(10,029 writes) and reached title 1024 at `0x00790400` and hangar 512 at
`0x006AB400`, but a physical watch on `0x0011A865..67` had zero writes in
those phases. The port selector positive control fired and produced 512
bounded VI-context rows, but both the pre-rebuild and rebuilt AUTOPILOT
captures stopped at VI-640; the title/hangar gate never armed. Specific
generated selector/writer markers were absent in both captures, so their
nulls are unevaluable. This rejects the watched byte range as the retail
producer boundary and rejects stale binary/missing AUTOPILOT as explanations,
but selects no selector hypothesis. Evidence:
`scratch/agent/s3091_m5_vi_selector_writer/AUDIT.md`.

ORIGIN: qualification-only route attribution. No selector writer, audio
route, generated behavior, or mitigation changed.

Session 3090 audited `fake_func_8009D7CC` across the companion map, redefs,
generated body, callers, header, overlay registration, and project TOML. The
four-byte record is the one-instruction `mtc1 $zero,$f4` entry fragment for
`filterVoiceSampleBlock`; the following function has its own complete body and
the project TOML is now synchronized as `filterVoiceSampleBlockPreamble`.
Evidence: `scratch/agent/s3090_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification and regeneration-safe symbol metadata.
No runtime, route, audio, mitigation, or generated instruction behavior
changed.

Session 3089 audited `fake_func_8009C2C8` across the companion map, generated
body, callers, header, overlay registration, and project TOML. The 8-byte
record contains only two COP1 instructions between complete `stopVoice` and
`computeVoicePanCoefficients` bodies, with no callable prologue, return
sequence, caller, or independent semantic identity. This selects H-Fragment
and synchronizes the regeneration-safe mechanical name `data_gap_8009C2C8`.
Evidence: `scratch/agent/s3089_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification. No runtime, route, audio, mitigation, or
generated instruction behavior changed.

Session 3088 audited `fake_func_80099FDC` across the companion map, redefs,
generated body, callers, header, overlay registration, and project TOML. The
project record is four bytes, and the generated branch's delay slot is the
first word of the `aspMain` RSP text payload; the remaining generated body is
an invalid CPU decode of RSP text through the next named CPU routine. No
caller or semantic companion identity exists. This selects H-Fragment and
synchronizes the regeneration-safe mechanical name `data_gap_80099FDC`.
Evidence: `scratch/agent/s3088_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification. No runtime, route, audio, mitigation, or
generated instruction behavior changed.

Session 3087 audited `fake_func_8007C298` across the companion map, generated
body, callers, header, overlay registration, and project TOML. The 8-byte
record contains only two argument-computation instructions between complete
`loadShieldPalette` and `initNpcTexturedEffectFromTemplate` bodies, with no
callable prologue, return sequence, caller, or semantic companion identity.
This selects H-Fragment and synchronizes the regeneration-safe mechanical name
`data_gap_8007C298`. Evidence: `scratch/agent/s3087_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification. No runtime, route, audio, mitigation, or
generated instruction behavior changed.

Session 3086 audited `fake_func_8006B704` across the companion map, generated
body, callers, header, overlay registration, and project TOML. The 12-byte
record contains a valid store plus argument setup between
`getLevelTimeLimit` and `loadCraftShadowTextures`, but has no callable
prologue/return, direct caller, or independent semantic name. This selects
H-Fragment with unresolved callability: preserve the placeholder rather than
inventing a name or data-gap classification. Evidence:
`scratch/agent/s3086_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification. No runtime, route, audio, mitigation, or
generated instruction behavior changed.

## Current state

The qualified port uses `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`, and
`ROGUESQ_LLE_SOLO=1`. `ROGUESQ_SPIN_YIELD=1` is diagnostic and default-off.
`ROGUESQ_AUTOPILOT` is the reliable in-process driver. The game can render
attribution, the N64 logo, the intro cinematic, the star flare, the Factor 5
logo, title-like VI 1024 (`0x00790400`), and hangar VI 512
(`0x006AB400`) with the validated input path. Hangar visuals still have
geometry/color artifacts.

M5 currently defaults to the Factor 5 image arm. `ROGUESQ_AUDIO_UCODE=0`
selects the silent `musyx_stub` control. Retail uses Factor 5 MORT audio, not
stock `aspMain`; audio is still partly stubbed. M3 is limited to complete
idiom-class audits. M4 hangar/512 Y=`0x8000` is not live on the first hangar
capture.

The original overlay-dispatch explanation is no longer the current blocker:
qualified runs reach title and hangar boundaries. Factor 5 image tasks and
CPU MORT speech are separate contracts. A `Broke` return proves task
completion, not PCM correctness. The M5 route dependency remains open, but
static generated-symbol work can proceed independently.

Session 3082 completed the bounded six-surface audit at `0x80019808`. The
companion map, generated body, callers, header, overlay registration, and
project TOML agree on an 8-byte defined gap between `projectPointToScreen` and
`awaitFrameSyncMesgBlock`; the generated body is only `lwc1`/`mul.s`, with no
callable prologue, return sequence, or callers. This selects H-Fragment and
confirms the existing regeneration-safe `data_gap_80019808` mapping. The next
sweep candidate is `fake_func_80024878`. Evidence:
`scratch/agent/s3082_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification. No runtime, route, audio, mitigation, or
generated instruction behavior changed.

Session 3083 completed the bounded six-surface audit at `0x80024878`. The
companion map, generated body, callers, header, overlay registration, project
TOML, and rename tooling agree on an 8-byte non-callable record containing
only `addu $sp,$fp,$zero` and `lw $ra,0x1C($sp)` before
`swizzleTextureRowsToTmem`. This selects H-Fragment and preserves the
regeneration-safe `data_gap_80024878` mapping. The next sweep candidate is
`fake_func_800555E8`. Evidence:
`scratch/agent/s3083_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification. No runtime, route, audio, mitigation, or
generated instruction behavior changed.

Session 3084 completed the bounded six-surface audit at `0x800555E8`. The
companion map, generated body, callers, header, overlay registration, project
TOML, and rename tooling agree on the 8-byte `initPlayerStructsPreamble`
tail-call entry to `initPlayerStructs`; the active generated tree has no stale
placeholder reference. This selects H-ExactIdentity and confirms the existing
regeneration-safe mapping. The next sweep candidate is
`fake_func_8006ACA4`. Evidence:
`scratch/agent/s3084_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification. No runtime, route, audio, mitigation, or
generated instruction behavior changed.

Session 3085 completed the bounded six-surface audit at `0x8006ACA4`. The
companion map retains the placeholder, the generated body is only three
instructions with no callable prologue or return, and no generated caller
exists. Overlay extent and project TOML place it as a 12-byte record between
`transformMeshPartIntoWorld` and `transformObjectColliderCenter`. This selects
H-Fragment, so the record is now named mechanically as `data_gap_8006ACA4` in
the project TOML, rename tooling, and active generated tree. Evidence:
`scratch/agent/s3085_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification. No runtime, route, audio, mitigation, or
generated instruction behavior changed.

## Latest results

Session 3081 completed the bounded six-surface audit at `0x800186D8`. The
companion map and independent redefs classify this as an 8-byte defined gap
between `freeRenderSubsystemResources` and `fetchVertexPositionPrimary`; no
caller, prologue, return sequence, or semantic identity supports a callable
name. This selects H-Fragment, so the project TOML was synchronized to the
existing regeneration-safe `data_gap_800186D8` mapping. Evidence:
`scratch/agent/s3081_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification. No runtime, route, audio, mitigation, or
generated instruction behavior changed.

Session 3080 completed the bounded six-surface audit at `0x8005C61C`. The
companion map, generated body, header, overlay registration, and project TOML
agree on a 4-byte isolated `addu $v1, $v1, $a0` fragment immediately before
`checkTrackedNpcProximityForCue`; there is no independent caller or semantic
identity. This selects H-Fragment, so the placeholder was renamed mechanically
to `data_gap_8005C61C` across the regeneration-safe mapping and generated tree.
The former preamble convenience rule was removed. The next sweep candidate is
`fake_func_80019808`. Evidence: `scratch/agent/s3080_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification. No runtime, route, audio, mitigation, or
generated instruction behavior changed.

Session 3079 completed the bounded six-surface audit at `0x80059B4C`. The
companion map, generated body, header, overlay registration, and project TOML
agree on a 4-byte isolated `sw $fp, 0x48($sp)` fragment immediately before
`mat34CrossRowsAndCopyPos`; there is no independent caller or semantic
identity. This selects H-Fragment, so the placeholder was renamed mechanically
to `data_gap_80059B4C` across the regeneration-safe mapping and generated tree.
The next sweep candidate is `fake_func_8005C61C`. Evidence:
`scratch/agent/s3079_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification. No runtime, route, audio, mitigation, or
generated instruction behavior changed.

Session 3078 completed the bounded six-surface audit at `0x80056344`. The
companion map, generated body, header, overlay registration, and project TOML
agree on a 12-byte three-instruction fragment between `clearActiveVoiceLine`
and `initNpcBookkeepingTables`; there is no prologue, return sequence, caller,
or independent semantic identity. This selects H-Fragment, so the placeholder
was renamed mechanically to `data_gap_80056344` across the regeneration-safe
mapping and generated tree. The next sweep candidate was `fake_func_80059B4C`,
now resolved as a mechanical gap; the next candidate is `fake_func_8005C61C`.
Evidence: `scratch/agent/s3078_generated_symbol_rename/AUDIT.md`.

ORIGIN: naming-only classification. No runtime, route, audio, mitigation, or
generated instruction behavior changed.

Session 3077 landed a bounded generated-symbol rename batch in the sibling
recompiled tree. `fake_func_800B47C4` and `fake_func_800B58B4` were renamed to
`menuControllerInputPreamble` and `playerAwingInitPreamble`; their generated
definitions, declarations, and overlay registrations now agree, with six
placeholder references removed. The companion mappings, generated bodies,
callers, and exact short extents support both preamble identities. The M5
VI-selector observation unit was not rerun; the mandated engineering pivot
selected the rename sweep because no M5 contract edge was proven for a safe
de-stub.

Evidence: sibling commit `f9d0ab0`, generated-tree verification, and the
existing companion symbol files. ORIGIN: naming-only code change; no runtime,
audio route, or mitigation behavior changed.

Session 3076 completed the bounded VI selector-state audit. The four records
at `0x80128D50 + {0,0x50,0xA0,0xF0}` and their `+8` width fields are copied by
`initVideoSubsystem` without aliasing; `applyPendingViChanges` selects and
passes the pointer unchanged. Retail `0x80128DA0` requires selector
`[A,B,C]=[1,1,0]`, while port `0x80128DF0` requires `C=1` and not `(A&&B)`.
The remaining divergence is upstream selector/pending-mask input from the
game writers, selecting H-SelectorWriter and rejecting alias/consumer causes
at this boundary. Evidence: `scratch/agent/s3076_m5_vi_selector_state/AUDIT.md`.

No behavior, audio route, or mitigation changed. The causal producer-value
difference is still single-source/static pending retail attribution of those
inputs.

Session 3075 ran the M5 Step-1 image/silent qualification with one rebuilt
Debug binary, concurrent arms, and the independent retail oracle. The oracle
passed the whole-RDRAM positive control and reached title `1024 @
0x00790400` plus hangar `512 @ 0x006AB400`. Both port arms positively
dispatched audio tasks (`78` rows each; `real_ucode=1/0`) but stopped at VI
640 (`0x0066A500`) after width 2 (`0x006DD000`); neither reached a target
phase. Both had zero target-phase task/DMA/image-return/SP/service/slot/voice/
PCM rows and zero crash/abort rows. This selects H-RouteInvalid; downstream
audio nulls are unevaluable, and no audio behavior or mitigation is
authorized. Evidence: `scratch/agent/s3075_m5_step1_qualification/AUDIT.md`.

ORIGIN: qualification-only. No runtime, generated instruction, route, audio,
or submodule behavior changed.

Session 3074 completed the bounded six-surface audit at `0x800C64A4`. The
companion mission map and `redefs.txt` retain the 12-byte `data_gap_800C64A4`
record immediately before `initHangarDisplayItemTimers`; generated code is
only an epilogue fragment with no return sequence or caller. Header, overlay
registration, project TOML, and rename tooling agree on address and extent,
and historical local snapshots show no competing identity. This selects
H-DataGap and preserves the placeholder. The next sweep candidate is
`data_gap_800C7DB4`. Evidence:
`scratch/agent/s3074_generated_symbol_rename/AUDIT.md`.

No build or runtime run was needed for this static unit. This rules out an
independently named callable/preamble identity and mapping drift at this
boundary; it does not make a claim about runtime behavior.

ORIGIN: naming-only classification. No runtime, generated instruction, route,
audio, or submodule behavior changed.

Session 3073 completed the bounded six-surface audit at `0x800C41AC`. The
companion mission map and primary `redefs.txt` retain the 4-byte
`data_gap_800C41AC` immediately before `plotRadarBlipColumn`; generated code
contains only `add.s`, with no return sequence or caller. Header, overlay
registration, project symbol TOML, and the main rename tool agree on address,
extent, and mechanical name. This selects H-DataGap and preserves the
placeholder. The next sweep candidate is `data_gap_800C64A4`. Evidence:
`scratch/agent/s3073_generated_symbol_rename/AUDIT.md`.

No build or runtime run was needed for this static unit. This rules out an
independently named callable/preamble identity and mapping drift at this
boundary; it does not make a claim about runtime behavior.

ORIGIN: naming-only classification. No runtime, generated instruction, route,
audio, or submodule behavior changed.

Session 3072 completed the bounded six-surface audit at `0x800BF784`. The
companion mission map and primary `redefs.txt` classify the 12-byte entry as
`data_gap_800BF784` immediately before `updateHudHealthIndicator`; generated
code contains only `lui`/`lwc1`/`sub.s`, with no return sequence or caller.
Header, overlay registration, project TOML, and the main rename tool agree on
the address and extent. A local `EXTRA_RENAMES` convenience rule calls the
fake symbol `updateHudHealthIndicatorPreamble`, but no independent companion
surface supports that semantic identity. This selects H-DataGap and preserves
the placeholder. The next sweep candidate is `data_gap_800C41AC`. Evidence:
`scratch/agent/s3072_generated_symbol_rename/AUDIT.md`.

No build or runtime run was needed for this static unit. This rules out an
independently named callable/preamble identity and mapping drift at this
boundary; it does not make a claim about runtime behavior.

ORIGIN: naming-only classification. No runtime, generated instruction, route,
audio, or submodule behavior changed.

Session 3071 completed the bounded six-surface audit at `0x800BF498`. The
companion mission map and `build/redefs.txt` preserve the mechanical
`data_gap_800BF498` identity; generated code contains only an 8-byte `lw`/`sw`
fragment with no return sequence or caller immediately before
`attached3DSoundEmitterNpcHandler`. Header, overlay registration, project
TOML, and rename tooling agree on the address and extent. This selects
H-DataGap and preserves the placeholder. The next sweep candidate is
`data_gap_800BF784`. Evidence: `scratch/agent/s3071_generated_symbol_rename/AUDIT.md`.

No build or runtime run was needed for this static unit. This rules out an
independently named callable/preamble identity and mapping drift at this
boundary; it does not make a claim about runtime behavior.

ORIGIN: naming-only classification. No runtime, generated instruction, route,
audio, or submodule behavior changed.

Session 3070 completed the bounded six-surface audit at `0x800BEBFC`. The
companion mission map and generated registration/TOML showed a 4-byte record
immediately before `initDemoPlayState` at `0x800BEC00`; generated code is the
single `addu $fp,$sp,$zero` fragment with no return sequence or caller. The
independent companion `redefs.txt` maps the corresponding fake symbol to
`initDemoPlayStatePreamble`, and the local `build_redefs.py` already carries
that identity. This selects H-ExactIdentity: the project TOML and
`rename_generated_symbols.py` were synchronized. The next sweep candidate is
`data_gap_800BF498`. Evidence:
`scratch/agent/s3070_generated_symbol_rename/AUDIT.md`.

Session 3057 mapped retail PC `0x80035798` to libultra
`__osViSwapContext` (`0x80035550–0x800358AC`), the VI-register commit
consumer, not a missing game overlay writer. The port has the corresponding
`events.cpp::update_vi` implementation and its `osViSetMode` publication path.
All four generated game-side VI callsites are present, but the s3056 port log
contains only requests of widths 320, 2, 640, and 640, so no 1024 descriptor
exists for the consumer to commit. This rejects missing-writer and aliasing at
the runtime boundary and does not select descriptor corruption. The upstream
game-side mode-selection call/state that should request 1024 remains open.
Evidence: `scratch/agent/s3057_m5_vi_writer_mapping/AUDIT.md`.

Session 3058 ran the retail-grounded VI request attribution. The oracle
passed the whole-RDRAM positive control, reached title at width 1024 and
hangar at width 512, and its `exec-prev` histogram attributed the 1024-capable
`osViSetMode` path to `0x8001B8DC` (142 calls), with only 6 calls from
`0x8001B720` and 5 from `0x8001BB54`. The companion map and generated tree
identify `0x8001B8DC` as `applyPendingViChanges`; the corresponding port path
exists, but the s3056 same-build capture showed it submitting width 640 rather
than 1024. This selects `H-RequestDescriptor`, rejects a missing direct
caller, and does not by itself prove why the descriptor source differs.
Evidence: `scratch/agent/s3058_m5_vi_request_attribution/AUDIT.md`.

Session 3059 completed the bounded static descriptor-source audit. The
`applyPendingViChanges` callsite at `0x8001B8DC` selects from the four-record
table at `0x80128D50`, with the width-bearing field at `+8`. Retail's title
request uses `0x80128DA0` (the `+0x50` record, width 1024), while the
qualified port capture used `0x80128DF0` (the `+0xA0` record, width 640).
`initVideoSubsystem` populates all four records through its existing copy
loop, and the port passes the selected pointer unchanged to `osViSetMode`.
This selects `H-SourceSelection`, rejecting a missing writer and pointer
aliasing at this boundary; the selector-state divergence remains open.
Evidence: `scratch/agent/s3059_m5_vi_descriptor_source/AUDIT.md`.

Session 3060 completed the bounded generated-symbol audit at `0x80017AE0`.
The companion map, generated body, callers, header, overlay registration, and
project TOML all agree on `setViewStateBytesAndFadeScale`, its `0x48`-byte
extent, and its callable setter semantics. No rename was needed; the next
sweep candidate is `0x80017B28`. Evidence:
`scratch/agent/s3060_generated_symbol_rename/AUDIT.md`.

Session 3061 completed the bounded generated-symbol audit at `0x80017B28`.
The companion map, generated body, sole caller, header, overlay registration,
and project TOML all agree on `setViewStateTripletBytes`, its `0x20`-byte
extent, and its three-byte setter semantics. The generated tree already has
the regeneration-safe semantic name, so no rename was needed. The next sweep
candidate is `0x80017B48`. Evidence:
`scratch/agent/s3061_generated_symbol_rename/AUDIT.md`.

Session 3062 landed the first rename in the current sweep batch. Independent
companion maps, generated body/header/registration, callers, and the project
TOML identify `0x800C63C0` as `getAvailableShipsForLevel`; the project TOML's
stale `func_800C63C0` entry was corrected. The rename tool now also preserves
the confirmed `rs_crc32` and `setHudSecondaryWeaponInfo` identities when a
regeneration emits their address placeholders. The duplicate menu-overlay
entry at the same address remains distinct. Evidence:
`scratch/agent/s3062_generated_symbol_rename/AUDIT.md`.

Session 3063 completed the bounded six-surface audit at `0x800E9AE0`. The
companion mission-overlay map says this is a real `0x114`-byte function split
by a false `0x800E9B10` target, but supplies no semantic name. The generated
body is coherent NPC/object initialization code; its header and overlay
registration remain address-named, while the project TOML and rename tool
already agree on `func_mission_overlay_800E9AE0`. No generated caller or
mapping drift was found, so no human rename was justified. Evidence:
`scratch/agent/s3063_generated_symbol_rename/AUDIT.md`.

Session 3066 completed the bounded six-surface audit at `0x800B58B4`. The
companion mission_overlay.txt comment ("real function is playerAwingInit"),
the oracle redefs.txt independent naming (`playerAwingInitPreamble`), the
generated body (3-instruction, 0xC bytes, no prologue or return, no caller),
and both rename tools all agree. Session 2962 had preserved the placeholder
because no independent preamble name existed at that time; the oracle
redefs.txt now closes that gap. The project TOML was synchronized from
`fake_func_800B58B4` to `playerAwingInitPreamble`. Evidence:
`scratch/agent/s3066_generated_symbol_rename/AUDIT.md`.

Session 3067 completed the bounded six-surface audit at `0x800B75C4`. The
companion map explicitly retains `fake_func_800B75C4` and says the real
function is `playerYwingInit`; `redefs.txt` has no independent
`playerYwingInitPreamble` identity. The generated body is only three
instructions (`lui`, `lwc1`, `mul.s`) over `0xC` bytes, with no return sequence
or caller; callers target `playerYwingInit` at `0x800B75D0`. Header,
registration, and project TOML agree on the `0xC`-byte boundary. This selects
H-Fragment and preserves the placeholder. The next sweep candidate is
`fake_func_800B89F4`. Evidence:
`scratch/agent/s3067_generated_symbol_rename/AUDIT.md`.

Session 3068 completed the bounded six-surface audit at `0x800B89F4`. The
companion mission map retains the fake entry and says the real function is
`playerVwingInit` at `0x800B8A00`, but companion `redefs.txt` has no V-wing
preamble identity. The external generated snapshot registers a 0xC-byte
placeholder immediately before `playerVwingInit`; its surrounding disassembly
shows the address inside the preceding control-flow sequence, and no caller
targets it. Header, registration, TOML, and rename tooling agree on the
placeholder and boundary. This selects H-Fragment and preserves the
placeholder. The next sweep candidate is `data_gap_800BCC38`. Evidence:
`scratch/agent/s3068_generated_symbol_rename/AUDIT.md`.

Session 3069 completed the bounded six-surface audit at `0x800BCC38`. The
companion mission map and redefs identify it as an explicit data gap before
`playerT16Init` at `0x800BCC40`; the generated body is an 8-byte conditional
branch into that initializer with an unresolved cross-function label, and no
caller targets the gap. Header, overlay registration, project TOML, and rename
tooling agree on the 8-byte boundary and mechanical name. This selects
H-DataGap and preserves the placeholder. The next sweep candidate is
`data_gap_800BEBFC`. Evidence:
`scratch/agent/s3069_generated_symbol_rename/AUDIT.md`.

Session 3065 completed the bounded six-surface audit at `0x800B47C4`. The
companion comments, generated extent, callers, header/registration, project
TOML, and rename tooling identify the 12-byte record as
`menuControllerInputPreamble`, immediately before the real
`menuControllerInput` body at `0x800B47D0`. The generated record is only a
float load/store with no return sequence or caller; the project TOML was
synchronized from its stale placeholder name. Evidence:
`scratch/agent/s3065_generated_symbol_rename/AUDIT.md`.

Session 3064 completed the bounded six-surface audit at `0x800B2628`. The
companion map, generated body/header/registration, and project TOML all agree
on an 8-byte menu-overlay placeholder, but the body is only a float load/store
with no return sequence and no generated caller. This selects the fragment or
data-boundary hypothesis; no semantic rename is justified. The next sweep
candidate is `0x800B47C4`. Evidence:
`scratch/agent/s3064_generated_symbol_rename/AUDIT.md`.

Session 3040 ran the M5 Step-1 image/silent qualification after an independent
retail ground-truth preflight. Retail passed the whole-RDRAM positive control
and reached title/hangar, but both concurrent port arms stopped at VI 640
(`0x0066A500`) before title; downstream audio rows are unevaluable. The
driver was corrected in-iteration to launch both arms concurrently, use the
scheduled AUTOPILOT route, and clean up child processes. The corrected run
reproduced the same route boundary. Image and silent dispatch controls were
positive (`44` each, `real_ucode=1/0`), so arm selection and logging ran; no
audio hypothesis was selected and no audio behavior changed. Evidence:
`scratch/agent/s3040_m5_step1_contract_pair_final/`.

Session 3041 ran the new retail-grounded ProducerMark boundary. Retail passed
the whole-RDRAM positive control, reached title/hangar, and executed
`0x8001BCE4` 2,470 times; predecessor `0x8000C628` accounted for 2,446 and
`0x8000BFE8` for 7. The same-build port capture had positive route controls
but stopped at VI 640 `0x0066A500`: 526 route-prepares were all
`accepted=0`, with no producer-mark candidate rows, title, or hangar. This
selects RouteFailure for this capture and leaves the caller/order comparison
and all downstream audio rows unevaluable. Evidence:
`scratch/agent/s3041_m5_producer_mark_boundary/`.

Session 3042 completed the bounded static ProducerMark call-chain audit.
All six direct generated calls to `0x8001BCE4` are present: one from
`bufferArbiterProducerScanWait`, three from `submitGfxFrame`, one from
`advanceVideoFrame`, and one from `initVideoSubsystem`. The generated body,
header, overlay registration, project TOML, and companion map agree. Host
`accepted` is only the committed-VI target predicate for 1024/title or
512/hangar; it cannot reject ProducerMark, so the VI-640 `accepted=0` rows do
not identify a missing caller or an acceptance bug. No behavior change was
justified. Evidence: `scratch/agent/s3042_m5_producer_mark_audit/AUDIT.md`.

Session 3043 completed the bounded VI-commit-to-route ordering audit. The
diagnostic `g_m5_vi_commit` snapshot is published by `osViSetMode_recomp`
immediately after queuing next-state mode data, before the retrace thread's
`update_vi` writes the actual VI registers. This is a real telemetry ordering
mismatch, but route preparation does not consume that snapshot: it reads the
live VI registers and applies the target-pair predicate directly. No route
behavior change is justified, and the VI-640 route failure remains open.
Evidence: `scratch/agent/s3043_m5_vi_commit_order_audit/AUDIT.md`.

Session 3044 completed the bounded audio-task publication-to-consumer audit.
`osSpTaskStartGo` forwards the guest `OSTask*` into the non-GFX SP queue;
`task_thread_func` consumes that same pointer, `run_task` calls
`get_rsp_microcode`, and the selected audio arm observes the descriptor on the
same consumer thread. The queue is the real handoff; the release/acquire
guest-pointer atomic is diagnostic only. No missing writer, wrong consumer, or
missing host ordering edge was found. The only remaining static concern is
descriptor lifetime/reuse because the queue carries a RDRAM pointer rather than
a copy; this is single-source evidence and requires independent temporal
ground truth before changing behavior. Evidence:
`scratch/agent/s3044_m5_task_handoff_audit/AUDIT.md`.

Session 3045 added and ran a regeneration-safe submit-to-consume descriptor
lifetime table. The independent retail oracle passed its whole-RDRAM control,
reached the 512 hangar, and attributed 1,013 type-2 `osSpTaskStartGo` rows to
task `0x80149470` / data `0x80171E70` (`data_size` `1–2`), with callers
`0x80019DEC` and `0x80019D68`. The port lifetime instrument had active phase
logging but zero accepted title/hangar routes and therefore zero lifetime
rows; its positive control did not arm. This selects
`H-MeasurementInsufficient` for the port capture, not descriptor immutability,
reuse, or ordering. No behavior change was justified. Evidence:
`scratch/agent/s3045_m5_task_lifetime/AUDIT.md`.

Session 3046 ran the new retail-grounded producer/signal edge audit. The first
oracle setup omitted Rice and stayed at VI 320, but its whole-RDRAM control
fired; the corrected Rice run again passed that control, reached title
`1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, and observed the known
`0x80019DEC`/`0x80019D68` producers plus `0x8001BCE4` consumers. No distinct
signal, payload, or consumer edge appeared. This selects
`H-MeasurementInsufficient` for the new-edge unit and leaves the port VI-640
route boundary unexplained. Evidence:
`scratch/agent/s3046_m5_route_producer_edge/AUDIT.md`.

Session 3047 ran a retail-grounded frame-sync edge audit. Retail's whole-RDRAM
positive control fired, and `0x80019810`/`0x8001983C` executed with callers
`0x8000BC14`/`0x8000BF38`; retail reached title and hangar. The batched port
probe was live and logged 164 pre-target `0x80128CF0` wrapper edges, but no
`0x80138D10` rows and no target-phase route: it stopped at VI 640
`0x0066A500`. This selects `H-MeasurementInsufficient`; the new edge's
missingness and ordering remain unevaluable. Evidence:
`scratch/agent/s3047_m5_frame_sync_edge/AUDIT.md`.

Session 3048 ran a retail-grounded DP event boundary audit. Retail's
whole-RDRAM control fired, reached title and hangar, and executed the DP
consumer at `0x8001C38C` from `0x8001C388` on queue `0x8011A408` in target
phases. The batched port probe was live and recorded 301 receives on that
queue, but only from alternate pre-target callers (`0x8000B650`, `0x8000834C`,
and early one-offs); it stopped at VI 640 with route preparation
`accepted=0`, no title/hangar phase, and no target caller row. This selects
`H-MeasurementInsufficient`; missingness and ordering remain unevaluable.
Evidence: `scratch/agent/s3048_m5_dp_event_boundary/AUDIT.md`.

Session 3049 audited event registration and DP completion wiring. Retail's
whole-RDRAM control fired, reached title and hangar, and saw `osSetEventMesg`
only for SI/AI plus zero executions of `dpInterruptHandlerThread`; its target
phase still reached the DP consumer at `0x8001C38C` on queue `0x8011A408`.
The same-build port positively registered DP event 9 to that queue with
message zero and produced repeated DP completion rows, but remained at VI 640
`0x0066A500`. This is a route-wiring divergence closest to
`H-EventDeliveryWrong`, not a missing port registration or an unevaluable
measurement. No behavior change was justified. Evidence:
`scratch/agent/s3049_m5_event_registration_edge/AUDIT.md`.

Session 3050 audited direct `osSendMesg` producers for DP queue
`0x8011A408`. Retail's positive-controlled oracle reached hangar and recorded
zero target-phase sends to that queue despite 72,158 watched `osSendMesg`
executions. The same-build port wrapper positive control fired, but the run
stopped at VI 640 and recorded zero phase-4 sends, only receives from
`0x80007904`/`0x8000B650`. This rejects a divergent direct producer and points
to external DP-queue delivery; the writer/interrupt edge is still unproven.
Evidence: `scratch/agent/s3050_m5_direct_dp_producer/AUDIT.md`.

Session 3051 ran the corrected retail-grounded external DP-delivery watch.
Retail passed the whole-RDRAM and execution positive controls, reached the
hangar, and executed `0x8001C38C` (receive from `0x8011A408`) and
`0x8001C3D4` (forward to `0x8011A7E8`) 243 times each in the target phase.
The port's existing batched DP-event instrument was live but stopped at
VI-640 origin `0x0066A500`, so its target-phase delivery remained
unevaluable. This selects `H-MeasurementInsufficient` for the port capture;
the retail pair is real, but the missing port handoff is not localized. The
zero watch at handler entry `0x8001C328` is not interpreted as absence because
the body PCs were positive in the same run. Evidence:
`scratch/agent/s3051_m5_external_dp_delivery/AUDIT.md`.

Session 3038 refreshed the M5 design gate after a direct source survey. The
active inventory remains complete at A1–A20 in `docs/M5-AUDIO-PLAN.md`: the
Factor 5 image is the real `M_AUDTASK` arm, `musyx_stub` is the only explicit
silent control, `aspMain` and `unknown_task_stub` are not live RS64 audio
routes, and `Broke` remains the required RSP completion edge. No production
audio stub or gate was changed. The old s3028 pre-title result is not a
target-phase qualification; the next run must use AUTOPILOT and phase gates.

Session 3037 synchronized the project symbol TOML for
`0x80017AD0`=`setRenderStateFlagByteThree`; generated code, callers, header,
and overlay registration already agreed. The neighboring setter pair is a
positive structural control. Evidence: `scratch/agent/s3037_generated_symbol_rename/`.

Sessions 3030–3036 audited the next generated-symbol candidates. Exact
companion identities were synchronized for `waitForAnyAudioSlot`,
`initSpeechSubsystem`, and `advancePlayerAnimationPhase`. The candidates
`0x8006ACA4`, `0x8006B704`, `0x8007C298`, `0x80099FDC`, and `0x8009C2C8` remain
mechanically unresolved fragments or boundaries and retain placeholders.
Evidence for each audit is in the corresponding `scratch/agent/s30*_generated_symbol_rename/`
directory and the ledger.

The s3028 paired M5 qualification did not reach title/hangar on either arm,
so its downstream audio nulls were unevaluable. Its corrected driver still
requires a fresh target-phase run; do not infer audio equivalence or a
contract gap from that result.

Session 3052 added a host-side sequence table joining `send_dl` entry/return,
`dp_complete`, DP external enqueue, and DP external delivery. The build
succeeded and the fixed port capture produced 726 sends, 553 returns, 553 DP
completions/enqueues, and 99 deliveries. Same-sequence ordering was
`send-return` → `dp-complete` → `external-enqueue`, with delivery later on the
consumer thread. The phase control fired, but the run again stopped at VI 640
origin `0x0066A500`; title/hangar route preparation never accepted. The first
instrument cap was corrected in-iteration to independent per-edge budgets.
This selects `H-MeasurementInsufficient` for the target-phase discriminator;
no route behavior change was justified. Evidence:
`scratch/agent/s3052_m5_route_order/AUDIT.md`.

Session 3053 extended that table to action dequeue, SP completion, and
display-list callback edges. The retail oracle independently passed its
whole-RDRAM control and reached title/hangar. The port table was positive:
559 action/dequeue and callback rows, 559 DP completion/enqueue rows, and 455
external deliveries. Pre-target ordering was internally consistent but the
port remained at VI 640 with route preparation `accepted=0`. Evidence:
`scratch/agent/s3053_m5_gfx_action_order/AUDIT.md`.

Session 3054 (checkpoint) analyzed the s3053 run.log `osViSetMode_recomp`
data. The game issued exactly 4 osViSetMode calls: widths 320, 2 (corrupt),
640, 640. The game **never called osViSetMode(width=1024)** in the AUTOPILOT
run. The route predicate at `src/main/main.cpp:1376–1380` fires only when
`rs64_vi_committed_width()` returns 1024 (title) or 512 (hangar). Older
successful runs (e.g. PORTING-STATE line 23336) confirm the transition
"vi_width=1024 (was 640) origin=0x00790400" is the correct title-screen
signature. The M4 summary shows steady-state VI at width=640, origin=0x005D4500.
This selects `H-TitleOsViNotCalled`: the game code path that calls
osViSetMode(width=1024) is not reached in current AUTOPILOT runs. All
sessions 3040–3053 returned H-MeasurementInsufficient because the route
predicate is unreachable when the VI never transitions to 1024. The
DP-event, ProducerMark, and action-order measurements are all structurally
downstream of this stall — they were measuring inside a phase that never arms.

Session 3055 attempted the required retail-grounded VI-mode discriminator.
The 90-second port AUTOPILOT arm reproduced exactly four `osViSetMode` calls
(widths 320, 2, 640, 640), zero width-1024 calls, and the VI-640 origin
`0x0066A500`. The corrected oracle arm included the whole-RDRAM positive
control but exited before emulation because the debugger-enabled mupen core
was absent at the documented Homebrew path; the initial recipe also exposed
that this frontend does not support the stale `--positive-rdram` option. No
retail caller/width attribution was obtained, so no VI hypothesis is selected.
Evidence: `scratch/agent/s3055_m5_vi_mode_oracle_setup/AUDIT.md`.

Session 3056 repaired the debugger-enabled mupen64plus prerequisite and ran
the retail-vs-port VI-mode discriminator with both positive controls. Retail's
whole-RDRAM watch reached 10,000 callbacks, then retail reached title at width
1024 around 17.3s and hangar at width 512 around 38.4s. The VI-register watch
attributed the 640→1024 transition to `pc=0x80035798`. The concurrent port
capture logged exactly four `osViSetMode` calls (widths 320, 2, 640, 640), zero
width-1024 calls, and remained at VI 640 origin `0x0066A500`. This selects
`H-TitleOsViNotCalled` for the port and rules out port-side VI suppression for
this capture. Evidence: `scratch/agent/s3056_m5_vi_mode_oracle_setup/AUDIT.md`.

## Next steps

Priority is maintenance, then M5, then systematic M3, then the generated
symbol sweep. Maintenance is complete. M5 design is complete. Step 1 remains
route-blocked at pre-title VI 640 despite a valid retail control and positive
port dispatch controls; target-phase audio rows remain unevaluable. M3 is
parked pending a new discriminator.

1. **M5 VI-mode publication edge — direct callsite boundary required.** Session
   3106 proved the retail mode-entry watch live but did not capture the
   640→1024 transition. Watch `0x8001B8DC`, `0x8001BB54`, and `0x8001B720`
   directly in one oracle run, retaining the whole-RDRAM control and target
   phase trace. A callsite hit at the transition identifies the writer; a
   live target phase with none identifies an unenumerated caller boundary.

2. **M5 VI-mode publication edge — new boundary required.** Session 3105
   selected H-SharedSwapPath: both surviving predecessors are framebuffer
   swaps, not mode writers, and their generated/companion identities agree.
   Do not repeat this caller audit. Revisit the absent retail 1024 writer only
   with a genuinely new external boundary that can attribute its caller or
   descriptor source.

3. **M5 VI-mode publication edge — parked after Session 3094.** The port
   publishes and consumes a live 640 descriptor (`0x80128DF0`) but never
   reaches the retail 1024 transition. The independent retail mode/caller
   watches are live. Revisit only with a genuinely new boundary that can
   discriminate the absent 1024 writer; do not repeat the selector-byte,
   ProducerMark, or current consumer probes.

4. **Generated-symbol sweep — now eligible if no new M5 discriminator is
   available.** The bounded six-surface audit rule remains in force; resume at
   the next unresolved placeholder rather than repeating closed audits.

4. **M5 VI-mode stall — attribute selector-writer inputs.** Session 3076
   ruled out table aliasing, record-copy reorder, selected-pointer mutation,
   and host VI alteration. Attribute the producer inputs for retail
   `[A,B,C]=[1,1,0]` versus port `0x80128DF0`, using the independent oracle and
   one phase-keyed port build. Do not change audio behavior from this result.

5. **Generated-symbol sweep — historical continuation notes.**
   The synchronized region through `0x80017B28` is complete; the preamble at
   `0x800B47C4` is synchronized as `menuControllerInputPreamble` and the
   preamble at `0x800B58B4` is synchronized as `playerAwingInitPreamble`.
   Preserve placeholders for fragments, data gaps, and unresolved boundaries;
   do not invent semantic names. The V-wing boundary at `0x800B89F4` was
   audited and preserved as a fragment; resume at the next candidate
   (`data_gap_800BCC38`)
   only after auditing companion map, generated body, callers, header, overlay
   registration, project TOML, and local duplicates. The `0x800BCC38` record
   was audited and preserved as a data gap; `0x800BEBFC` was synchronized as
   `initDemoPlayStatePreamble`; `0x800BF498` was audited and preserved as a
   data gap; `0x800BF784` was also audited and preserved as a data gap;
   resume at `data_gap_800C7DB4`; `0x800C64A4` and `0x80024878` were audited
   and preserved as data gaps. `fake_func_800555E8` was synchronized as
   `initPlayerStructsPreamble`; `0x8006ACA4` was classified and synchronized
   as `data_gap_8006ACA4`; `fake_func_8006B704` was audited and preserved as
   a callable-ambiguous fragment; `fake_func_8007C298` was then classified and
   synchronized as `data_gap_8007C298`; `fake_func_8009C2C8` was classified
   and synchronized as `data_gap_8009C2C8`. Session 3090 synchronized
   `filterVoiceSampleBlockPreamble`; continue the sweep at the next unresolved
   placeholder.
   If the sweep becomes a
   revisit under the rule in the user instructions, use the external
   retail-entry or M4 boundary instead.

5. **M5 audio de-stubbing — qualify Step 1, then implement one named edge.**
   Resume after the route boundary is repaired or a target-phase route is
   independently reached. Use the phase-keyed task/DMA/return/service/
   slot/voice/MORT/PCM table; do not change a gate, wait, voice guard, or
   output destination from qualification alone.

6. **M5 route repair/handoff — identify a different producer/signal edge.**
   Retain task and phase positive controls and use a genuinely new handoff
   angle only after selector-writer attribution.

7. **M3 crash work — parked.** Resume only as a complete idiom-class audit
   with a named discriminator; passive recurrence belongs in the soak queue.

8. **M4 accumulator origin — blocked at route qualification.** The latest
   revisit had generic controls but zero M4 stage-1 positive-control rows and
   no 512 hangar phase. Do not interpret those nulls.

9. **M5 SP-yield lifecycle validation — parked** pending a route angle that
   reaches target phases.

10. **M5 CPU-side MORT publication — unresolved; callback edge closed.** The
   corrected edge is `serviceStreamingVoice` descriptor `+0x190` to
   `dmaVoiceSampleAndSignal`; `+0x194` is the legitimate speech source. Do
   not repeat this callback audit without a new destination/order edge.

11. **External retail-entry boundary — candidate set rejected (s2903).** The
   oracle reached title/hangar, but the four watched candidate PCs were
   boot/pre-title only. Any revisit needs a different static handoff and
   ground-truth PC attribution.

12. **M5 image task contract / hangar artifact — parked.** No writeback, remap,
   forced state, or mitigation without an `ORIGIN:` naming the writer and
   stating whether its value is legitimate.

13. **M5 route handoff — retail grounded, port route still missing.** Retail
    positively executes `bufferArbiterProducerMark` at `0x8001BCE4` in title
    and hangar. The next route unit must use a new port-side repair/probe
    angle tied to this handoff and retain the positive control.

## Durable boundaries

Factor 5 uses the custom command mappings in
[`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md); do not infer stream
semantics from standard F3DEX. The qualified Factor 5 path is LLE-only.
Interpreter limits, null-GBI guards, and other defensive runtime checks are
safety mechanisms, not explanations.

Ask the retail oracle for ground truth before adding port instrumentation.
Batch every discriminator in one build and run; scope budgets to the target
phase; use SIGKILL and run from `build/`. Follow `make_elf.py` → N64Recomp →
`fixup_game_funcs.py` → CMake. Never hand-edit generated functions for
behavior changes. Never run `git submodule update`, `git checkout -- lib/...`,
`git clean`, or `git reset --hard`. If `lib/` changes, export its patches in
the same iteration. A mitigation-shaped diff requires an `ORIGIN:` line.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed. Failed
experiments remain in the ledger and project overview.

Static boundary-only symbol classifications remain non-renames when companion
symbols, source/m2c, callers, and local semantics do not provide a defensible
name. Stable companion duplicate-prefix and preamble mappings belong in
`tools/rename/build_redefs.py`.

## Archived progression

Sessions through 3043 established the current M5 boundaries, qualified the
rendering route, and advanced the regeneration-safe symbol sweep. Exact
interval results, counts, and run outcomes are preserved in
`PORTING-STATE.md` and `docs/PROJECT-OVERVIEW.md`.
