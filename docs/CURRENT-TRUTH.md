# Rogue Squadron 64 Recomp — current truth

Operational front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history through s2403 is summarized in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md);
the append-only ledger remains authoritative for exact commands and probe rows.

Current maintenance marker: Session 2459 (2026-08-26).

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The old boot/menu-overlay explanation is closed.
- Qualified route: `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_SPIN_YIELD=1`,
  `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. Spin yield is gated and
  default-off.
- Product multi-header freelist restore is on. Garbage-CIMG and wrap-drop
  mitigations are off. Any future mitigation needs a named writer, a legitimacy
  judgment, and an `ORIGIN:` line.
- M5 defaults to the Factor 5 image arm. `ROGUESQ_AUDIO_UCODE=0` selects the
  silent `M_AUDTASK` `Broke` stub. The image arm performs DMEM work, returns
  `Broke`, emits generated DMA, and can publish PCM. Stock `aspMain` is not this
  game's contract; MORT is a separate CPU speech asset. The design gate is
  [`M5-AUDIO-PLAN.md`](M5-AUDIO-PLAN.md).
- The retail oracle is the independent witness for game-side memory claims. Its
  whole-RDRAM, phase, task/status, and named-PC controls must pass before a
  retail null is interpreted. It reaches attract, title, and hangar, not a
  mission.
- The current M5 question is whether the port's generated audio-overlay
  alternate is the legitimate counterpart of retail's second-range consumer.
  The image arm reaches task completion and generated DMA, but no legitimate
  downstream slot/voice/output contract has been established.

- **s2454 — no port runtime dispatcher body replaces retail `0x8002BEEC`.**
  The source candidate table finds `get_function`/`rs64_m5_dispatch_boundary`
  is only a lookup observer, while `rs_memset` is reached through 88 direct
  generated calls. The complete audio-overlay candidate at `0x8008F2CC`
  (`allocateSongChannelArray` -> `rs_memset` -> `after_6`) is the only
  statically grounded second-range-capable alternate. This selects
  `H-PortGeneratedAlternate` at source scope and rules out a generated/runtime
  `__osDispatchThread` replacement; live provenance remains open.

- **s2455 — the matched port provenance capture is blocked before the target
  phase.** Retail controls passed, including hangar origin `0x006AB400` and
  target-PC rows. The rebuilt qualified port arm reproduced an abort at 4.3s
  in `get_function(0)` from `convertMat3x4ToN64Mtx` (last guest PC
  `0x80001F88`), with no phase-gated M5 witness rows. This is a non-result for
  `H-PortF2CC/H-PortOtherStatic/H-PortDynamic`, not evidence for any one arm.
  The immediate blocker is the pre-phase null-dispatch boundary.

- **s2456 — the reported pre-phase PC is not a lookup callsite.** The external
  generated census contains 28,385 `LOOKUP_FUNC` expansions, but none in
  `convertMat3x4ToN64Mtx`; `0x80001F88` is only the return delay-slot `nop` of
  `buildHeapFreeList`. The retail oracle passed `[gpr-ctl]` and the whole-RDRAM
  control but observed zero executions of `0x80001F88` in 3,557 VI, with no
  hangar phase rows. This is a non-result for the original missing-target,
  legitimate-zero, and bad-data hypotheses; the resolver needs a native
  caller capture before the stale guest-PC breadcrumb can be interpreted.

- **s2457 — the first null is reached from generated menu code, but the guest
  breadcrumb is stale.** A first-hit resolver capture recorded requested
  `0x00000000`, guest `0x80001F88`, and a native backtrace through
  `convertMat3x4ToN64Mtx` → `traverseSceneGraphRecursive` →
  `setupCameraMatrices` → `runMenuModelViewerScreen`. The same rerun's
  indirect positive control resolved `0x8009123C` before the abort. This
  selects `H-ResolverGeneratedCaller` for the native boundary and
  `H-StaleGuestBreadcrumb` for the reported guest PC; it does not identify
  the zero-producing generated callsite or authorize a missing-function stub.

- **s2458 — the port image arm reaches a generated alternate, but not the
  retail-grounded second-range relation.** Retail controls passed: whole-RDRAM
  writes 12,661, exact image-range writes 1,536/1,125, and 594 hangar-phase
  `0x8002BEEC` → `0x800078EC` predecessor rows; `0x8008F2CC` executed 6 times.
  In the paired qualified port run, the image arm reached title and hangar,
  produced 8,351 image-stage rows and 4,149 completed joins, all
  `stage-only`, and no PCM or consumer-only rows. Its phase-scoped static
  `rs_memset` table retained 1,024 rows; the first hangar row was callsite
  `0x8008F2CC`, `dst=0x801797B0`, `len=0x298`, with active Factor 5 identity,
  followed mainly by `0x800052C4`. This selects
  `H-PortGeneratedAlternate` at static-callsite scope and rules out an
  observed port second-range consumer join. The stub arm crashed before the
  target phase, so its null target-phase rows are a non-result. This is
  single-source port-boundary evidence paired with independent retail ground
  truth; no output remap, task-data change, gate, or guard is authorized.

- **s2459 — generated-alternate equivalence remains a qualified non-result at
  the port boundary.** The corrected retail oracle passed whole-RDRAM (12,661),
  exact ranges (1,536/1,125), 627 hangar-phase `0x8002BEEC` -> `0x800078EC`
  predecessor rows, and six `0x8008F2CC` executions. The paired port image arm
  crashed before target capture in `matchKeywordWithPriority`
  (`last-guest-pc=0x8000834C`); a fixed image-only attempt with
  `ROGUESQ_DRAIN_INLOOP_TICK=1` also crashed in `slotDispatcherIter`
  (`last-guest-pc=0x80007904`). The passed controls qualify the missing port
  tuples as a non-result, but do not select equivalent versus bootstrap-only.
  The initial oracle command without Rice/hold controls is setup-only and
  excluded. Artifact: `scratch/agent/s2459_m5_generated_alternate_equivalence/audit.md`.

## Latest evidence

- **s2452 — the retail second-range boundary has no generated dispatcher body.**
  Static inspection places `0x8002BEEC` inside retail `__osDispatchThread`
  (`0x8002BD74..0x8002BEEF`), immediately before `__osCleanupThread`; the
  generated tree contains no body or label for that runtime dispatcher. The
  known generated alternate at `funcs_23.c:0x8008F2CC` directly calls
  `rs_memset`, continues at `after_6`, and performs writeback-cache setup. The
  88-site direct-call census contains no literal `0x8002BEEC` caller. This
  selects `H-DifferentGeneratedBoundary`, rules out a malformed direct call at
  that literal boundary, and leaves the port-side runtime replacement open.
  Artifact: `scratch/agent/s2452_m5_caller_lowering/audit.md`.
- **s2451 — `rs_memset` does not consume guest `$ra` in either body.** The
  generated and retail bodies have no `$ra` reads/writes or return-dependent
  branch beyond terminal `jr $ra`. This rules out a body-level return/link
  explanation for the missing second-range consumer; the caller/data-path
  divergence remains open.
  Artifact: `scratch/agent/s2451_rs_memset_ra_audit.txt`.
- **s2450 — direct and indirect calls share the generator's no-link contract.**
  The recompiler emits a plain `(rdram, ctx)` invocation for named, reference,
  runtime-lookup, register-lookup, and generated `jal` calls; `needs_link_branch`
  only emits an `after_N` continuation. This selects
  `H-GeneratorIntentionalNoRA` at the source/output contract scope, but does
  not establish whether that contract is semantically valid for `rs_memset`.
  Artifact: `scratch/agent/s2450_direct_jal_audit/`.
- **s2449 — no generated static `rs_memset` callsite writes `ctx->r31`.** All
  expected 88 `jal 0x800078E0` sites were audited with their preceding and
  delay-slot instructions; none writes `r31`. Together with s2448 this selects
  `H-GeneratedDirectCallOmitsRA` and rules out an observed caller overwrite.
  Artifact: `scratch/agent/s2449_static_audit.tsv`.
- **s2448 — every observed static caller already has zero guest `ra`.** A
  fixed paired capture passed retail and port route controls; both arms retained
  1,024 caller rows and every row had `ra=0`. The indirect positive control
  resolved in both arms. This selects `H-CallsiteAlreadyZero` at the live caller
  boundary, without identifying the lowering cause.
  Artifact: `scratch/agent/s2448_m5_static_rsmemset_callsite_abi_fixed/`.
- **s2447 — the generated `rs_memset` entry loses every static caller return
  address.** The corrected phase-scoped rerun passed independent retail and
  port controls; 88 static sites were enumerated and all retained title/hangar
  rows had `ra=0`, including second-range destinations. The indirect positive
  control resolved. This selects `H-StaticCallerContextLost`, without locating
  whether the omission is at the callsite or wrapper.
  Artifact: `scratch/agent/s2447_m5_static_rsmemset_callsites_fixed/`.
- **s2446/s2445 — the port reaches the second-range helper through a stable
  static path.** The live indirect target control resolved, but
  `get_function(0x800078E0)` was not observed; `0x800078EC` is a loop block
  inside `rs_memset`, not an independent target. Port rows at the helper had
  zero saved `ra`, so `H-PortStaticRsMemsetPath` supersedes the earlier
  `H-PortAlternatePath` label. The semantic caller and lowering boundary remain
  unresolved.
- **s2442 — retail grounds the semantic caller.** With independent controls,
  the exact second-range store rows at `0x800078EC` joined
  `PREVIOUS_PC=0x8002BEEC` 632 times; the generated `0x8008F2CC` callsite ran
  six times. Stable store context included `ra=0x8008F2D4` and
  `a0=0x801797B0`. This is retail-only evidence and authorizes no port change.
- **s2430/s2431/s2434 — retail range activity is real.** The first exact range
  is written by `0x800078EC`; the second has `0x80007670` and helper PCs. All
  selected PCs execute in hangar, and exact-store rows at the helper advance
  through the range with varied pre-store words. The semantic helper/caller
  relation was closed by s2442, but the port consumer is still open.
- **s2420–s2428 — M5 route and title controls are valid.** Stub and image arms
  reach title and hangar under the qualified route. The image arm changes DMEM,
  emits generated DMA, reaches `break_pc=0x1328`, and completes SP service; the
  stub does not. The title `0x80015BC8` writer joins the port title task row,
  while no bounded hangar slot/voice/descriptor/filter consumer joins the image
  identity. No output remap, task-data change, gate change, or guard is
  authorized.
- **s2408–s2419 — downstream identity and handoff remain unresolved.** The
  sequence key is reproducible for stage-to-key-on ordering, but later PCM rows
  have a different phase/origin. Retail provides stable phase-specific task/data
  handoff pointers; port emits additional task/data rows and differs at that
  boundary. These are observation-scope results, not permission to remap output.

## Active backlog

Closed investigations are not active work items. This is one monotonic sequence;
#1 is the next campaign priority.

1. **M5 generated alternate equivalence — active.** Compare the port
   `0x8008F2CC` alternate's phase/task arguments and destination against the
   independently grounded retail callsite, then determine whether it is an
   equivalent consumer or bootstrap-only path.
   The current port boundary is pre-target dispatch
   (`matchKeywordWithPriority` / `slotDispatcherIter`); audit the complete
   bounded call/return idiom there before another equivalence capture. No
   output remap, task-data change, gate change, or guard is authorized.
2. **M5 task/output closure — closed at current capture scope.** The earlier
   task-gap label was a join artifact.
3. **M5 gate polarity/writer join — closed at current capture scope.**
4. **M5 payload-transformation provenance — closed at current capture scope.**
5. **M5 A1 retail flag semantics and pre-target route boundary — closed at
   current capture scope.**
6. **M3 crash work — parked.** Resume only as a systematic idiom-class audit
   with a named discriminator.
7. **Hangar visual artifact — parked.** H2 and consumer-mode H1 are refuted;
   H3 is unavailable because the oracle cannot screenshot the LLE path.
8. **Generated-symbol renaming — parked.** Resume only after M5 closes or M3
   obtains a new discriminator; do not invent names for unresolved placeholders.

## Durable boundaries

### Route, rendering, and Factor 5

The accepted route is `LLE_UNGATED=1, LLE_SOLO=1`; it reaches title and hangar,
while other arms do not reliably reach both. Menu spin yield is a diagnostic
route aid, not a default behavior change. Factor 5 mappings and independent
controls are in [`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md) and
[`tools/oracle/README.md`](../tools/oracle/README.md).

