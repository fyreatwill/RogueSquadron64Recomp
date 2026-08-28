# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history
is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact counts and recipes
remain in the ledger and scratch artifacts.

Current maintenance marker: Session 2877 (2026-08-27).

## Live result

The qualified port route is `ROGUESQ_LLE_FORCE=1`,
`ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. `ROGUESQ_SPIN_YIELD=1`
is diagnostic. `ROGUESQ_AUTOPILOT` is the reliable in-process driver.

M5 defaults to the Factor 5 image arm. `ROGUESQ_AUDIO_UCODE=0` selects the
silent `musyx_stub` control. Stock `aspMain` is not the retail contract;
MORT is a separate CPU speech boundary.

Qualified runs can reach title (`VI 1024`, origin `0x00790400`) and hangar
(`VI 512`, origin `0x006AB400`) with the appropriate input path. Recent
same-build route-validation pairs instead stalled at pre-title `VI 640`,
origin `0x0066A500`; their target-phase audio rows are invalid. The retail
oracle independently reaches attract, title, and hangar but not a mission.
Every narrow retail claim requires the whole-RDRAM positive control first.

The M5 publication edge remains unresolved. Image-stage DMEM/DMA/completion,
candidate ring destinations, CPU MORT filter state, renderer consumption,
service cadence, and voice streaming are live in qualified windows, but no
legitimate writer, payload, destination, and ordering relation has been named
for the AI source span. The corrected streaming callback edge is
`serviceStreamingVoice` descriptor `+0x190` -> `dmaVoiceSampleAndSignal`;
`+0x194` is the legitimate speech-sample source. That routine writes the voice
ring and signals completion; it does not publish AI data. Speech loading,
slot initialization, cursor advancement, queue, PI, host-AI, mixer, and named
renderer audits likewise found no publication edge.

The mandatory external-boundary revisit (single-source oracle evidence)
qualified the known retail route in one run: the whole-RDRAM positive control
reached 10,000 callbacks and was removed, while VI transitions reached title
1024 (`0x00790400`) and hangar 512 (`0x006AB400`). A broad main-text execution
watch over `0x8003D000..0x80040000` produced 938,889 lifetime hits but no
phase-gated target rows, so it did not identify a new retail-entry dispatcher;
do not repeat this range recipe. This is a measurement of the oracle route,
not a two-source explanation of the port boundary.

The new M5 status-table oracle probe was instrument-valid: its whole-RDRAM
positive control reached 10,000 callbacks and the same driven retail run
reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`. The status
poll changed only slots 16/17 continuously in both target phases, while the
phase-qualified `0x80094648` channel writer ran 256 times with predecessor
`0x80094644`; no discrete status transition or ordering edge aligned with the
writer. This is single-source evidence that the status-table scheduling angle
did not select a port discriminator. It does not explain the M5 publication
gap or authorize a behavior change.

The next post-dispatch oracle probe was instrument-valid after correcting an
initial 320-only run that omitted Rice video. Retail passed the 10,000-write
whole-RDRAM control and reached title/hangar. Scheduler handoff `0x80019CD0`,
SP start `0x80033FCC`, and queue send `0x80019F1C` were active in both target
phases; yield-status `0x80019E14` was absent. The matching same-build port
image/silent pair stopped at pre-title `VI 640 @ 0x0066A500`, with dispatch
controls but no downstream task/audio/SP/queue/PCM markers. This is
route-failure evidence for this port recipe; the retail event table is not
interpretable on the port until a route is qualified.

The single-image route requalification then rebuilt the Debug target and used
the long validated in-process schedule, phase-gated at VI 1024. It stayed at
pre-title `VI 640 @ 0x0066A500` until the 180-second gate timeout, with no
crash or abort marker. Four B40-route and one filter-voice diagnostic lines
were present, but no target-phase task, audio-return, SP, queue, or PCM rows
could be evaluated. This independently reproduces H-route-failure for the
current port recipe and does not select an M5 publication explanation.

The route-repair audit found concrete drift from the last successful hangar
recipe: the active pair had changed the phase gate to 1024, omitted
`PROBE_LEAVE_OK=1` and `ROGUESQ_M4_Y8000_WIDTH=512`, and used a different
driver. A one-build concurrent silent/image A/B restored all three controls.
Both arms reached the positive pre-title checkpoint `VI 640 @ 0x0066A500`
with 47 audio-dispatch markers each, but neither reached hangar
`VI 512 @ 0x006AB400` before the bounded capture was SIGKILLed; neither
crashed or aborted. This rejects configuration drift as sufficient and selects
H-route-state. Downstream audio nulls remain unevaluable.

