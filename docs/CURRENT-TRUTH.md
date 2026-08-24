# Rogue Squadron 64 Recomp — current truth

Operational front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history through s2302 is summarized in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md)
§46; the append-only ledger is authoritative for exact commands, counts, and
probe rows.

Maintained in Session 2305 (2026-08-24). Session 2303 was the maintenance
iteration that migrated durable s2263–s2302 history to §46, pruned closed
detail, and renumbered the active backlog. Session 2304 ran the M5
task→stage→PCM ordinal join; s2305 extended it to a corrected bounded
temporal join.

The current M5 boundary is task/output contract work. The qualified default
Factor 5 image arm reaches title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`; a prior measured nonzero phase-10 slot class had exact
source and consumer joins. Retail independently reaches both origins and
supplies a different task/output writer class. The latest C88 route discriminator was
coverage-invalid before title/hangar, so it provides no C88 or key-on verdict.
The latest M5 temporal table passed retail and port route controls and matched
both nonzero image-stage rows to exact DMA. For the observed pair,
`0x166450`/`nz=621` has no PCM tuple anywhere in the retained phase and is
independently `stage-only`; `0x166750`/`nz=639` has source and consumer at
ordinal `+12`, with correct event ordering, and is independently
`stage-consumer-match`. This selects an unconsumed output at the first tuple,
not a universal delay or a too-narrow ordinal window.

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The old boot/menu overlay explanation is closed.
- The qualified route uses `ROGUESQ_LLE_FORCE=1`,
  `ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_LLE_UNGATED=1`, and
  `ROGUESQ_LLE_SOLO=1`. Spin yield is environment-gated and default-off.
- Product multi-header freelist restore is on. Garbage-CIMG and wrap-drop
  mitigations are off. Any future mitigation must name the writer, state
  whether the value is legitimate, and include an `ORIGIN:` line.
- M5 audio defaults to the Factor 5 image arm. `ROGUESQ_AUDIO_UCODE=0`
  selects the silent `M_AUDTASK` `Broke` stub for controls. The image arm does
  real DMEM work and generated DMA, then returns `Broke`; its host canary is
  probe data only. Stock `aspMain` is not the game's MusyX/Factor 5 contract,
  and MORT is a separate CPU speech asset.
- The default image arm is qualified through the same title/hangar route as
  the stub at the tested recipe scope. The measured output contract is
  mixed for the observed nonzero tuples: one exact tuple closes through PCM
  source/consumer and one remains stage-only. No writeback, consumer, writer,
  slot, gate, guard, address remap, or default change is authorized.
- The retail oracle is an independent witness. Its whole-RDRAM, title, hangar,
  width-aware target, and exact-PC controls must pass before a null is read.
  The oracle currently reaches attract/title/hangar, not a mission.
- Generated-symbol renaming is closed at the useful boundary. Do not recensus
  or invent names for the five remaining placeholders:
  `func_8000040C`, `func_800927B0`, `func_80092A54`, `func_80092CF0`, and
  `func_800E9AE0`.

## Latest evidence

- **s2305 — bounded temporal task→stage→PCM join.** The same-run retail
  whole-RDRAM `10,000`, title/hangar, and target writer-PC controls passed, as
  did the port title/hangar gates. Both nonzero phase-10 stage rows had exact
  DMA (`2/2`). The `0x166450`, `0x300`, `2B9E9631`, `nz=621` row had no exact
  source or consumer tuple within `±64` or anywhere in the retained phase;
  native joining reported `stage-only`. The `0x166750`, `0x300`, `6ADD4218`,
  `nz=639` row matched source and consumer ordinal `12` (`delta=+12`) with
  DMA-before-source and source-before-consumer; native joining reported
  `stage-consumer-match`. This selects `H-StageUnconsumed` for the observed
  pair, rules out `H-OrdinalWindowTooNarrow` for the first row, and does not
  authorize a contract or mitigation change.

- **s2302 — C88 route coverage.** Retail passed whole-RDRAM `10,000`, title,
  hangar, and all-eight transfer-PC controls. Port C88=0 reached the initial
  `640 @ 0x00696100`, emitted positive fingerprint rows, settled at
  `route_state=2`, `b40=1`, `key_on=0`, and bus-crashed at guest PC
  `0x8000834C` before title/hangar. The required hangar gate withheld C88=1.
  This is `H-CoverageInvalid` at recipe scope; it does not select a C88 route,
  pointer/data, branch-state, key-on return, or mitigation.
- **s2304 — task→stage→PCM ordinal join.** The fixed capture passed retail
  whole-RDRAM `10,000`, title/hangar, and target writer-PC controls, and the
  port reached title/hangar. Its complete nonzero phase-10/hangar table had
  two image-stage rows (`0x168E50`/`0x169150`, `0x300`, `nz=621/639`). Both
  matched exact same-ordinal DMA tuples; neither matched a same-ordinal PCM
  source or consumer (`2/2`, `0/2`, ordering `NA`). Native image joining
  independently reported both as `stage-only`. Its exact two-row result is
  retained for that capture, but s2305 found a different phase-10 pair with
  one complete temporal join; the `0/2` same-ordinal result is not a
  route-wide output conclusion.
- **s2301 — task/output sequence.** The fixed retail capture passed whole-RDRAM
  `10,000`, title, hangar, and `1,530` width-aware target VI rows. The retained
  sequence had `48` sentinel rows from `0x80094648`, then adjacent same-tuple
  rows from `0x8008EB8C` and `0x8008EBBC` at
  `0x141AD0 = 0x120E0000`; the independent writer histogram matched `48/1/1`.
  This selects `H-SharedSequence` at the measured span. A shorter control run
  had no target rows and was treated as coverage-invalid.
- **s2291–s2300 — retail boundary.** Retail metadata can publish the same
  destination pointer and `0x300` length as a port image tuple, but the retail
  payload-producing writer class differs from the port Factor 5 image-DMA
  edge. Retail writes all 16 candidate `0x300` slots from `0x166450` through
  `0x169150` via `0x800078EC`; none is written in the hangar target phase.
  The independent task/output span `0x141AD0:0x141AF0` instead exposes the
  target writer family `0x8008EB8C`, `0x8008EBBC`, and `0x80094648`. Sentinel
  filtering, phase latching, and the extended sequence capture resolved the
  row-cap artifacts but did not assign semantic roles. This selects
  `H-RetailDifferentWriter` plus `H-SharedSequence` at their measured scopes.
- **s2290 — default image arm.** Corrected explicit keycode-36 Start delivery
  and a hangar gate qualified both the silent stub and default image arms.
  The default target window contained nonzero image payloads with `nz=621` and
  `nz=639`; the stub had no image-stage rows. This qualifies the default at
  recipe scope, not a new writer or mitigation.
- **s2287–s2289 — retail route.** Independent retail controls passed and
  retail executed the equivalent initial-640 slot route (`110` iterator,
  `2` inner, `5` batch rows), while the exact port crash PCs were absent.
  This closes the narrow hypothesis that retail omits slot dispatch, without
  identifying the port callback/list state.
- **s2283–s2286 — A1 route.** Four-arm and corrected two-wave VI matrices
  passed their positive controls but failed in the same initial width-640
  route before either target origin. Logger removal changed the crash PC but
  did not restore coverage. These are route-invalid/route-intrinsic recipe
  observations, not VI-publisher or audio-writer conclusions.
- **s2272 — qualified output.** A corrected staggered pair kept both arms
  qualified through title/hangar. Two nonzero phase-10 rows each matched PCM
  source and consumer tuples with source-before-consumer ordering and no
  stage-only or ordering-violation rows. Earlier paired failures were
  route-invalid and do not overturn this result.

## Active backlog

Closed investigations are not active work items. This is the single monotonic
sequence; #1 is the next work unit.

1. **M5 Step 3 unconsumed-edge attribution.** Use one same-run capture to
   attribute the `0x166450` stage-only tuple against the `0x166750` tuple that
   closes through PCM, with the independent retail writer controls and a
   phase-scoped writer/source/consumer table. Do not change runtime behavior
   or add writeback/consumer/slot mitigation.
2. **M5 key-on tuple contract — parked.** Resume only with a genuinely new
   route discriminator that restores `512 @ 0x006AB400`. The s2302 C88=0
   crash had `route_state=2`, `b40=1`, `key_on=0`; C88=1 was withheld.
3. **M5 A1 second-origin transition — parked.** Resume only with a new
   discriminator that restores `0x00696100`/`0x00696600` coverage; do not
   repeat the failed four-arm/two-wave matrix.
4. **M5 drain in-loop tick A/B — parked.** Resume only with a new renderer
   or ground-truth discriminator that places both arms in one target window.
5. **M3 crash work — parked.** Resume only as a systematic idiom-class audit
   with a named discriminator; do not chase a single recurring crash.
6. **Hangar visual artifact — parked.** Malformed-triangle H2 and consumer
   mode H1 are refuted. H3 is unavailable because the oracle cannot
   screenshot the LLE path; do not repeat the capped `0xD60` scan.

## Durable boundaries

### Route, rendering, and Factor 5

The accepted route table selects `LLE_UNGATED=1, LLE_SOLO=1`: the `11` arm
reaches title and hangar, `01` reaches title only, and `10`/`00` reach neither.
Menu spin yield is a diagnostic route aid, not a default behavior change.
Factor 5 command mappings and independent-ground-truth requirements live in
[`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md) and
[`tools/oracle/README.md`](../tools/oracle/README.md). The runtime cannot be
its own witness for a null.