### M5 audio and image output

Direct service entry/exit, service gate/loop, task/AI boundary, image DMEM work,
generated DMA, and reporter association are live on the port. The image arm's
downstream identity is not yet a legitimate slot, voice, PCM, or output mapping.
Retail proves related ranges and task-field writers are active, including the
second-range helper/caller relation, but does not prove a port equivalent.
Zero-valued rows are diagnostically ambiguous; no output remap or mitigation is
permitted without a named legitimate writer and an `ORIGIN:` line.

### VI, M3, M4, and generated symbols

Retail/port VI selector and current-line publication remain unresolved outside
the qualified route. M3 is parked pending a complete idiom audit. M4
accumulator-origin work is parked. Generated-symbol renaming remains parked at
the useful boundary.

## Superseded conclusions

These were believable before qualified routes or independent controls, but are
superseded at their measured scopes:

- The old overlay/menu explanation, intrinsic 640 flakiness, missing input or
  wait-return claims, and unqualified PCM-null claims.
- Clean-stub, canary-poison, final-E50, uniform-gate, host-isolator, and
  global-zero image-DMA explanations.
- The s2190–s2197 and s2283/s2284 second-origin/A1 matrices, the s2228 and
  s2242–s2259 image/pair crash splits, and s2288's stub-first route conclusion.