The s2872 retail-first route-state discriminator was instrument-valid: the
whole-RDRAM control reached 10,082 writes, title, and hangar. Retail's
`0x80141AD0..0x80141AEF` span had 82 writes; target-phase writers were only
`0x80094648` (24 in each phase), while `0x80019CD0`, `0x80033FCC`, and
`0x80019F1C` ran and `0x80019E14` did not. The matching port image/silent pair
again stopped at pre-title `VI 640 @ 0x0066A500` for the full 180-second gate;
both emitted 73 audio-dispatch and 4 B40-route rows, but no title/hangar,
crash, or abort. Their five route-state rows were identical and showed zero
state bytes. This exhausts that state-table discriminator without selecting a
route explanation or permitting a behavior change.

SP-yield state is real API state and the request lifecycle now clears the
previous request before staging the next task. The generic scheduler has two
yield call sites, but no audio-specific generated branch was found. Target
audio-yield reachability is unvalidated because the qualified driver stalls
before the target phases. The AI status shim reports the N64 FIFO-full bit
(`0x40000000`) when buffered audio is full, but no qualified caller was found;
it is not established as the PCM blocker.

The s2873 generated-symbol sweep classified three main-overlay records at
`0x80079278`, `0x80079CD8`, and `0x8007A0E8` as non-callable eight-byte
instruction fragments immediately before named routines. They are now named
`data_gap_*` in the companion map, project symbol map, and generated snapshot;
the rename is recorded in `tools/rename_generated_symbols.py` for regeneration.

The s2874 bounded sweep inspected `0x8007A86C` and `0x8007C298`. Their generated
sizes and isolated instruction fragments are consistent with gaps, but the
companion map supplies only `fake_func_*` plus `defined:true`, with no
source-backed classification. Both remain ambiguous-or-fake and unchanged;
the source table is `scratch/agent/s2874_generated_symbol_rename/source-table.md`.

The s2875 retail-first state-arbiter probe was instrument-valid: the
whole-RDRAM control reached 10,000 callbacks, and the driven retail run reached
title (`634 VI` in `0x00790400:1024`) and hangar (`217 VI` in
`0x006AB400:512`). The `0x80130B40..0x80130B80` state span had 105 lifetime
writes; target-phase writers included `0x8006E4B4` in both title and hangar,
with additional title writers `0x80007628`, `0x8006DC00`, `0x8006DC2C`,
`0x8006DC38`, and `0x800C5B54`. `mainGameLoop` (`0x8003DFA0`) and its
`0x8003E010` body entry each executed once at boot only. This selects a retail
state-writer route lead, not a repeated-loop-entry lead. It does not establish
port absence because the matching port recipe still stops at pre-title VI 640;
no behavior change is authorized. Artifact:
`scratch/agent/s2875_m5_state_arbiter/RESULTS.md`.

The s2876 retail-vs-port writer-equivalence unit was instrument-valid on the
retail side (10,105 whole-RDRAM writes, title and hangar reached, six
`0x8006E4B4` executions). The matching image/silent port pair instead stalled
at non-target 640 `0x005D4500` phase 4; both had zero state rows and no crash or
abort. This selects H-route-invalid for this run, so writer equivalence and
downstream audio remain unevaluable. Artifact:
`scratch/agent/s2876_m5_state_arbiter/RESULTS.md`.

The s2877 retail-first consumer selection was instrument-valid: the whole-RDRAM
control reached 10,000 callbacks, retail reached title and hangar, and a
bounded `0x800B0000..0x800D0000` execution census selected
`playObjectiveVoiceLine2` (`0x800C7D1C`, caller `0x800C5D40`) as a target-phase
audio consumer. The same-build image/silent port pair both stopped at
pre-title 640 `0x0066A500` for the 180-second phase gate, with zero consumer
rows and no crash or abort. This again selects H-route-invalid for the run;
consumer equivalence and downstream audio remain unevaluable. Artifact:
`scratch/agent/s2877_m5_route_state/RESULTS.md`.

The s2878 documented in-process autopilot requalification was run as a
same-build image/silent pair. Both arms reached the positive pre-title
checkpoint `VI 640 @ 0x0066A500`, then timed out at the 180-second title gate;
neither crashed or aborted, and neither reached title or hangar. This selects
H-autopilot-does-not-repair-route and rejects H-arm-divergence for this run.
Downstream consumer and audio rows remain unevaluable. Artifact:
`scratch/agent/s2878_route_autopilot/`.

## Next steps

Priority is maintenance, then M5, then systematic M3, then the generated
symbol sweep. The sweep remains eligible while M5 is open and M3 is parked;
apply only source-backed renames and preserve callable-ambiguous records.

