# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
background is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact run
recipes and historical evidence remain in the append-only ledger.

Current maintenance marker: Session 3033 (2026-08-28).

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
qualified runs reach title and hangar boundaries. Factor 5 image tasks and CPU
MORT speech are separate contracts. A `Broke` return proves task completion,
not PCM correctness. The M5 route dependency remains open, but it no longer
blocks all progress: static generated-symbol work can proceed independently.

## Latest results

Session 3033 audited `0x8006B704`. The companion map has no human identity;
the generated snapshot emits a `0xC`-byte fragment containing a store and two
argument-setup instructions, with no return or callable epilogue, immediately
before `loadCraftShadowTextures`. The token appears only in its generated
definition, header, overlay registration, and project TOML, with no direct
generated callers or duplicate definition. Preserved `fake_func_8006B704`
rather than inventing a callable or data-gap rename. This rules out an exact
companion rename and local duplicate; the fragment remains mechanically
unresolved. Evidence:
`scratch/agent/s3033_generated_symbol_rename/source-table.md`.

Session 3032 classified `0x8006ACA4` as the mechanically supported inline
fragment `fake_func_8006ACA4`. The companion map has no human identity; the
generated token is exactly three floating-point instructions with no return or
callable epilogue, and its `0xC` overlay registration matches that fragment.
There are no direct generated callers or duplicate definitions. Preserved the
placeholder and built `RecompiledFuncs` successfully. This rules out an exact
companion rename, callable-boundary interpretation, and local duplicate for
this address. Evidence:
`scratch/agent/s3032_generated_symbol_rename/source-table.md`.

Session 3031 completed the bounded generated-symbol audit at `0x80066A90`.
The companion map names the unique callable `initSpeechSubsystem`; its
standalone generated `0x170`-byte body, six generated callers, header,
overlay registration, and project symbol TOML agree. No placeholder or local
duplicate definition remains, so no synchronization was needed. This rules
out an ambiguous placeholder, inline-fragment classification, and local
duplicate callable for this address. Evidence:
`scratch/agent/s3031_generated_symbol_rename/source-table.md`.

Session 3028 built the Debug target and ran a same-build concurrent M5
Step-1 image/silent baseline with the independent retail oracle. The oracle
passed the whole-RDRAM positive control at 10,000 callbacks and reached title
1024 at origin 0x00790400 plus hangar 512 at origin 0x006AB400. Both port arms
fired the M_AUDTASK dispatch control 340 times but remained at pre-title VI
640 (0x0066A500), with no title/hangar phase and no downstream task, return,
or DMA rows in the captured summaries; neither arm crashed or aborted. The
first driver omission was corrected in-iteration by adding the documented
autopilot, but the corrected run still did not reach target phases. Repeated
full-log scans made the nominal phase waiter exceed its intended wall-time
budget, so the known processes were SIGKILLed after preserving the capture.
Target-phase audio nulls are unevaluable; this run selects neither the
live-image nor silent-equivalence hypothesis and leaves the route-repair
dependency open. Evidence:
scratch/agent/s3028_m5_step1_contract_pair/RESULTS.md.

Session 3030 completed the bounded generated-symbol audit at `0x800668B0`.
The companion map names the unique callable `waitForAnyAudioSlot`; its
standalone generated `0x68`-byte body, three generated callers, header
declaration, and main-overlay registration agree. Synchronized the stale
project symbol TOML and built `RecompiledFuncs` successfully. This rules out
an ambiguous placeholder, data-gap classification, and local duplicate
callable for this address. Evidence:
`scratch/agent/s3030_generated_symbol_rename/source-table.md`.

Session 3027 completed the bounded generated-symbol audit at `0x80053F7C`.
The companion map names the unique callable `updateAnimatedTextureStreaming`;
its generated 0x300-byte body has matching boundaries, five generated callers,
matching header and overlay registration, and no duplicate callable
definition. Synchronized the stale project symbol TOML and built
`RecompiledFuncs` successfully. This rules out an ambiguous placeholder,
data-gap classification, and local duplicate callable for this address.
Evidence: `scratch/agent/s3027_generated_symbol_rename/source-table.md`.

Session 3026 completed the bounded generated-symbol audit at `0x80040218`.
The companion map names the unique callable `getNextSlotNpcTypeId`; its
generated 0x44-byte body follows one NPC-slot link and returns the linked
type or `0xFFFF`. The generated body, header, overlay registration, and 25
generated callers agree, with no duplicate callable definition. Synchronized
the stale project symbol TOML and built `RecompiledFuncs` successfully. This
rules out an ambiguous placeholder, data-gap classification, and local
duplicate callable for this address. Evidence:
`scratch/agent/s3026_generated_symbol_rename/source-table.md`.

Session 3025 completed the bounded generated-symbol audit at `0x8003E8DC`.
The companion map names the unique callable `slotDispatcherIter`; the
generated body, header, 0x170-byte overlay registration, and 146 generated
references agree, with no duplicate callable definition. Synchronized the
stale project symbol TOML and built `RecompiledFuncs` successfully. This
rules out an ambiguous placeholder, data-gap classification, and local
duplicate callable for this address. Evidence:
`scratch/agent/s3025_generated_symbol_rename/source-table.md`.

Session 3022 classified `0x80024878` as the mechanically supported short
record `data_gap_80024878` immediately before `swizzleTextureRowsToTmem`.
The companion map, generated body/header, and overlay registration agree;
the generated body is only an `addu $sp,$fp,$zero` plus `lw $ra,0x1C($sp)`
fragment, with no duplicate callable definition. Synchronized the stale
project symbol TOML and built `RecompiledFuncs` successfully. This closes the
exact-name and overlay-collision hypotheses without inventing a callable
rename. Evidence: `scratch/agent/s3022_generated_symbol_rename/source-table.md`.

Session 3020 completed the bounded generated-symbol audit at `0x8002221C`.
The companion map, generated body, caller, header, and overlay registration
identify the unique callable as `findAndUnlinkSmallestEntry`; its 0xF0-byte
body performs the material free-list best-fit search and unlink. Synchronized
the stale project symbol TOML and built `RecompiledFuncs` successfully. This
rules out an unnamed data gap and a local duplicate callable for this address.
Evidence: `scratch/agent/s3020_generated_symbol_rename/source-table.md`.