### M5 audio and image output

`docs/M5-AUDIO-PLAN.md` inventories the active audio stubs, traps, gates, and
the incremental task→DMA→service→slot→voice→PCM validation sequence. Direct
service entry/exit, the service gate/loop, slot-0 status sequence, and the
task/AI boundary are live on the port. Retail independently matches the
status cycle. MORT speech is separate from Factor 5 RSP audio.

The image arm changes DMEM, completes, and emits generated DMA. A prior
qualified phase-gated capture observed exact nonzero stage/source/consumer
joins with source-before-consumer ordering; s2304's pair had no same-ordinal
PCM endpoints. The corrected s2305 temporal table found a mixed pair: the
`0x166450`/`nz=621` tuple stayed `stage-only` even across the full retained
phase, while `0x166750`/`nz=639` joined to source and consumer at ordinal
`+12`. The silent arm's PCM boundary is separately qualified but all-zero.
Retail writes corresponding field spans and a different task/output span. This
is a measured contract boundary, not permission to add a copyToRAM/CIMG
writeback, writer guard, slot guard, consumer change, or address remap.

### VI state and second origin

Retail's `__osViNext` context uses `framep` plus the selected field to produce
the next origin. The port has matching framebuffer/mode candidates, but its
default selector, guest `comRegs.vCurrent`, and published current-line bit
remain zero. Opt-in field/current-register/timing/total-`VI` arms recover the
split, but the natural host publisher and cadence are unidentified. The A1
matrices were route-invalid and do not select any VI arm.