1. **M5 Step 1 new route-state source class.** The barrier, launch-order,
   boot-time-key, phase-relative-key, autopilot, gate-writer, pre-title
   task-field, and broad main-text retail-entry angles are exhausted at the
   current discriminator. The next M5 unit needs a genuinely new
   post-dispatch or scheduling discriminator and must qualify title/hangar
   before interpreting service, slot, MORT, or PCM nulls. The first
   post-dispatch table is ground-truth-qualified but its matching port pair
   was route-invalid; repair or replace the route before reading downstream
   nulls. Do not land a
   behavior change without a named legitimate writer and ordering edge. The
   status-table poll / `0x80094648` alignment angle is now exhausted: it
   reached both target phases but produced no discrete scheduling edge. The
   long-schedule image requalification also reproduced the pre-title route
   stop. The route-control audit restored the concrete recipe drift but both
   arms still stopped at VI 640, selecting H-route-state. The s2875 ground
   truth found target-phase writers in the `0x80130B40` span, led by
   `0x8006E4B4`, while `mainGameLoop=0x8003DFA0` is boot-only; the loop-entry
   sub-angle is exhausted, but writer equivalence remains open. The next unit
   must first use a distinct route-state discriminator or repaired route
   qualification before interpreting downstream nulls. Ground
   truth must precede any port instrumentation. The s2873 pivot
   did not change this unresolved M5 ordering; its next audio behavior change
   still requires a named legitimate contract edge.
2. **M3 crash work — parked.** Resume only as a complete idiom-class audit
   with a named discriminator; passive recurrence belongs in the soak queue.
3. **Generated-symbol renaming sweep.** The s2873 batch completed
   `0x80079278..0x8007A0F0`: three proven data gaps were renamed and no
   callable names were inferred. Continue with the next bounded unresolved
   interval only when M5 has no writer-backed behavior edge; exact companion
   semantic names and mechanically proven short data-gap names are allowed,
   while callable-ambiguous and data-ambiguous entries stay unchanged.
4. **M5 SP-yield lifecycle validation — parked** pending a route angle that
   reaches target phases.
5. **M5 CPU-side MORT publication — unresolved, callback edge closed.** Do not
   repeat the closed callback audit until a new legitimate AI destination and
   ordering edge are named.
6. **External retail-entry boundary — parked.** Return only with a new,
   phase-qualified oracle discriminator; the oracle does not drive missions.
7. **M4 accumulator origin — parked.** The producer, selector, and indirect
   consumer are localized; equality remains unresolved and broad watches are
   not a substitute.
8. **M5 image task contract / hangar artifact — parked.** No writeback,
   remap, forced state, or mitigation without an `ORIGIN:` naming the writer
   and stating whether its value is legitimate.

## Durable boundaries

Factor 5 uses the custom command mappings in [`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md);
do not infer its stream semantics from standard F3DEX. The qualified path is
LLE-only for Factor 5. Existing interpreter safety limits, null-GBI guards,
and other defensive runtime checks remain safety mechanisms, not explanations.

The historical overlay-dispatch explanation is not the current blocker: the
qualified path reaches title and hangar boundaries. Factor 5 image tasks and
CPU MORT speech are separate contracts. A `Broke` return proves task
completion, not PCM correctness. MusyX is not stock `aspMain`; audio remains
partly stubbed, so every de-stub must be incremental and phase-qualified with
a same-run positive control.

Evidence rules: ask the retail oracle for ground truth before adding port
instrumentation; batch all discriminator counters in one build and run; scope
budgets to the target phase; use SIGKILL and run from `build/`; follow
`make_elf.py`, N64Recomp, fixup scripts, then CMake; never hand-edit generated
game functions for behavior changes. Never run `git submodule update`,
`git checkout -- lib/...`, `git clean`, or `git reset --hard`. If `lib/`
changes, export its patches in the same iteration. A mitigation-shaped diff
requires an `ORIGIN:` line.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed. Detailed
failed experiments remain in the append-only ledger and project overview.

Static boundary-only symbol classifications remain non-renames when companion
symbols, source/m2c, callers, and local semantics do not provide a defensible
name. Stable companion duplicate-prefix and preamble mappings belong in
`tools/rename/build_redefs.py`.

## Archived progression

Sessions s2677–s2871 established the current M5 boundaries, repaired the
generated duplicate-symbol collision that blocked the full Debug link,
validated the AI-status and SP-yield shims at compile/link scope, and advanced
the regeneration-safe generated-symbol sweep through
`0x80073500..0x80074500`. The sweep repeatedly found already-synchronized
callables or ambiguous/fake records; source-backed data gaps were renamed only
when their short non-callable structure was proven. Exact interval results,
counts, and run outcomes are in `PORTING-STATE.md` and
`docs/PROJECT-OVERVIEW.md`.