Session 3021 completed the bounded generated-symbol audit at `0x800233B0`.
The companion map names it `texPackTlutAtAllocSlot`, and its 0x164-byte
instruction body matches the documented TLUT allocation/packing wrapper.
The generated snapshot emits that body inline after the preceding callable's
return, with no standalone generated definition, header declaration, caller,
or overlay registration; the address occurs once as an instruction label.
Synchronized the stale project symbol TOML and built `RecompiledFuncs`
successfully, but did not invent a generated callable rename. This rules out
an unnamed companion identity and a local duplicate callable while leaving a
generator function-boundary defect open. Evidence:
`scratch/agent/s3021_generated_symbol_rename/source-table.md`.

Session 3019 completed the bounded generated-symbol audit at `0x8001C260`.
The companion map, generated body, caller, header, and overlay registration
identify the unique callable entry as `waitForPostSwapAck`; its 0x98-byte body
polls the post-swap flag, receives/yields, and clears the flag. There is no
second callable definition or conflicting registration. Synchronized the
stale project symbol TOML and built `RecompiledFuncs` successfully. This
rules out an unnamed data gap and a local duplicate callable for this address.
Evidence: `scratch/agent/s3019_generated_symbol_rename/source-table.md`.

Session 3018 completed the bounded generated-symbol audit at `0x8001BB6C`.
The companion map names the unique generated callable
`selectAndApplyViMode`; its 0xDC-byte body selects/copies a VI mode and calls
`osViSetMode_recomp` and `waitOnVideoQueue`. The generated caller, header, and
overlay registration agree, with no local duplicate callable or conflicting
registration. Synchronized the stale project symbol TOML and built
`RecompiledFuncs` successfully. This rules out an unnamed data gap and a
local duplicate callable for this address. The next sweep candidate is
`0x8001C260`, which requires a fresh ambiguity audit because the scanner found
no standalone generated prologue match. Evidence:
`scratch/agent/s3018_generated_symbol_rename/source-table.md`.

Session 3017 completed the bounded generated-symbol audit at `0x8001B7F0`.
The companion map names the unique generated callable
`applyPendingViChanges`; its 0x2AC-byte body applies pending VI feature bits,
selects the mode structure, and calls `osViSetMode_recomp`. The generated
caller, header, and overlay registration agree, with no local duplicate
callable or conflicting registration. Synchronized the stale project symbol
TOML and built `RecompiledFuncs` successfully. This rules out an unnamed data
gap and a local duplicate callable for this address. The next sweep candidate
is `0x8001BB6C`. Evidence:
`scratch/agent/s3017_generated_symbol_rename/source-table.md`.

Session 3016 completed the bounded generated-symbol audit at `0x8001B7D8`.
The companion map names the unique generated callable
`clearPendingViChanges`; its 0x18-byte body clears the two pending VI words,
and two generated callers, the header, and overlay registration agree. The
project symbol TOML was stale and was synchronized; `RecompiledFuncs` built
successfully. This rules out an unnamed data gap and a local duplicate
callable for this address. The next sweep candidate is `0x8001B7F0`, which
requires a fresh ambiguity audit because the scanner found no standalone
generated prologue match. Evidence:
`scratch/agent/s3016_generated_symbol_rename/source-table.md`.

Session 3013 completed the bounded generated-symbol audit at `0x80019808`.
The companion map and generated artifacts classify it as the same 8-byte
short record `data_gap_80019808`: only `lwc1`/`mul.s`, no generated callers or
duplicate callable definition, immediately before the complete
`awaitFrameSyncMesgBlock`. Synchronized the stale project symbol TOML and
built `RecompiledFuncs` successfully. This rules out an exact semantic rename
and an ambiguous callable identity for this address. Evidence:
`scratch/agent/s3013_generated_symbol_rename/source-table.md`.

Session 3014 completed the bounded generated-symbol audit at `0x8001B7B8`.
The companion map, generated definition, six generated callers, header, and
overlay registration identify the unique callable entry as
`requestViFeatureChange`; only the project symbol TOML was stale. Synchronized
the TOML and built `RecompiledFuncs` successfully. This rules out the
ambiguous-placeholder and duplicate-definition hypotheses for this address.
No runtime, audio, or route behavior changed. Evidence:
`scratch/agent/s3014_generated_symbol_rename/source-table.md`.

Session 3015 completed the bounded generated-symbol audit at `0x8001B7C8`.
The companion map, generated definition, seven generated callers, header,
overlay registration, and `redefs.txt` identify the unique callable entry as
`beginSceneRenderFrame`; only the project symbol TOML was stale. Synchronized
the TOML and built `RecompiledFuncs` successfully. This rules out the
ambiguous-placeholder, data-gap, and duplicate-callable hypotheses for this
address. No runtime, audio, or route behavior changed. Evidence:
`scratch/agent/s3015_generated_symbol_rename/source-table.md`.

Session 3012 completed the bounded generated-symbol audit at `0x80018ED4`.
The companion project has no entry or semantic name; the generated code is a
valid 0x20-byte cache-invalidation loop emitted as a label inside
`packMtxRowFloatToFixed`, with no direct callers or overlay registration.
Preserved the `func_80018ED4` placeholder rather than inventing a name. This
rules out an exact companion rename and a mechanically proven data-gap rename
for this address. Evidence:
`scratch/agent/s3012_generated_symbol_rename/source-table.md`.

Session 3011 completed the bounded generated-symbol audit at `0x8001818C`.
The companion map, generated definition, sole direct caller, and overlay
registration identify the unique callable entry as `advanceVideoFrame`; only
the project symbol TOML was stale. Synchronized the TOML and built
`RecompiledFuncs` successfully. This rules out the ambiguous-placeholder and
duplicate-definition hypotheses for this address. No runtime, audio, or route
behavior changed. The next sweep candidate is `0x80018ED4`, which requires a
fresh ambiguity audit because it has no companion-map semantic entry.
Evidence: `scratch/agent/s3011_generated_symbol_rename/source-table.md`.

Session 3010 completed the bounded generated-symbol audit at `0x80017B88`.
The companion map, generated definition, two direct callers, and overlay
registration identify the unique callable entry as
`buildAndRegisterDefaultMaterial`; only the project symbol TOML was stale.
Synchronized the TOML and built `RecompiledFuncs` successfully. This rules
out the ambiguous-placeholder and duplicate-definition hypotheses for this
address. No runtime, audio, or route behavior changed. The next sweep
candidate is `0x8001818C`. Evidence:
`scratch/agent/s3010_generated_symbol_rename/source-table.md`.

Session 3009 completed the bounded generated-symbol audit at `0x80017B78`.
The companion map assigns the exact operation-level name
`setRenderViewScaleFloat`; the generated definition is a unique 16-byte leaf
that stores `$f12` to `0x8011A840`, and the header/overlay registration already
agree. There are no direct generated callers and no duplicate callable
definition. Synchronized the stale project symbol TOML and built
`RecompiledFuncs` successfully. This rules out the ambiguous-placeholder and
duplicate-definition hypotheses for this address; it does not establish a
more specific meaning for the stored float. No runtime, audio, or route
behavior changed. The next sweep candidate is `0x80017B88`. Evidence:
`scratch/agent/s3009_generated_symbol_rename/source-table.md`.

