# Rogue Squadron 64 Recomp — current truth

Operational front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history through s2302 is summarized in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md)
§46; the append-only ledger is authoritative for exact commands, counts, and
probe rows.

Maintained in Session 2313 (2026-08-24). Session 2303 was the maintenance
iteration that migrated durable s2263–s2302 history to §46, pruned closed
detail, and renumbered the active backlog. Session 2304 ran the M5
task→stage→PCM ordinal join; s2305 extended it to a corrected bounded
temporal join; s2306 extended it to a 45-second recurrence capture with a
per-destination payload-mismatch summary; s2307 extended that capture across
all retained target phases; s2308 added phase-scoped writer provenance and
discovered that the nonzero ring slots rotate between captures; s2309 added
retail whole-ring writer/value ground truth; s2311 added a title-phase writer
census alongside both active 512 target buckets; s2312 added both recurring
post-title 512 origins and found no phase-attributed writer rows in any of the
five distinct configured buckets.
Session 2313 added the two earlier 640 origins and again found no
phase-attributed writer rows, despite positive callback coverage in both.

The current M5 boundary is task/output contract work. The qualified default
Factor 5 image arm reaches title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`; measured nonzero phase-10 slots have exact source and
consumer joins in some captures. Retail independently reaches both origins
and supplies a different task/output writer class. The latest C88 route
discriminator was coverage-invalid before title/hangar, so it provides no C88
or key-on verdict. The s2309 phase-gated table found the current port pair at
`0x168850`/`len=0x300`/`fnv=60F910DE`/`nz=621` and
`0x168B50`/`len=0x300`/`fnv=7B70923A`/`nz=639`. The first had exact source
and consumer events, then a same-destination image-DMA rewrite to
`F59C39C5`/`nz=0`; the second remained stage-only. Retail's whole-ring
watch wrote all `0x3000` bytes and its final snapshot had `12026` nonzero
bytes, forcing at least `506` nonzero bytes in the observed `0x168850` slot.
That aggregate/final-snapshot result still selects `H-PortOnlyZeroFill` at
its capture scope. The s2312 same-run title plus four 512 buckets found all
five distinct phase buckets empty for the sixteen retail slot writers, while
the lifetime writer control remained positive and all final slot snapshots
were nonzero. Session 2313 added `0x0066A500:640` and `0x00696100:640`; both
had positive VI coverage (`18` and `202`) but no phase writer-PC rows. This
selects `H-Retail-Earlier-Or-Unattributed` at capture scope across all seven
configured buckets. The stage-only row and game-level legitimacy remain open.
No runtime behavior change is authorized.

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
  the stub at the tested recipe scope. The measured output contract remains
  capture-dependent: s2306 had one exact source/consumer pair and one
  stage-only row, s2307 found two fixed-address payload mismatches, s2308
  found a rotated pair with exact nonzero publication followed by later
  image-DMA zero writes, and s2309 independently showed aggregate retail
  nonzero final data. In s2310 the current port pair was
  `0x166750`/`0x166A50`; both were stage-only and later zero-filled by
  image-DMA, while retail's lifetime slot writers were outside both
  `0x006AB400:512` and `0x006AB800:512` phase buckets. Thus
  `H-PortOnlyZeroFill` remains an aggregate/final-snapshot result, and
  `H-SlotRoleTimeSkew` is selected for target-phase polarity. No writeback,
  consumer, writer, slot, gate, guard, address remap, or default change is
  authorized.
- The s2312 retail writer census retained the title and both active 512
  buckets and added `0x00656400:512` and `0x00656800:512`. All sixteen
  lifetime slot writers remained positive at `0x800078EC` with `768` writes
  each, but none of the five distinct phase buckets had a writer-PC row; all
  sixteen final snapshots were nonzero.
- **s2313 — earlier 640-origin retail writer census.** The same-run capture
  passed whole-RDRAM `10000`, title/hangar VI coverage, ring writes `12288`,
  all sixteen lifetime writer controls (`768` each), all seven phase callback
  controls, and all sixteen nonzero final snapshots. The new
  `0x0066A500:640` and `0x00696100:640` buckets had `18` and `202` VI
  callbacks, respectively, but no phase writer-PC row; neither supplied the
  missing publication phase. The complete seven-bucket × seventeen-watch
  phase matrix was empty for writer PCs. The port's observed pair was
  `0x168850`/`0x168B50`, with stage FNV/nz `2B9E9631/621` and
  `6ADD4218/639`, exact source/consumer events `11801/11802` and
  `11810/11811`, and later zero PCM events `11873/11874` and `11882/11883`;
  `0x168B50` also had a later zero image-stage event `11820`. This confirms
  the earlier-origin gap at capture scope and leaves writer attribution and
  game legitimacy open. No runtime or contract change was authorized.
- The retail oracle is an independent witness. Its whole-RDRAM, title, hangar,
  width-aware target, and exact-PC controls must pass before a null is read.
  The oracle currently reaches attract/title/hangar, not a mission.
- Generated-symbol renaming is closed at the useful boundary. Do not recensus
  or invent names for the five remaining placeholders:
  `func_8000040C`, `func_800927B0`, `func_80092A54`, `func_80092CF0`, and
  `func_800E9AE0`.

## Latest evidence

- **s2313 — earlier 640-origin retail writer census.** The same-run capture
  passed whole-RDRAM `10000`, title/hangar VI coverage, ring writes `12288`,
  all sixteen lifetime writer controls (`768` each), all seven phase callback
  controls, and all sixteen nonzero final snapshots. The new
  `0x0066A500:640` and `0x00696100:640` buckets had `18` and `202` VI
  callbacks, respectively, but no phase writer-PC row; the complete
  seven-bucket × seventeen-watch phase matrix was empty. The port's observed
  pair was `0x168850`/`0x168B50`, with stage FNV/nz `2B9E9631/621` and
  `6ADD4218/639`, exact source/consumer events `11801/11802` and
  `11810/11811`, and later zero PCM events `11873/11874` and `11882/11883`;
  `0x168B50` also had later zero image-stage event `11820`. This confirms the
  earlier-origin gap at capture scope and authorizes no runtime or contract
  change.

- **s2312 — retail writer earlier-origin gap.** The same-run capture passed
  whole-RDRAM `10000`, title/hangar VI coverage, ring writes `12288`, all
  sixteen lifetime writer controls (`768` each at `0x800078EC`), nonzero
  final ring and slot snapshots, port title/hangar, and 45-second retention.
  The five distinct phase buckets had positive VI callbacks but no
  phase-attributed writer rows: `0x00790400:1024=631`,
  `0x006AB400:512=1895`, `0x006AB800:512=2386`,
  `0x00656400:512=2258`, and `0x00656800:512=1767`. This selects
  `H-Retail-Earlier-Or-Unattributed` and rules out both new post-title
  origins plus coverage invalidity at this capture scope.

  The current port pair was `0x166D50`/`0x300`/`60F910DE`/`nz=621` and
  `0x167050`/`0x300`/`7B70923A`/`nz=639`. The first was stage-only at event
  `9472`, with later zero PCM events `13497/13498` and image-stage event
  `13551`. The second matched source/consumer events `9572/9573` after stage
  event `9474`, then later emitted zero image-stage events `9577/9642` and
  zero PCM events `9637/9638`. No contract or runtime change was authorized.

- **s2311 — retail writer other-phase result.** The same-run capture passed
  whole-RDRAM `10000`, title/hangar VI coverage, ring writes `12288`, all
  sixteen lifetime writer controls (`768` each), title/target phase callback
  controls (`632`/`2735`/`1536`), port title/hangar, and 45-second retention.
  The `0x00790400:1024`, `0x006AB400:512`, and `0x006AB800:512` writer-PC
  buckets were all empty; all sixteen final slot snapshots were nonzero.
  The VI trace showed recurring post-title 512 origins `0x00656400` and
  `0x00656800` (25 and 44 callbacks in the retained trace), so this selects
  `H-RetailOtherPhase` and leaves the two-origin split for the next census.
  The current port pair was `0x169150`/`0x166450`, both `len=0x300`, with
  stage FNV/nz `2B9E9631/621` and `6ADD4218/639`. Each had an exact source
  and consumer match at events `9704/9705` and `9706/9707`, followed by
  zero-payload source/consumer rows at `9776/9777` and `9778/9779` and
  later zero image-stage rows at `9781` and `9788`. No contract, writer,
  slot, consumer, or mitigation change was authorized.

- **s2310 — per-slot retail polarity and dual-512 phase control.** The
  initial capture passed whole-RDRAM, title/hangar, ring-wide, all sixteen
  slot watches, port title/hangar, and 45-second retention, but its single
  `0x006AB400:512` writer bucket had no entries. The fixed rerun added
  `0x006AB800:512` in the same recipe. Both phase buckets were active
  (`1535` and `2720` VI callbacks), and the lifetime positive control
  attributed all sixteen `768`-byte slot watches (`768` writes each) to
  retail PC `0x800078EC`; neither 512 bucket contained a writer entry.
  The corrected run's current port pair was `0x166750`/`0x166A50`, with
  stage events `9740/9742`, FNV/nz `60F910DE/621` and
  `7B70923A/639`, respectively. Both were stage-only in the port join;
  later zero rows were events `9882/9884`, writer kind image-DMA, PC `0`,
  callsite `0x8008EE84`. Retail final snapshots for those exact slots were
  nonzero (`750/768`), FNV `E5CF803C`, and `753/768`, FNV
  `E611A9A8`. This selects `H-SlotRoleTimeSkew` for target-phase
  polarity, rules out a target-phase retail zero conclusion, and does not
  prove target-phase retail nonzero publication because its phase writer arm
  was a valid zero. No contract change or mitigation is authorized.

- **s2309 — retail whole-ring polarity.** The required oracle preflight and
  same-run capture passed the whole-RDRAM positive control, title/hangar VI
  origins, ring watch, an active phase bucket, the lifetime ring writer, and
  the final ring snapshot; the
  port reached title/hangar and retained 45 seconds. The port's current
  phase-10 pair was `0x168850` (`60F910DE`, `nz=621`) and `0x168B50`
  (`7B70923A`, `nz=639`). The first had exact source/consumer events
  `10804/10805`, then same-destination zero rows beginning at event `10881`;
  the last writer was image-DMA (`writer_pc=0`, callsite `0x8008EE84`). The
  second was stage-only. Retail wrote all `12288` bytes in
  `0x166450..0x169450` through `0x800078EC`; its final ring snapshot had
  `12288` bytes and `12026` nonzero. A `0x300` target slot leaves at most
  `11520` nonzero bytes outside itself, so at least `506` bytes of the exact
  `0x168850` slot were nonzero. This selects aggregate `H-PortOnlyZeroFill`
  and
  refutes slot rotation for the observed pair. The result does not prove
  game intent and authorizes no writeback or mitigation.

- **s2308 — dynamic-slot writer provenance.** The initial driver capture was
  postprocessing-invalid because it stopped the oracle before its shutdown
  summaries and used non-portable AWK hex bounds. The corrected same-run
  capture passed the retail whole-RDRAM control (`10,000`), title/hangar
  origins, both target-range write summaries (`768` each), and a phase writer
  histogram; the port reached title/hangar and retained 45 seconds. The
  complete ring table found that the nonzero phase-10 pair had rotated to
  `0x167C50` (`2B9E9631`, `nz=621`) and `0x167F50` (`6ADD4218`, `nz=639`).
  Stage events `9386/9388` were followed by exact source/consumer events
  `9467/9468` and `9469/9470`, respectively. Subsequent rows at those same
  destinations were `F59C39C5`/`nz=0`; their writer snapshots were
  `writer_kind=image-dma`, `writer_pc=0`, callsite `0x8008EE84`, with the
  image-DMA write sequence advancing after the exact pair. This is a
  single-source port result that rules out an image-publication gap and a
  ring-role mismatch for the observed pair; it established the port-side
  image-DMA zero-fill behavior but not its retail polarity or game intent.
  The independent oracle confirms active retail writes in the watched PCM
  ring and target phase, but its fixed two-slot controls did not cover the
  dynamically selected `0x167F50` pair; s2309 supplied the missing whole-ring
  evidence.

- **s2307 — cross-phase payload tuple mismatch.** The fixed same-run capture
  passed retail whole-RDRAM `10,000`, title/hangar, and all three target
  writer-PC controls, and the port reached title/hangar with 45-second
  retention. Its two nonzero phase-10 stage rows were
  `0x167650`/`0x300`/`2B9E9631`/`nz=621` and
  `0x167950`/`0x300`/`6ADD4218`/`nz=639`. The cross-phase table retained
  `1,251` width-512/`0x006AB400` PCM rows and found zero exact source or
  consumer matches for either stage row. An independent raw-log recount found
  `38` same-destination PCM rows for `0x167650` and `40` for `0x167950`, all
  `F59C39C5`/`nz=0`; the postprocessor summary independently reported
  `19/19` and `20/20` source/consumer mismatches. This selects
  `H-PayloadTupleMismatch` for the observed rows, rules out
  `H-CrossPhaseExact` at this scope, and does not authorize a contract change.

- **s2306 — recurrence and destination payload summary.** The fixed same-run
  capture passed retail whole-RDRAM `10,000`, title/hangar, and all three
  target writer-PC controls; the port reached title/hangar and retained 45
  seconds after hangar. Its two nonzero phase-10 rows both matched exact DMA:
  `0x168550`/`0x300`/`60F910DE`/`nz=621` remained without exact source or
  consumer in the retained phase, while `0x168850`/`0x300`/`7B70923A`/`nz=639`
  matched both at ordinal `+12` with valid ordering. The per-destination table
  reported `stage-only` for the first and exact source/consumer for the
  second, plus one same-destination zero-payload mismatch flag for each
  endpoint on the second. This selects `H-StageUnconsumed` at the observed
  phase scope and leaves cross-phase attribution open.

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

1. **M5 Step 3h companion 640-origin retail writer census.** Ask ground truth
   first, retain the completed title, four 512, and two earlier 640 buckets,
   then add the companion origins `0x0066AA00:640` and `0x00696600:640` in the
   same oracle invocation. Require whole-RDRAM, title/hangar, all sixteen
   lifetime writer controls, positive callback counts for both new buckets,
   and nonzero final snapshots. Join every bucket to the actual current port
   stage pair. A positive writer-PC matrix at either companion origin selects
   it; both positive selects shared/alternating publication; both empty leaves
   writer attribution open. No writeback, consumer, writer, slot, gate,
   guard, address-remap, or default change.
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

The image arm changes DMEM, completes, and emits generated DMA. Qualified
phase-gated captures show a rotating mixed output contract: s2306 had one
stage-only row and one source/consumer join at ordinal `+12`, s2307 found two
fixed-address zero-payload mismatches, s2308 found a nonzero pair with exact
source/consumer publication followed by later same-destination image-DMA
zero rows, and s2309 found a retail polarity mismatch for the observed
physical pair. The image-stage and port-side zero writers are known;
`H-PortOnlyZeroFill` is selected at that capture scope, while game-level
legitimacy and the stage-only row remain open. The silent arm's PCM boundary
is separately qualified but all-zero. Retail writes corresponding field
spans and a different task/output span. This is a measured contract
boundary, not permission to add a copyToRAM/CIMG writeback, writer guard,
slot guard, consumer change, or address remap.

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
- s2307's fixed `0x167650`/`0x167950` addresses as stable target slots;
  s2308's complete ring table observed the nonzero pair at
  `0x167C50`/`0x167F50` instead.
- s2308's port-only zero-fill observation as evidence of retail-normal
  polarity; s2309's independent whole-ring snapshot shows nonzero data in
  the observed physical slot at the same capture scope.
- s2309's claim that its phase writer histogram proved retail target-phase
  polarity. Its log had active phase VI coverage but no
  `writer-pc-phase ... pc=` rows; only the lifetime ring writer was
  positive. s2310's corrected dual-512 run reproduced that distinction. The
  s2309 aggregate whole-ring/final-snapshot evidence remains valid, but it
  cannot establish target-phase publication.
- s2311's `H-RetailOtherPhase` selection was a candidate-gap result based on
  two unmeasured post-title origins. s2312 measured both with positive VI
  controls and no phase writer rows, so that selection is superseded by
  `H-Retail-Earlier-Or-Unattributed`; the earlier 640-origin gap remains open.

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
