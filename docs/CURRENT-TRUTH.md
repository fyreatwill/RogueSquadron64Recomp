# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
background is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact run
recipes and historical evidence remain in the append-only ledger.

Current maintenance marker: Session 2962 (2026-08-28).

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
symbol sweep. Maintenance is complete for this iteration. M5 is paused after
repeated route-invalid runs; M3 is parked pending a new discriminator.

1. **M5 audio de-stubbing — plan complete, execution gated by route.**
   `docs/M5-AUDIO-PLAN.md` inventories every active audio stub, trap, gate, and
   safety hatch. Do not interpret service, slot, MORT, or PCM nulls until a
   same-build port run qualifies title/hangar. Do not change behavior without
   an `ORIGIN:` naming the legitimate writer and ordering edge.

2. **M3 crash work — parked.** Resume only as a complete idiom-class audit
   with a named discriminator; passive recurrence belongs in the soak queue.

3. **Generated-symbol renaming sweep — active bounded campaign.** Continue
   from the next unparked placeholder after `0x800B58B4`, currently expected
   to be `0x800B75C4` subject to the census. Exact companion semantic names
   and mechanically proven short data gaps may be renamed across every map
   and generated artifact. Valid executable fragments without callable proof
   remain unchanged. Keep HYPOTHESIS-ID
   `generated-symbol-renaming-sweep`.

4. **M5 SP-yield lifecycle validation — parked** pending a route angle that
   reaches target phases.

5. **M5 CPU-side MORT publication — unresolved; callback edge closed.** The
   corrected edge is `serviceStreamingVoice` descriptor `+0x190` to
   `dmaVoiceSampleAndSignal`; `+0x194` is the legitimate speech source. That
   routine writes the voice ring and signals completion; it does not publish
   AI data. Do not repeat this callback audit without a new destination and
   ordering edge.

6. **External retail-entry boundary — candidate set rejected (s2903).** The
   oracle reached title/hangar, but the four watched candidate PCs were
   boot/pre-title only. Do not repeat that set or the exhausted broad main-text
   range; any revisit needs a different static handoff.

7. **M4 accumulator origin — unresolved.** Producer and consumer registers
   have independent derivations. A future revisit needs one phase/task-keyed
   port probe joining the `B74` writer/value, producer slot, and consumer
   index, with the existing positive-control mark. The oracle cannot observe
   RSP DMEM `0xC70/0xB74`; do not interpret the s2944 pre-title null as an M4
   result.

8. **M5 image task contract / hangar artifact — parked.** No writeback, remap,
   forced state, or mitigation without an `ORIGIN:` naming the writer and
   stating whether its value is legitimate.

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
