# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history
is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact counts and recipes
remain in the ledger and scratch artifacts.

Current maintenance marker: Session 2901 (2026-08-27).

## Live result

The s2899 generated-symbol sweep classified `0x80024A0C..0x80024A10` as a
four-byte non-callable record immediately before the companion
`gspF3DEXTextStart` segment. It had no generated call or lookup references and
was renamed to `data_gap_80024A0C` in the companion map, project symbol map,
and generated files; three generated references changed. The complete source
table is `scratch/agent/s2899_generated_symbol_rename/source-table.md`.

The s2900 sweep classified `0x80026B98..0x80026BA0` as one eight-byte
non-callable zlib fragment immediately before `inflateReset`. It has no
generated call or lookup references and was renamed to `data_gap_80026B98` in
the companion source/map, project symbol map, generated C/header, overlay
metadata, and regeneration-safe rename table. Complete source table:
`scratch/agent/s2900_generated_symbol_rename/source-table.md`.

The s2901 sweep classified the five short zlib-overlay records at
`0x8002851C`, `0x80028D58`, `0x800290D8`, `0x80029B14`, and `0x80029D14` as
isolated instruction fragments immediately before established callable
bodies. None has generated call or lookup references beyond overlay metadata;
all five were renamed to `data_gap_*` in the companion map, project symbol
map, generated C/header, overlay metadata, and regeneration-safe rename
table. Complete source table:
`scratch/agent/s2901_generated_symbol_rename/source-table.md`.

The s2902 sweep inspected the complete `0x80029D20..0x8002A080` interval
between established zlib/libultra symbols. It found zero generated
placeholder definitions, so no rename or mapping change was selected. The
next unresolved placeholder is `0x8003DF98`; the complete interval table is
`scratch/agent/s2902_generated_symbol_rename/source-table.md`.