### Key-on, M3, and M4

Retail reaches the alternate key-on transfer path and skips the eight port
divide PCs. The port has positive normal-tail/slot behavior with divisor
`0xC0` and no guard hits. Exact `(origin,width,PC)` tuple buckets differ in
both directions. A qualified port pointer/source/state witness exists, but
retail raw addresses vary and the common target window for a full join is
not currently restored. The `-0x25A4` pointer-chase, six-site PIC,
ten-site audio-slot, slot-dispatch, two-line overlay-move, and leftover
`fake_func_*` size-class audits are closed at their stated scopes.

## Superseded conclusions

The following were believable before qualified route and independent controls,
but are superseded at their measured scopes:

- The old overlay/menu explanation, “640 is intrinsically flaky,” missing
  input/wait-return claims, and unqualified PCM-null claims.
- Clean-stub, canary-poison, final-E50, uniform-gate, host-isolator, and
  global-zero image-DMA explanations.
- s2190–s2197 second-origin/caller explanations that were coverage artifacts;
  the open boundary is host VI-state publication/cadence.
- s2228 detail-ring and s2242–s2259 image/pair crash splits as intrinsic
  image or writer defects; they are intermittent route-load observations.
- s2283/s2284 A1 matrices as evidence against a particular VI publisher;
  both lacked target-origin coverage.
- s2288's stub-first route conclusion as a default/audio-null result; s2290
  supplied explicit input and qualified both arms.
- The logger-removal explanation from s2286; removing the logger changed
  timing/PC but did not restore the target route.
- s2304's two-row `0/2` same-ordinal PCM gap as a route-wide output result;
  s2305's corrected guest-address normalization and independent native join
  found one `+12` source/consumer pair in a different observed tuple class.

## Evidence and safety rules

- Ask the retail oracle for ground truth before adding an instrument. Arm its
  whole-RDRAM positive control first; watches are physical addresses and must
  be phase-gated by VI callbacks.
- A null is worthless without a same-run positive control. Batch every arm and
  counter in one build/run, scope budgets to the phase, and use VI gates rather
  than elapsed time for animated scenes.
- Regenerate in order: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then
  CMake. Diagnostics in generated output belong in fixup scripts.
- Kill runs with SIGKILL, never SIGTERM. Run from `build/` with the ROM
  present. Capture paths must not start with `.` in the final component.
- Do not run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. If `lib/` changes, export submodule patches in the same
  iteration.
- A mitigation is not an explanation: name the writer, state legitimacy, and
  add an `ORIGIN:` line before landing a skip, allow, guard, or restore.
- Never add a diagnostic field without a complete discriminating table and an
  outcome that can select among hypotheses.