Session 3008 completed the bounded generated-symbol audit at `0x80017B48`.
The companion map, generated definition, header, overlay registration, and
five direct callers identify the unique callable entry as
`setMissionLevelInitByte`; the project symbol TOML alone was stale.
Synchronized the TOML and built `RecompiledFuncs` successfully. The companion
comment's four-caller count is stale, but the extra generated caller is
coherent and does not create an identity conflict. This rules out the
ambiguous-placeholder and duplicate-definition hypotheses for this address.
No runtime, audio, or route behavior changed. The next sweep candidate is
`0x80017B78`. Evidence:
`scratch/agent/s3008_generated_symbol_rename/source-table.md`.

Session 3007 completed the bounded generated-symbol audit at `0x80017B28`.
The companion map, generated definition, header, overlay registration, and
one direct caller identify the unique callable entry as
`setViewStateTripletBytes`; the project symbol TOML alone was stale.
Synchronized the TOML and built `RecompiledFuncs` successfully. This rules
out the ambiguous-placeholder and duplicate-definition hypotheses for this
address. No runtime, audio, or route behavior changed. The next sweep
candidate is `0x80017B48`. Evidence:
`scratch/agent/s3007_generated_symbol_rename/source-table.md`.

Session 2976 completed the phase-aware independent retail route capture after
the s2975 watch-overhead failure. The oracle now defers execution watches until
the first requested target VI bucket while retaining the whole-RDRAM positive
control. The corrected Rice-backed run passed the control at 10,000 callbacks,
armed at title `1024 @ 0x00790400`, and recorded 1,352 title rows plus 810
hangar rows at `512 @ 0x006AB400` for route PC `0x80019CD8` (all predecessor
`0x80033300`). It supports `H-retail-target-predicate` as single-source
evidence and rules out the absent-retail-route and debugger-overhead
explanations for this capture; it does not establish a port mismatch.
Artifact: `scratch/agent/s2976_m5_route_oracle/RESULTS.md`.

Session 2978 ran the existing port-side route-preparation probe from scratch.
The prior turn-limit block was false: the run produced 1,028 route rows and
3,454 LLE-task positive-control rows. The port remained at boot/pre-title VI
320 (`0x006DD280`), with zero title `1024 @ 0x00790400` or hangar
`512 @ 0x006AB400` phase gates, so the route comparison was unevaluable and
does not select a port route hypothesis. The next unit is the M5 audio
de-stubbing design survey rather than a repeat of this stalled capture.
Artifact: `scratch/agent/s2978_m5_route_port/RESULTS.md`.

Session 2980 audited the prescribed M5 Step 1 prerequisite for a genuinely new
port route repair or independent handoff. The checked-in tree contains only the
existing phase-gated route/VI handoff diagnostics; no new route behavior,
handoff, or target-phase producer is available. The latest port evidence still
stops at VI 640 (`0x0066A500`) while the retail control reaches title/hangar.
Because the Step 1 discriminator requires target-phase rows, no build or A/B
soak was run and all audio downstream hypotheses remain unevaluable. This
iteration is blocked on a concrete route repair or independent handoff, not on
an audio conclusion.

Session 2981 tested that block instead of accepting it as fact. The oracle
control reached title and hangar, but the current port executable reproduced
the pre-title stop under both silent and image arms: the array-based driver
reached VI 640 (`0x0066A500`) and no target phase. Both arms dispatched 42
audio tasks, with no crash or abort. A first legacy-wrapper failure was only a
field-order/string-match defect; the independent array-based driver then
reproduced the route stop. M5 target-phase audio remains unevaluable, so the
next unit is re-scoped to the independent generated-symbol sweep while the
route repair or handoff remains an open M5 dependency.

Session 2982 classified `0x800027B8` as an ambiguous two-instruction
executable fragment between `getOsResetType` and `processPolledControllerData`.
It has no stack frame, return, memory operation, generated caller, or exact
companion semantic name; the companion map intentionally retains
`fake_func_800027B8`. The placeholder remains unchanged. The next sweep
candidate is `0x8001C3FC`. Evidence:
`scratch/agent/s2982_generated_symbol_rename/source-table.md`.

Session 2984 classified `0x8001C3FC` as a mechanically proven one-instruction
data/fixup gap between the complete `dpInterruptHandlerThread` epilogue and
`sinfApprox` prologue. There is no generated caller or exact companion
semantic name; the companion's defined fake entry was synchronized to
`data_gap_8001C3FC` across the project map, generated C/header/overlay files,
and regeneration-safe rename machinery. The generated-functions target built
successfully. The next sweep candidate is `0x80023968`.
Evidence: `scratch/agent/s2984_generated_symbol_rename/source-table.md`.

Session 2985 classified `0x80023968` as a mechanically proven eight-byte
boundary gap. Its body is only `mul.s` followed by `add.s`, between the
complete `getLoadedTextureCount` and `emitMaterialRenderModeDL` routines;
there is no generated caller, standalone entry contract, or companion
semantic identity. Synchronized the companion map, project symbol TOML,
generated C/header/overlay artifacts, and regeneration-safe rename machinery
to `data_gap_80023968`; `RecompiledFuncs` built successfully. The next sweep
candidate is `0x80024128`.

Session 2986 classified `0x80024128` as a mechanically proven eight-byte
fragment containing only two isolated halfword loads between the complete
`emitProfilerBarSegment` and `flushDebugTextOverlay` routines. There is no
direct generated caller, standalone entry contract, or companion semantic
identity. Synchronized the companion map, project symbol TOML, generated
C/header/overlay artifacts, and regeneration-safe rename machinery to
`data_gap_80024128`; `RecompiledFuncs` built successfully. The next sweep
candidate is `0x800555E8`. Evidence:
`scratch/agent/s2986_generated_symbol_rename/source-table.md`.
Evidence: `scratch/agent/s2985_generated_symbol_rename/source-table.md`.

Session 2987 classified `0x800555E8` as a two-instruction tail-call entry
(`j 0x800555F0; nop`) immediately preceding the complete `initPlayerStructs`
body. The companion map identifies the successor exactly, and generated
callers target the successor rather than the fragment. Following the
project's established entry-fragment convention, synchronized the companion
map, project symbol TOML, generated C/header/overlay artifacts, and
regeneration-safe rename machinery to `initPlayerStructsPreamble`.
The `RecompiledFuncs` target built successfully. The remaining generated
placeholder candidates are already covered by earlier ledger classifications,
so the next unit returns to the M5 route-repair/independent-handoff blocker.
Evidence:
`scratch/agent/s2987_generated_symbol_rename/source-table.md`.

