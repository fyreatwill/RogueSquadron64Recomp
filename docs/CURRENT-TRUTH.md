# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
background is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact run
recipes and historical evidence remain in the append-only ledger.

Current maintenance marker: Session 2979 (2026-08-28).

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
not PCM correctness.

## Latest results

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

## Next steps

Priority is maintenance, then M5, then systematic M3, then the generated
symbol sweep. Maintenance is complete for this iteration. M5 remains active
on audio de-stubbing, with the design survey complete; M3 is parked pending a new
discriminator. The sweep is active under the stable slug
`generated-symbol-renaming-sweep`.

1. **M5 audio de-stubbing — qualify Step 1, then implement one named edge.**
   The design survey is complete in `docs/M5-AUDIO-PLAN.md`. First obtain a
   new route repair or independent handoff that reaches title/hangar so the
   same-build image/silent positive-control row is evaluable. Only then make
   one contract change selected by task → SP → service/slot → PCM evidence.
   Do not repeat the s2978 route capture unchanged.

2. **M3 crash work — parked.** Resume only as a complete idiom-class audit
   with a named discriminator; passive recurrence belongs in the soak queue.

3. **Generated-symbol renaming sweep — continue bounded semantic fragments.**
   Session 2974 renamed three defensible entry fragments to
   `initVoiceSubtitleSystemPreamble`, `initWaterSprayParticlesPreamble`, and
   `filterVoiceSampleBlockPreamble`. Continue with the next bounded batch only
   when successor boundaries and body shape support a semantic name; preserve
   `func_8000040C` and other ambiguous records.

4. **M4 accumulator origin — blocked at route qualification.** The latest
   revisit had live generic controls but zero M4 stage-1 positive-control rows
   and no 512 hangar phase. Do not interpret its M4 nulls. Resume only with a
   genuinely new route repair or an independent ground-truth handoff that can
   make the M4 control execute.

5. **M5 SP-yield lifecycle validation — parked** pending a route angle that
   reaches target phases.

6. **M5 CPU-side MORT publication — unresolved; callback edge closed.** The
   corrected edge is `serviceStreamingVoice` descriptor `+0x190` to
   `dmaVoiceSampleAndSignal`; `+0x194` is the legitimate speech source. That
   routine writes the voice ring and signals completion; it does not publish
   AI data. Do not repeat this callback audit without a new destination and
   ordering edge.

7. **External retail-entry boundary — candidate set rejected (s2903).** The
   oracle reached title/hangar, but the four watched candidate PCs were
   boot/pre-title only. Do not repeat that set or the exhausted broad main-text
   range; any revisit needs a different static handoff and ground-truth PC
   attribution.

8. **M5 image task contract / hangar artifact — parked.** No writeback, remap,
   forced state, or mitigation without an `ORIGIN:` naming the writer and
   stating whether its value is legitimate.

9. **M5 route handoff — retail grounded, port route still missing.** Retail
   positively executes `bufferArbiterProducerMark` at `0x8001BCE4` in title
   and hangar, while s2972's port pair never reaches that phase. The next
   route unit must use a genuinely new port-side repair/probe angle tied to
   this handoff and retain the positive control; do not infer a mismatch from
   the oracle alone.

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