- s2304's route-wide PCM gap, s2307's fixed addresses, s2308's zero-fill
  interpretation, s2325's destination-role split, and s2335–s2342's
  inactive-parent/gate labels.
- s2346's output-metadata-writer-absent label and the successive s2347–s2360
  candidate, overflow, value, task-field, and source/payload labels where later
  controls superseded them.
- s2376's input-dependent A1 label, s2379's unresolved flag split, s2383's
  missing-completion label, and s2399's identity-cleared label.
- s2445's `H-PortAlternatePath` label and s2446's original assumption that
  `0x800078EC` was a callable function target; corrected boundary inspection
  and the live indirect positive control superseded them.

## Evidence and safety rules

- Ask the retail oracle for ground truth before adding an instrument; arm its
  whole-RDRAM positive control first.
- A null requires a same-run positive control. Batch counters and A/B arms in
  one build/run, scope budgets to the phase, and use VI gates rather than time.
- Regenerate in order: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then
  CMake. Diagnostics in generated output belong in fixup scripts.
- Kill runs with SIGKILL, never SIGTERM. Run from `build/` with the ROM present.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. If `lib/` changes, export submodule patches in the same
  iteration.
- A mitigation is not an explanation: name the writer, state legitimacy, and
  add an `ORIGIN:` line before landing a skip, allow, guard, or restore.
- Never add a diagnostic field without a complete discriminating table and an
  outcome that can select among hypotheses.