Session 2988 ran a same-build paired port capture of the existing host-side
buffer-arbiter retrace transition driver. The control reached pre-title VI 640
(`0x0066A500`) with 45 real Factor 5 audio-task dispatches and five route-state
rows; the treatment (`ROGUESQ_FORCE_BUFFER_PROGRESS=1`) stalled at boot VI 320
(`0x006DD280`) with 57 dispatches and zero route-state or target rows. Neither
arm reached title/hangar, and neither produced crash/abort markers. The shared
task dispatch is a positive control, while the phase divergence selects
`H-repair-harmful` for this implementation and rejects this forced transition
driver as the route repair. It does not identify the missing writer/signal.
Artifact: `scratch/agent/s2988_m5_buffer_repair_ab/RESULTS.md`.

Session 2989 first ran the independent retail oracle with a whole-RDRAM
positive control. Retail reached title and hangar and executed
`bufferArbiterMarkSlotReady` (`0x8001BEC8`) 3,815 times,
`waitOnVideoQueue` (`0x8001BE80`) 11 times, and `bufferArbiterAllocSlot`
(`0x8001BF20`) 7,654 times in target phases; `viRetraceHandlerThread` direct
entry was not observed. This grounds the READY transition and its
`0x8001A2F8` caller as a new port edge. The regeneration-safe probe and
generated output built successfully. The port run passed positive controls
(570 LLE task rows, one filter-voice control, eight shade-DMA controls) but
stayed at VI 640 origin `0x0066A500`, with zero target READY rows and no
crash/abort markers. The target null is unevaluable, not evidence of a port
mismatch. Artifact: `scratch/agent/s2989_m5_new_handoff/RESULTS.md`.

Session 2990 added a regeneration-safe probe at the retail-grounded
`0x8000BFFC` caller edge into `waitOnVideoQueue` (`0x8001BE80`) and built the
Debug target successfully. The corrected phase-gated port run passed its
filter-voice and shade-DMA positive controls but remained at VI 640 origin
`0x0066A500` for the 180-second target wait, with zero wait-edge rows and no
crash/abort markers. The target null is unevaluable, not evidence for
`H-wait-missing`; this edge is now instrumented and the next route unit must
use a different grounded producer/signal or a new repair angle. Artifact:
`scratch/agent/s2990_m5_wait_signal/RESULTS.md`.

Session 2991 added a regeneration-safe probe at both generated callers of the
retail-grounded `bufferArbiterAllocSlot` edge (`0x8001A280` and `0x8001C14C`,
corresponding to retail predecessors `0x8000C13C` and `0x8001C14C`). The Debug
target built successfully. The port passed same-run controls (4,806 LLE task
rows, one filter-voice control, and eight shade-DMA controls) but stayed at VI
640 origin `0x0066A500` through the 180-second title wait, with zero alloc
target rows and no crash/abort markers. The target null is unevaluable, not
evidence for `H-alloc-missing`; no behavior repair was attempted. Artifact:
`scratch/agent/s2991_m5_alloc_signal/RESULTS.md`.

Session 2992 audited the queued ProducerMark premise against the generated
code before instrumenting it. `0x8000C0C4` calls READY
(`bufferArbiterMarkSlotReady`, `0x8001BEC8`); the actual ProducerMark
(`0x8001BCE4`) callers are `0x8000BFE8`, `0x8000C440`, `0x8000C628`, and
`0x8000C64C`. Added the regeneration-safe probe at the dominant actual caller
`0x8000BFE8` and built Debug successfully. The qualified capture passed 80
LLE/audio-task positive-control rows but remained at VI 640 origin
`0x0066A500`, with zero title/hangar phases, zero target rows, and no
crash/abort markers. The target null is unevaluable; the generated-call audit
does select the prior edge premise as mislabeled and rules out treating
`0x8000C0C4` as ProducerMark. Artifact:
`scratch/agent/s2992_m5_producer_signal/RESULTS.md`.

Session 2993 tested a genuinely new locally available route edge: the retail
oracle's dominant `bufferArbiterProducerMark` predecessor `0x8000C628`.
Added the regeneration-safe s2993 probe and built the Debug executable. Silent
and image arms ran concurrently from that same build; both produced 45
audio-task positive-control rows, but both remained before the title gate and
recorded zero target C628 rows, with no crash or abort. The target result is
unevaluable, so this does not refute the port-route dependency. The block was
re-scoped to static symbol work. Independently, `0x80001354` was confirmed by
the companion map, generated definition, and four generated callers as
`runVideoFrameTick`; the project TOML now carries that semantic name.
Artifacts: `scratch/agent/s2993_m5_c628_handoff/` and the s2993 session entry.

Session 2994 completed the bounded generated-symbol audit at `0x800022F8`.
The companion map, generated definition, and generated caller identify the
unique callable entry as `coalesceFreeHeapBlocks`; the generated tree and
companion map already carried that name, so only the project symbol TOML was
stale. Synchronized the TOML and built `RecompiledFuncs` successfully. The
next sweep candidate is `0x80002E10` (`siServiceThread`).

Session 2995 completed the bounded generated-symbol audit at `0x80002E10`.
The companion map, generated definition, overlay registration, and duplicate
check agree on the unique callable name `siServiceThread`; only the project
symbol TOML was stale. Synchronized the TOML and built `RecompiledFuncs`
successfully. The sweep helper cannot resume from a human name because its
parser accepts placeholder names only; this is a tooling limitation, not an
identity conflict. The next placeholder in TOML order is `0x80007D74`.
Evidence: `scratch/agent/s2995_generated_symbol_rename/source-table.md`.

Session 2996 completed the bounded generated-symbol audit at `0x80007D74`.
The companion map, generated definition, and caller set identify the unique
callable entry as `allocateDisplayListBuffer`; the project symbol TOML alone
was stale. The generated body is the display-list free-pool allocator and has
96 callers, with no duplicate generated definition. Synchronized the TOML and
built `RecompiledFuncs` successfully. The next sweep candidate is
`0x8000815C`, whose companion entry has no semantic comment and requires a
fresh ambiguity audit. Evidence:
`scratch/agent/s2996_generated_symbol_rename/source-table.md`.