The qualified port route is `ROGUESQ_LLE_FORCE=1`,
`ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. `ROGUESQ_SPIN_YIELD=1`
is diagnostic. `ROGUESQ_AUTOPILOT` is the reliable in-process driver.

M5 defaults to the Factor 5 image arm. `ROGUESQ_AUDIO_UCODE=0` selects the
silent `musyx_stub` control. Stock `aspMain` is not the retail contract;
MORT is a separate CPU speech boundary.

The s2881 M5 Step 1 image/silent re-baseline built successfully and ran the
retail oracle plus both port arms concurrently. The oracle whole-RDRAM control
hit 10,000 writes but reached only pre-title VI 640; both port arms reached
the same `0x0066A500` phase and emitted audio-dispatch controls, then stopped
without title/hangar. No crash or abort occurred. Target-phase task, DMA,
service, slot/voice, MORT, and PCM rows are unevaluable, selecting
H-RouteInvalid for this recipe rather than an audio-contract hypothesis.
Artifact: `scratch/agent/s2881_m5_step1_rebaseline/RESULTS.md`.

The s2882 route-order/stage-call discriminator was instrument-valid: the
retail oracle's whole-RDRAM control reached 10,000 writes and independently
reached title and hangar. Both same-build port arms stopped at pre-title
`VI 640 @ 0x0066A500`; every route prepare was `accepted=0`. The image arm
had 68 pre-title-or-earlier stage-call rows, all `route_valid=0`; the silent
arm had none. This selects H-RouteInvalid for the recipe and leaves
H-RouteOrder versus H-StageCall unevaluable. Artifact:
`scratch/agent/s2882_m5_pretitle_route_order/RESULTS.md`.

The s2888 generated-symbol sweep completed `0x800E0000..0x800F0000`. All
nine placeholders were classified as bounded non-callable records: eight
short fragments and one invalid COP2/trap gap. `0x800E8A34` was renamed to
the existing duplicate-symbol-prefix name for `runDestructionPhaseSequence`;
the other eight received mechanical `data_gap_*` names. The reconciliation
renamed 27 references across generated C, the header, and overlay metadata;
no callable-ambiguous record changed. Artifact:
`scratch/agent/s2888_generated_symbol_rename/source-table.md`.

The s2889 sweep found one placeholder in the next interval, `0x800FA248`.
Its 8-byte generated body is two negative-address `lb` instructions immediately
before `initMission`, and the companion map provides no semantic callable name.
It was mechanically renamed to `data_gap_800FA248` in the companion/project
maps, rename tool, and generated snapshot; three generated references changed
and no old-name references remain. Artifact:
`scratch/agent/s2889_generated_symbol_rename/source-table.md`.

The s2892 sweep completed the main-text placeholder interval
`0x800027B8..0x800027C0`. Its sole 8-byte record contains only an isolated
`addu`/delay-slot fragment immediately before `processPolledControllerData`,
with no callable body or semantic companion name; it was reconciled as
`data_gap_800027B8` in the checked symbol map. The generated snapshot and
rename table were already synchronized, so no generated references changed.
Artifact: `scratch/agent/s2892_generated_symbol_rename/source-table.md`.

The s2894 sweep completed the next main-text interval,
`0x80003380..0x80003430`. Its sole placeholder, the 12-byte record at
`0x80003424`, is an incomplete three-instruction fragment immediately before
`rand`; it has no generated call or lookup references and no semantic
companion name. It was reconciled as `data_gap_80003424` in the companion and
project maps; the generated snapshot was already synchronized. Artifact:
`scratch/agent/s2894_generated_symbol_rename/source-table.md`.

The s2891 sweep completed the mission-overlay placeholder interval
`0x80101CCC..0x80109620`. All 14 records were bounded non-callable fragments
or fixup trap gaps with no semantic companion or independent caller evidence;
they were reconciled as `data_gap_*` in the project and companion maps. The
generated snapshot was already synchronized and exact searches found zero old
names. Artifact: `scratch/agent/s2891_generated_symbol_rename/source-table.md`.

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

The s2874 bounded sweep inspected `0x8007A86C` and `0x8007C298`; both remain
ambiguous-or-fake and unchanged. The s2880 sweep covered `0x8007C300..0x800AF700`:
three `__builtin_trap()` gap-fillers renamed to `data_gap_*`, five ambiguous
executable fragments left unchanged. Source table:
`scratch/agent/s2880_generated_symbol_rename/source-table.md`.

The s2883 sweep examined the next placeholder interval through
`0x800BAA00`. It left the previously audited `fake_func_800B2628` data
fragment unchanged, and renamed five source-backed contiguous preambles to
`playerXwingInitPreamble`, `menuControllerInputPreamble`,
`playerAwingInitPreamble`, `playerYwingInitPreamble`, and
`playerVwingInitPreamble`. The reconciliation changed 15 generated
references across three files. Source table:
`scratch/agent/s2883_generated_symbol_rename/source-table.md`.

The s2884 sweep examined `0x800BAA00..0x800C0000`. Four short mission-overlay
records were proven non-callable data gaps by their generated bodies and exact
companion/TOML boundaries: `0x800BCC38`, `0x800BEBFC`, `0x800BF498`, and
`0x800BF784`. They are now `data_gap_*` in the companion map, project symbol
map, generated snapshot, and rename tool; reconciliation changed 12 generated
references across `funcs_32.c`, `funcs_33.c`, `funcs.h`, and
`recomp_overlays.inl`. No further generated placeholder was found above
`0x800C0000`. Source table:
`scratch/agent/s2884_generated_symbol_rename/source-table.md`.

The s2887 sweep examined the complete `0x800C0000..0x800D0000` interval and
found nine placeholders. All nine were mechanically classified as non-callable
data gaps from exact short boundaries, fragment-shaped generated bodies, or an
explicit trap-filled gap; no unique callable companion name was present. They
were renamed to `data_gap_*` in the companion maps, project symbol map,
generated snapshot, and rename tool. The reconciliation changed 27 generated
references across the generated C, header, and overlay files. Source table:
`scratch/agent/s2887_generated_symbol_rename/source-table.md`.

The s2886 M5 route/contract discriminator rebuilt the Debug target and ran the
image and silent arms concurrently. The retail oracle positive control reached
10,000 callbacks and independently reached title and hangar; its
`0x8006E4B4` execution watch had six boot-time hits and no phase-gated field
rows, while the state-span watch had 105 writes. Both port arms stopped at
pre-title `VI 640 @ 0x0066A500`: image had 66 dispatches, 6,869 rejected route
preparations, and 68 pre-title stage calls; silent had 66 dispatches and 6,886
rejected preparations. Neither produced target-phase task, DMA, service, slot,
MORT, or PCM rows, and neither crashed or aborted. This selects H-RouteInvalid
again, leaves downstream audio unevaluable, and authorizes no behavior change.
After three stalled route iterations, the next unit pivots to the bounded
generated-symbol sweep.

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

The s2879 ground-truth-first route-source census qualified the distinct
`0x8006D900..0x8006F43C` execution range: the retail oracle's whole-RDRAM
control reached 23,501 writes, title `1024`, and hangar `512 @ 0x006AB400`,
with target-phase range hits. The matching same-build image/silent port pair
both reached only pre-title `VI 640 @ 0x0066A500`; each emitted nine
route-source rows (four boot/320 and five pre-title/640), zero target-phase
rows, and no crash or abort. This selects H-route-invalid for this run and
rejects H-arm-specific divergence at the observed route. It does not compare
the candidate source class at title/hangar and authorizes no behavior change.
Artifact: `scratch/agent/s2879_m5_new_route_state/` and
`tools/apply_s2879_m5_route_probe.py`.

## Next steps

Priority is maintenance, then M5, then systematic M3, then the generated
symbol sweep. The sweep remains eligible while M5 is open and M3 is parked;
apply only source-backed renames and preserve callable-ambiguous records.

1. **M5 audio de-stubbing — plan complete, execution gated by route.** The
   s2886 route/contract pair again selected H-RouteInvalid; pause this exact
   discriminator after three stalled iterations and require a genuinely new
   route repair before another M5 run.
   `docs/M5-AUDIO-PLAN.md` now contains the current inventory of every active
   audio stub, trap, gate, and safety hatch plus the incremental validation
   sequence. The s2885 survey found no additional production audio path. The
   barrier, launch-order,
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
3. **Generated-symbol renaming sweep — remaining placeholders below `0x8010`.** The s2873 batch completed
   `0x80079278..0x8007A0F0`. The s2880 sweep covered `0x8007C300..0x800AF700`:
   three `__builtin_trap()` gap-fillers (`0x80099C4C`, `0x800AEC54`, `0x800AF6A8`)
   were renamed to `data_gap_*`; five ambiguous executable fragments were left
   unchanged. The s2883 batch then renamed five proven preambles through
   `0x800BAA00`; continue with the next bounded interval after `0x800BAA00`
   only when M5 has no writer-backed behavior edge; exact companion semantic names
   and mechanically proven short data-gap names are allowed, while
   callable-ambiguous and data-ambiguous entries stay unchanged. The s2887
   sweep renamed nine data gaps through `0x800D0000`, and s2888 renamed nine
   more records through `0x800F0000`, and s2889 renamed the single data gap at
   `0x800FA248`; s2890 renamed the adjacent data gaps at `0x800FBE14` and
   `0x800FEF04`; s2891 then reconciled all 14 placeholders through
   `0x80109620` as bounded data gaps. The s2892 sweep then reconciled the
   next main-text record at `0x800027B8` as a bounded data gap; s2893
   reconciled the four-byte `0x8000337C` fragment as `data_gap_8000337C`.
   Continue with the next remaining placeholder after `0x80003380` unless M5
   gets a new writer-backed route or contract discriminator. s2894 classified
   `0x80003424..0x80003430` as a bounded non-callable data gap; continue after
   `0x80003430`. s2895 classified `0x8000537C..0x80005380` as a bounded
   invalid/data gap caused by a false split reference before `initRsMallocHeap`;
   s2896 classified `0x80005568` and `0x8000595C` as bounded non-callable
   fragments before `piDmaWorker` and `initMemoryPack`; s2897 classified
   `0x80006BFC..0x80006C00` as a bounded isolated store fragment after
   `initMemoryPack`; s2898 classified the false split tail at `0x80007064`
   and four short records through `0x80007910` as data gaps; s2899 classified
   `0x80024A0C..0x80024A10` as a data gap before `gspF3DEXTextStart`; continue
   s2900 classified `0x80026B98..0x80026BA0` as a data gap before
   `inflateReset`; s2901 then classified the five zlib fragments through
   `0x80029D20` as data gaps. s2902 inspected the following
   `0x80029D20..0x8002A080` established-symbol interval and found no
   placeholders; continue with `0x8003DF98`.
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