Session 2997 completed the bounded generated-symbol audit at `0x8000815C`.
The companion map, generated definition, and generated caller identify the
unique callable entry as `drainMeshReleaseQueue`; only the project symbol TOML
was stale. Synchronized the TOML and built `RecompiledFuncs` successfully.
The next sweep candidate is `0x8000C07C` (`submitGfxFrame`). Evidence:
`scratch/agent/s2997_generated_symbol_rename/source-table.md`.

Session 2998 completed the bounded generated-symbol audit at `0x8000C07C`.
The companion map, generated definition, overlay registration, and 14 direct
callers identify the unique callable entry as `submitGfxFrame`; the project
symbol TOML alone was stale. Synchronized the TOML and built `RecompiledFuncs`
successfully. The next sweep candidate is `0x8000CB88`, which has no usable
comment/prologue match and requires an ambiguity audit. Evidence:
`scratch/agent/s2998_generated_symbol_rename/source-table.md`.

Session 2999 completed the bounded generated-symbol audit at `0x8000CB88`.
The companion map, generated definition, header, overlay registration, and
four direct callers identify the unique callable entry as
`reserveAndEmitDLEntry`; only the project symbol TOML was stale. The scanner's
overlay-reuse warning did not correspond to duplicate callable definitions.
Synchronized the TOML and built `RecompiledFuncs` successfully. No runtime,
audio, or route behavior changed. The next sweep candidate was `0x8000DE70`.
Evidence: `scratch/agent/s2999_generated_symbol_rename/source-table.md`.

Session 3000 completed the bounded generated-symbol audit at `0x8000DE70`.
The companion map identifies the entry exactly as `appendRdpStateDl`; the
generated definition, header, overlay registration, and six direct callers
agree, with no duplicate callable definition. The project symbol TOML alone
was stale. Synchronized it and built `RecompiledFuncs` successfully. No
runtime, audio, or route behavior changed. The next sweep candidate is
`0x8000E0BC`. Evidence:
`scratch/agent/s3000_generated_symbol_rename/source-table.md`.

Session 3001 audited `0x8000E0BC` as `selectRenderPresetByIndex`. The
companion map, project TOML, generated header, overlay registration, unique
generated definition, and ten direct callers agree; the TOML was already
synchronized, so this was a confirmation audit with no symbol edit. The
generated-functions target built successfully. The next sweep candidate is
`0x80011C9C`; the placeholder-only scanner limitation was recorded rather
than treated as an identity conflict. Evidence:
`scratch/agent/s3001_generated_symbol_rename/source-table.md`.

Session 3003 audited `0x80015548` as `traverseSceneGraphRecursive`. The
companion map, generated body, header, overlay registration, and caller set
agree on the unique scene-graph walker; the generated tree was already
renamed, so only the project symbol TOML was stale. Synchronized it and built
`RecompiledFuncs` successfully. The scanner's overlay-reuse warning did not
correspond to a duplicate callable definition. No runtime, audio, or route
behavior changed. The next sweep candidate is `0x80017AB0`.
Evidence: `scratch/agent/s3003_generated_symbol_rename/source-table.md`.

Session 3004 audited `0x80017AB0` as `setRenderStateFlagByteOne`. The
companion map, generated body, header, overlay registration, and direct
callers agree on the unique 16-byte setter that stores `a0` at `0x8012A870`
and returns 1; no duplicate callable definition exists. The generated tree
was already renamed, so only the project symbol TOML was stale. Synchronized
it and built `RecompiledFuncs` successfully. No runtime, audio, or route
behavior changed. The next sweep candidate is `0x80017AC0`. Evidence:
`scratch/agent/s3004_generated_symbol_rename/source-table.md`.

Session 3005 audited `0x80017AC0` as `setRenderStateFlagByteTwo`. The
companion map, generated definition, five direct callers, header, and overlay
registration agree; the scanner's overlay-reuse warning is not a duplicate
callable definition. Synchronized the stale project TOML entry and built
`RecompiledFuncs` successfully. No runtime, audio, or route behavior changed.
The next sweep candidate is `0x80017AE0`. Evidence:
`scratch/agent/s3005_generated_symbol_rename/source-table.md`.

Session 3002 audited `0x80011C9C` as `renderUnlitMeshFaces`. The companion map,
generated definition, header, overlay registration, and two direct callers
agree, with no duplicate generated definition. The generated tree was already
renamed, so only the project symbol TOML was stale; synchronized it and built
`RecompiledFuncs` successfully. The scanner's placeholder-only stop is a
tooling limitation, not an identity conflict. The next sweep candidate is
`0x80015548`. Evidence:
`scratch/agent/s3002_generated_symbol_rename/source-table.md`.

Session 2979 refreshed `docs/M5-AUDIO-PLAN.md` from a source survey. The active
audio surface is still the Factor 5 image arm versus the explicit silent
`musyx_stub`; stock `aspMain` and `unknown_task_stub` are not valid RS64
de-stubbing targets. The source contracts are coupled through task dispatch,
DMEM/DMA, `Broke`, SP completion, guest service/slot state, and PCM
publication, while CPU-side MORT remains a separate speech path. This selects
the coupled-contract planning hypothesis, but the s2978 VI-640 pre-title stop
means the downstream positive control has not run and authorizes no gate, wait,
voice, or writeback change. Artifact: `docs/M5-AUDIO-PLAN.md`.

Session 2975 attempted the independent retail route-preparation discriminator
at guest PC `0x80019CD8`. The fixed command used the locally built debugger
core, passed the whole-RDRAM positive control at 10,000 callbacks, and logged
64 route-PC executions, but all were boot-width `320 @ 0x006DD280`; the
per-execution debugger watch prevented the 45-second capture from reaching
title or hangar. This is unevaluable, not evidence for a predicate mismatch;
the next route unit needs a phase-aware breakpoint arm retaining the same-run
positive control. Artifact:
`scratch/agent/s2975_m5_route_oracle/RESULTS.md`.

Session 2974 resumed the regeneration-safe generated-symbol sweep after the
mandatory pivot from route preparation. Three short records were identified as
entry fragments immediately preceding complete companion-named routines:
`0x80055A2C` before `initVoiceSubtitleSystem`, `0x80072CE8` before
`initWaterSprayParticles`, and `0x8009D7CC` before `filterVoiceSampleBlock`.
They were renamed to the corresponding `*Preamble` names in the companion
map, rename table, and generated C/header/overlay artifacts. The generated-
functions target built successfully. No ambiguous fragments or game behavior
were changed. Artifact:
`scratch/agent/s2974_generated_symbol_rename/source-table.md`.

Session 2970 completed the bounded generated-symbol census for the lowest
remaining placeholder, `0x8000040C`. The generated body is a complete `0x34`
-byte callable entry-segment routine that clears caller-supplied memory in
`0x10`-byte units and issues `cache 0x0D`; `main` calls it at two startup sites.
The companion project only hardcodes the address and size in `make_elf.py`, with
no semantic name, independent lookup, or alternate caller contract. It is
therefore callable-but-ambiguous, not a data gap; the placeholder remains and
`RecompiledFuncs` built successfully. This closes the currently generated
placeholder sweep without inventing an address-coded synonym. Evidence:
`scratch/agent/s2970_generated_symbol_rename/source-table.md`.

Session 2971 ran the corrected independent retail-oracle capture for the new
framebuffer-arbiter producer handoff `bufferArbiterProducerMark`
(`0x8001BCE4`). The first Homebrew-core command failed before emulation with
`DebugSetCallbacks failed`; the fixed command used the locally built debugger
core. Its whole-RDRAM positive control reached 10,000 writes, and the retail
route reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`.
The candidate executed 4,267 times, with target-phase rows in both title and
hangar (primarily predecessor `0x8000C628`). This selects
`H-retail-handoff` and rules out an absent candidate or stale route for this
capture as single-source oracle evidence. It does not establish a port
difference. Artifact: `scratch/agent/s2971_m5_route_qualification/RESULTS.md`.

Session 2972 reran the M5 Step 1 same-build silent/image baseline after the
retail handoff qualification. The first reused wrapper exited before launching
the arms; a corrected wrapper then launched both arms from the successful
Debug build. Both dispatched audio (`59` silent, `49` image) but stopped at
port VI 640 (`0x0066A500`), with no title/hangar phase, task-contract,
DMEM/DMA, service, slot/voice, or PCM rows and no crash/abort markers. The
retail oracle in the same artifact passed its whole-RDRAM positive control and
reached title/hangar. This selects `H-port-route` for this capture; all
downstream audio nulls remain unevaluable and no audio behavior changed.
Artifact: `scratch/agent/s2972_m5_step1_qualified_route/RESULTS.md`.

Session 2973 ran the phase-gated M5 route-preparation census after fixing two
wrapper-only zsh formatting defects. The retail oracle in the same artifact
passed its whole-RDRAM positive control and reached title `1024 @ 0x00790400`
and hangar `512 @ 0x006AB400`. Both port arms reached only VI 640
(`0x0066A500`) with no crash or abort. Route preparation was active in both
arms, but every row was non-target (`target=0`, `accepted=0`): 1,027 rows in
silent and 839 in image. No target-candidate or identity-edge row fired. This
selects `H-route-prep-absent` and rules out an audio-arm-specific preparation
divergence for this capture. Downstream audio nulls remain unevaluable.
Artifact: `scratch/agent/s2973_m5_route_preparation/RESULTS.md`.

Session 2968 ran the M5 Step 1 same-build pair after a successful Debug
rebuild. The independent retail oracle passed its whole-RDRAM positive
control (`10000` callbacks) and reached title `1024 @ 0x00790400` plus hangar
`512 @ 0x006AB400`. Both port arms (silent `ROGUESQ_AUDIO_UCODE=0` and Factor
5 image `=1`) dispatched 66 audio tasks but remained at VI 640; neither
reached title or hangar. Both had zero task-contract/image-stage,
audio-return, service/slot, or PCM-boundary rows and zero crash/abort markers.
The downstream A/B discriminator is therefore unevaluable. The matching
pre-title stall rules out an audio-arm-specific route difference, but does not
distinguish audio degeneracy from an image contract gap. No audio behavior
changed. Artifact: `scratch/agent/s2968_m5_step1_image_vs_silent/audit.md`.

Session 2969 ran the prescribed M4 accumulator-boundary revisit after a
successful Debug rebuild. Generic VI controls fired, but the M4 accumulator
probe's stage-1 positive-control path produced zero rows and the route stopped
at VI 640 (`0x0066A500`) after the scheduled AUTOPILOT inputs; there was no 512
hangar phase, no accumulator row, and no crash/abort marker. The M4 hypotheses
are therefore all unevaluable, not selected. Artifact:
`scratch/agent/s2969_m4_accumulator_boundary/audit.md`.

Session 2957 classified `0x800AE3E4` as an ambiguous three-instruction
overlay-boundary fragment. Its final word overlaps the menu overlay's named
`tickEasedCameraKeyframeBlend` entry at `0x800AE3EC`; there is no prologue,
return, caller, independent lookup, or exact companion name. It remains
`fake_func_800AE3E4` with no rename. Artifact:
`scratch/agent/s2957_generated_symbol_rename/source-table.md`.

Session 2958 classified `0x800AEC54` as a mechanically proven 12-byte data
gap: the generated body is an invalid-decode trap, the companion map retains
the fake entry, and no callable references exist. It was renamed to
`data_gap_800AEC54` across the project map, companion map, and generated
artifacts; `RecompiledFuncs` built successfully. Artifact:
`scratch/agent/s2958_generated_symbol_rename/source-table.md`.

Session 2959 classified `0x800B2628` as an eight-byte valid executable
fragment (`lwc1`/`swc1`) between complete callable bodies. It has no
standalone prologue, return, caller, independent lookup, or companion
semantic name, so `fake_func_800B2628` remains unchanged. Artifact:
`scratch/agent/s2959_generated_symbol_rename/source-table.md`.

Session 2960 re-censused the next apparent candidate, `0x800B42BC`, and
found it was already parked by the companion map as a one-word orphan before
`playerXwingInit`, not a callable preamble or data gap. Removed stale local
rename-table entries that would have synthesized `playerXwingInitPreamble` on
future regeneration; `RecompiledFuncs` built successfully. Artifact:
`scratch/agent/s2960_generated_symbol_rename/source-table.md`.

Session 2962 classified `0x800B58B4` as an ambiguous three-instruction
executable fragment immediately before `playerAwingInit` at `0x800B58C0`.
It contains `addiu a3, 0x7f`, a cross-address `jal 0x800E9B10`, and its delay
slot, with no standalone prologue, return, caller, independent lookup, or
exact companion semantic name. The companion explicitly retains the fake
entry and identifies the adjacent real function, which is insufficient to
name the fragment. The placeholder remains unchanged. Artifact:
`scratch/agent/s2962_generated_symbol_rename/source-table.md`.

Session 2961 classified `0x800B47C4` as an ambiguous three-instruction
executable fragment immediately before `menuControllerInput` at `0x800B47D0`.
It has no standalone prologue, return, caller, or independent lookup. The
companion m2c source is keyed to the larger controller routine rather than
this fragment, so no exact semantic name is justified; the placeholder
remains unchanged. Artifact:
`scratch/agent/s2961_generated_symbol_rename/source-table.md`.

Session 2963 classified `0x800B75C4` as a three-instruction executable
fragment (`lui`/`lwc1`/`mul.s`) that is also an internal branch target from
`findLockOnTarget`. It has no standalone prologue, return, independent caller,
lookup, or exact companion semantic name; `playerYwingInit` begins at
`0x800B75D0` with its own prologue. The placeholder remains unchanged. Removed
stale `playerYwingInitPreamble` entries from both regeneration-safe rename
tables so a future reconciliation cannot apply that unsupported name. Artifact:
`scratch/agent/s2963_generated_symbol_rename/source-table.md`.

Session 2965 classified `0x800BCC38` as a mechanically proven 8-byte data/fixup
gap: `playerTieInterceptorUpdate` ends at that address, the generated body is
only `bc1f` plus its delay-slot `nop`, and `playerT16Init` begins at
`0x800BCC40` with its own stack prologue. The companion map independently
records `data_gap_800BCC38` and the same successor boundary. The regeneration-
safe maps already used `data_gap_800BCC38`; removed the stale
`playerT16InitPreamble` override from `build_redefs.py` and regenerated the
companion redefs. `RecompiledFuncs` built successfully. Artifact:
`scratch/agent/s2965_generated_symbol_rename/source-table.md`.

Session 2966 classified `0x800EC6EC` as a mechanically proven 4-byte
data/fixup gap. The generated body is one invalid COP2 word emitted as a
`do_break`, bounded by the complete `destroyObjectOwnedNpcSlot` epilogue and
the independent `tickCraftMountedAnimationEffect` prologue. No generated
caller, independent lookup, or companion semantic name exists. Renamed it to
`data_gap_800EC6EC` across the project map, companion map, generated C/header/
overlay files, and regeneration-safe redefs; `RecompiledFuncs` built
successfully. Artifact:
`scratch/agent/s2966_generated_symbol_rename/source-table.md`.

Session 2967 re-censused `0x800ECE04` and confirmed it as a 12-byte
non-callable fragment between the complete `dispatchSlotActionTwelveByGlobalId`
epilogue and independent `datItemActorNpcHandler` prologue. It has no
standalone prologue, return, generated caller, independent lookup, or
companion semantic name. Synchronized the companion map, project TOML,
generated C/header/overlay artifacts, and regeneration-safe rename path to
`data_gap_800ECE04`; `RecompiledFuncs` built successfully. No generated
placeholder remains after this address. Artifact:
`scratch/agent/s2967_generated_symbol_rename/source-table.md`.

Session 2964 classified `0x800B89F4` as the next ambiguous three-instruction
executable fragment. Its `bnel` targets `L_800B8AD0`, its delay slot increments
`s2`, and its fall-through continues at `0x800B8A00`; there is no standalone
prologue, return, caller, lookup, or exact companion semantic name. The
companion map retains the fake entry and independently names
`playerVwingInit` at `0x800B8A00`. The placeholder remains unchanged.
Removed stale `playerVwingInitPreamble` entries from both regeneration-safe
rename tables. Artifact:
`scratch/agent/s2964_generated_symbol_rename/source-table.md`.

Session 2955 classified `0x800AAADC` as the four-byte entry preamble for
`playerSnowSpeederInit` at `0x800AAAE0`. The body is only `sh a0, 0x1A(v1)`;
there is no standalone prologue, return, independent caller, or lookup. It
was renamed to `playerSnowSpeederInitPreamble` across the project map,
companion map, and generated artifacts. `RecompiledFuncs` built successfully.
Artifact: `scratch/agent/s2955_generated_symbol_rename/source-table.md`.

Session 2954 made the same classification for `0x800AA6CC`, the four-byte
entry preamble of `npcPredictedRangeCheck` at `0x800AA6D0`, and renamed it to
`npcPredictedRangeCheckPreamble`. Session 2953 classified `0x8009D978` as a
non-callable four-byte gap in an audio coefficient table and renamed it to
`data_gap_8009D978`. Session 2952 preserved `0x8009D8BC` as a valid but
callable-ambiguous branch fragment. These entries and their artifacts are
recorded in the ledger.

The latest M5 route work still stops at pre-title VI 640
(`0x0066A500`). Session 2949's retail oracle reached title and hangar and
observed three phase-specific `source_word` families at the route-message
handler, with sampled `branch_state=0x0010`; session 2950's matching port
probe passed the F5 positive control but had invalid guarded pointers and
never reached target phases. Field, timing, and logic explanations therefore
remain unevaluable. Pause this exact route discriminator until a genuinely
new route repair exists.

The soak queue's latest entries are historical failures/terminations, not new
evidence for the current work unit: s2328 exited after 2 seconds, s2680's
recipe returned 127 immediately, and older s1972/s1974 runs respectively
completed 330 seconds and were killed at the 600-second cap. Full details
remain under `scratch/agent/soak_results/` and in `SOAK-RESULTS.md`.

Session 3023 audited `0x8002BB34`. The companion libultra symbol/source tree
has no identity for this address, and the generated tree has no callable
definition, caller, header declaration, or overlay registration. The
placeholder range overlaps the known `__osException` range and ends at
`__osEnqueueAndYield`, so it is not an independently supported function
boundary. Preserved `func_8002BB34` rather than inventing a rename or a
`data_gap_*` classification. Evidence:
`scratch/agent/s3023_generated_symbol_rename/source-table.md`.

Session 3024 completed the bounded generated-symbol audit at `0x8003DFA0`.
The companion map, generated body, header, eight generated caller-boundary
sites, and overlay registration identify the unique callable entry as
`mainGameLoop`; only the project symbol TOML was stale. Synchronized the TOML
and built `RecompiledFuncs` successfully. This rules out the ambiguous-
placeholder and duplicate-definition hypotheses for this address. Evidence:
`scratch/agent/s3024_generated_symbol_rename/source-table.md`.

Session 3029 completed the bounded generated-symbol audit at `0x80062B04`.
The companion map names the unique callable `advancePlayerAnimationPhase`;
its generated 0x178-byte body, five generated callers, header declaration,
and main-overlay registration agree, with no duplicate callable definition.
Synchronized the stale project symbol TOML and built `RecompiledFuncs`
successfully. This rules out an ambiguous placeholder, data-gap
classification, and local duplicate callable for this address. The M5 route
review found no untried in-tree repair: the existing 4-to-5-to-0 host
transition driver was already rejected, while current producer hooks are
observation-only. Evidence:
`scratch/agent/s3029_generated_symbol_rename/source-table.md`.

## Next steps

Priority is maintenance, then M5, then systematic M3, then the generated
symbol sweep. Maintenance is complete. M5 remains blocked on a new route
repair/handoff because the s3028 baseline did not reach target phases and
the s3029 source review found no untried in-tree repair. M3 is parked pending
a new discriminator; continue the generated-symbol sweep while M5 is blocked.

1. **Generated-symbol sweep — continue only with exact companion identities.**
   `0x80019808` was mechanically classified and synchronized as
   `data_gap_80019808`; do not invent a semantic name for it. `0x8001B7B8`
   was synchronized as `requestViFeatureChange`, `0x8001B7C8` as
   `beginSceneRenderFrame`, and `0x8001B7D8` as
   `clearPendingViChanges`, and `0x8001B7F0` as
   `applyPendingViChanges`, `0x8001BB6C` as `selectAndApplyViMode`, and
   `0x8001C260` as `waitForPostSwapAck`, `0x8002221C` as
   `findAndUnlinkSmallestEntry`, and `0x800233B0` as
   `texPackTlutAtAllocSlot` in the project map. The generated body for
   `0x800233B0` is currently an inline fragment with no callable token, so do
   not force a generated rename. Audit the next placeholder candidate
   `0x80024878` was classified as `data_gap_80024878`; do not invent a
   callable name for it. `0x8002BB34` has no companion identity or generated
   callable boundary and remains a placeholder; do not force a rename or gap
   label. `0x8003DFA0` was synchronized as `mainGameLoop`, `0x8003E8DC` as
   `slotDispatcherIter`, and `0x80040218` as `getNextSlotNpcTypeId` in the
   project map. Continue at `0x80062B04` and keep the M5 route
   dependency open below. `0x80062B04` is now synchronized as
   `advancePlayerAnimationPhase`, and `0x800668B0` is synchronized as
   `waitForAnyAudioSlot`; `0x80066A90` is synchronized as
   `initSpeechSubsystem`. The `0x8006ACA4` candidate was audited as a
   three-instruction inline fragment and remains `fake_func_8006ACA4`; audit
   `0x8006B704` was likewise preserved as an unresolved 12-byte fragment;
   audit the next placeholder candidate `0x8007C298`.

2. **M5 route repair/handoff — identify a different producer/signal edge.** The
   s2988 forced 4→5→0 host transition driver is rejected: it regressed the
   port to VI 320 in the paired run. The s2989 READY, s2990 wait-on-video, and
   s2991 alloc probes are unevaluable because the port stopped at VI 640; do
   not repeat them unchanged. The `0x8000C0C4` example was verified to be
   the READY caller, not ProducerMark; the actual ProducerMark caller probe at
   `0x8000BFE8` was also unevaluable because the port stayed at VI 640.
   Resume only with a genuinely new handoff/repair angle or independent
   ground-truth edge, retaining the same-run task positive control plus
   title/hangar phase gates.

3. **M5 audio de-stubbing — qualify Step 1, then implement one named edge.**
   The design survey is complete in `docs/M5-AUDIO-PLAN.md`. First obtain a
   new route repair or independent handoff that reaches title/hangar so the
   same-build image/silent positive-control row is evaluable. Only then make
   one contract change selected by task → SP → service/slot → PCM evidence.
   Do not repeat the s2978 route capture unchanged.

4. **M3 crash work — parked.** Resume only as a complete idiom-class audit
   with a named discriminator; passive recurrence belongs in the soak queue.

5. **M4 accumulator origin — blocked at route qualification.** The latest
   revisit had live generic controls but zero M4 stage-1 positive-control rows
   and no 512 hangar phase. Do not interpret its M4 nulls. Resume only with a
   genuinely new route repair or an independent ground-truth handoff that can
   make the M4 control execute.

6. **M5 SP-yield lifecycle validation — parked** pending a route angle that
   reaches target phases.

7. **M5 CPU-side MORT publication — unresolved; callback edge closed.** The
   corrected edge is `serviceStreamingVoice` descriptor `+0x190` to
   `dmaVoiceSampleAndSignal`; `+0x194` is the legitimate speech source. That
   routine writes the voice ring and signals completion; it does not publish
   AI data. Do not repeat this callback audit without a new destination and
   ordering edge.

8. **External retail-entry boundary — candidate set rejected (s2903).** The
   oracle reached title/hangar, but the four watched candidate PCs were
   boot/pre-title only. Do not repeat that set or the exhausted broad main-text
   range; any revisit needs a different static handoff and ground-truth PC
   attribution.

9. **M5 image task contract / hangar artifact — parked.** No writeback, remap,
   forced state, or mitigation without an `ORIGIN:` naming the writer and
   stating whether its value is legitimate.

10. **M5 route handoff — retail grounded, port route still missing.** Retail
   positively executes `bufferArbiterProducerMark` at `0x8001BCE4` in title
   and hangar, while s2988's control reaches only VI 640 and its forced
   transition treatment regresses to VI 320. The next route unit must use a
   genuinely new port-side repair/probe angle tied to this handoff and retain
   the positive control; do not infer a mismatch from the oracle alone.

## Durable boundaries

Factor 5 uses the custom command mappings in
[`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md); do not infer stream
semantics from standard F3DEX. The qualified Factor 5 path is LLE-only.
Interpreter limits, null-GBI guards, and other defensive runtime checks are
safety mechanisms, not explanations.

Evidence rules: ask the retail oracle for ground truth before adding port
instrumentation; batch every discriminator in one build and run; scope
budgets to the target phase; use SIGKILL and run from `build/`; follow
`make_elf.py` → N64Recomp → `fixup_game_funcs.py` → CMake; never hand-edit
generated functions for behavior changes. Never run `git submodule update`,
`git checkout -- lib/...`, `git clean`, or `git reset --hard`. If `lib/`
changes, export its patches in the same iteration. A mitigation-shaped diff
requires an `ORIGIN:` line.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed. Detailed
failed experiments are preserved in the ledger and project overview.

Static boundary-only symbol classifications remain non-renames when companion
symbols, source/m2c, callers, and local semantics do not provide a defensible
name. Stable companion duplicate-prefix and preamble mappings belong in
`tools/rename/build_redefs.py`.

## Archived progression

Sessions s2677–s2871 established the current M5 boundaries, repaired the
generated duplicate-symbol collision that blocked the full Debug link,
validated AI-status and SP-yield shims at compile/link scope, and advanced
the regeneration-safe symbol sweep. Sessions s2872–s2955 refined the route
boundary and continued the bounded symbol census. Exact interval results,
counts, and run outcomes are in `PORTING-STATE.md` and
`docs/PROJECT-OVERVIEW.md`.
