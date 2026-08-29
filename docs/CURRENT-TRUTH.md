# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
background and archived lineages are in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md);
exact run recipes and evidence remain in the append-only ledger and scratch
artifacts. This file is intentionally compact and is the required pre-work
read.

Current maintenance marker: Session 3135 (2026-08-28).

## Current state

The native port builds and boots. With the validated spin-yield route and
Factor 5 LLE-only path it reaches attribution, the N64 logo, intro cinematic,
star flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar VI 512
(`0x006AB400`). Hangar visuals still have geometry/color artifacts. Yield is
default-off. Audio is not production-complete: the Factor 5 image task is the
qualified audio arm, while the `musyx_stub`/Broke path is the silent control.

Recent M5 route captures stop at pre-title VI 640 (`0x0066A500`), although
independent retail runs pass a whole-RDRAM positive control and reach title and
hangar. Therefore target-phase audio/task/DMA/service/slot/voice/MORT/PCM
nulls from those port captures are unevaluable. No audio gate, wait, voice
guard, output destination, or VI behavior may be changed without a named
legitimate writer and an ordering edge.

The regeneration-safe generated-symbol sweep is closed: the only remaining
project placeholders are the deliberately preserved ambiguous fragments
`fake_func_800AE3E4` and `fake_func_800B75C4`, both already audited. The next
active engineering prerequisite is a new retail-grounded M5 boundary.

## Latest evidence

Session 3116's independent retail-oracle boundary capture passed the
whole-RDRAM positive control and reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`. The post-init execution range
`0x8001B7B8:0x8001BB6C` fired throughout the run, including target phases,
but did not provide direct VI-mode-write attribution. This refutes the range
as the missing 640-to-1024 writer while proving it is live. Combined with
Session 3115, the writer remains outside both watched ranges or in a later
handoff. This is single-source oracle evidence; it does not authorize a port
change.

Session 3112 synchronized the mechanically classifiable generated records
`0x800B2628`, `0x800B42BC`, and `0x800B89F4` as `data_gap_*` where appropriate,
and synchronized the stale generated `0x800B42BC` name. No runtime behavior
changed. Session 3110/3111 retail boundary watches passed the positive control
and reached title/hangar, but the `selectAndApplyViMode` plus descriptor-helper
range never executed during the 640→1024 transition. The missing writer is
outside the already watched direct `osViSetMode` callsites and helper range.
These are single-source oracle qualifications; they select an unenumerated
writer but do not identify it.

Session 3117's static audit identified guest PC `0x800C2984` in
`runMenuModelViewerScreen` as a new request-stage handoff: it calls
`requestViFeatureChange(0x11)`, whose first store is the pending word at
`0x80128E90`. This is outside the closed direct `osViSetMode` callsites and
selector range. It is a candidate boundary only; no runtime behavior changed
and retail attribution is still required.

Session 3118's independent retail-oracle capture passed the whole-RDRAM
positive control (10,000 visible writes and 10,000 additional counted writes),
reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, and executed
`0x800C2984` exactly once at 3.3s during the already-live 640 phase
(`0x0066A500`). It did not execute at the 640-to-1024 transition or in title
or hangar. This rejects the candidate as the target-phase publication
boundary; it is a pre-title request-stage event whose relationship to the
missing writer remains unresolved. This is single-source oracle evidence.

Session 3119's complete static audit of the five remaining
`requestViFeatureChange` callers classified them as mission/cutscene or menu
maintenance, cinematic/player-record teardown, and post-transition hangar
work. None is a target-phase 640-to-1024 publication handoff; the hangar call
is explicitly after `beginSceneRenderFrame`. This selects
`H-AlreadyEnumerated` for this caller family and moves the next retail probe to
the unenumerated handoff between the pending request-mask store and VI
descriptor publication. This is static evidence only and does not identify
the writer. Evidence: `scratch/agent/s3119_m5_vi_request_callers.md`.

Session 3120 corrected the M5 task-contract arm identity in the runtime:
`run_task` now treats an unset `ROGUESQ_AUDIO_UCODE` as the default real
`factor5_ucode_b` image, matching `get_rsp_microcode`; only an explicit `0`
selects `musyx_stub`. The target builds successfully. No game soak was run in
this environment, so downstream phase rows remain unevaluable.

Session 3121's independent retail oracle passed the whole-RDRAM positive
control (18,055 writes), reached title `1024 @ 0x00790400` and hangar `512 @
0x006AB400`, and watched the pending VI range, all four game VI records, the
final record, and selector bytes in one run. No title-phase write occurred to
the selector or record ranges. The pending range's title rows were only the
known per-frame `0x8001BA80/0x8001BA88` writers; request/clear edges were live
in the 640 and hangar controls. This selects a deferred/outside-consumer
publication boundary for the next retail probe. It is single-source oracle
evidence and does not identify the writer or authorize a port change.

Session 3122's independent retail oracle passed the whole-RDRAM positive
control (10,000 callbacks), reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`, and watched the untested libultra consumer range
`0x80034F38:0x800356AC`. At the 640-to-1024 transition it executed
`viMgrMain` and entered `__osViSwapContext` (`0x80035550`) with the new
`0x00790000` context immediately before the VI trace reported `0x00790400`.
The consumer range was live (1,675,531 executions; 4,604 context swaps).
This selects `H-ConsumerHandoff` and rejects the candidate-set form of
`H-OutsideConsumer`; `__osViNext`'s optional join was empty and is
unevaluable. The result is single-source retail evidence: it authorizes a
port-side parity probe but no behavior change.

Session 3123 built the existing port-side VI consumer probe and ran the
validated spin-yield/F5-LLE image arm for 120 seconds. Its all-width positive
control fired 8 rows, and the consumer committed width 640 continuously, but
the port never reached target width 1024 or hangar width 512. The capture
therefore selects `H-PortConsumerAbsent` only at the route's observed target
phase: no target-phase consumer row exists because the port stopped at 640.
It does not distinguish a missing consumer from an upstream route stop. This
is single-source port evidence; no behavior change is authorized.
Evidence: `scratch/agent/s3123_vi_consumer_capture/run.log`.

Session 3124 ran the paired, phase-keyed M5 route qualification with the
corrected image arm and silent control in one build/window. Both arms passed
the same-run positive controls (nine VI-context control rows and the host
voice-audit control), each dispatched 2,944 audio tasks, and each reached VI
640 but neither reached title 1024 or hangar 512. Image rows identified
`factor5_ucode_b`; silent rows identified `musyx_stub`. This selects
`H-BothPreTarget`: target-phase audio/task/DMA/service/slot/voice/MORT/PCM
nulls remain unevaluable and no audio behavior change is authorized. This is
single-source port evidence; it does not identify the upstream route blocker.
Evidence: `scratch/agent/s3124_m5_route_qualification/summary.txt`.

Session 3125's independent retail oracle passed the whole-RDRAM positive
control (10,000 callbacks), reached title `1024 @ 0x00790400` at 17.3s and
hangar `512 @ 0x006AB400` at 38.4s, and the fixed phase-gated run recorded
post-consumer execution rows in both target buckets (including
`0x800356F4` at title and `0x800358E8` at hangar). The range also reported
3,724,111 hits overall. This rejects a retail-side stop immediately after
`__osViSwapContext` but does not identify the port's pre-target divergence.
This is single-source retail evidence and authorizes an exact phase-gated port
parity probe, not a behavior change.
Evidence: `scratch/agent/s3125_m5_retail_post_consumer/oracle_phase.log`.

The strongest route boundary remains the independent comparison: retail
reaches title at 1024 and hangar at 512, while the recent same-build port
capture issues only widths 320, 2, 640, and 640 and remains at VI 640. The
port's audio-arm dispatch controls are positive in earlier qualified runs,
so a zero target-phase audio row is not evidence of absent dispatch.

Session 3126's phase-gated port parity probe passed both same-run controls:
the VI-context control fired 8 rows and the host voice-audit control fired
once. The port still issued only the pre-title 640 origin and produced zero
rows from the retail-live `0x800356AC:0x80035B00` range; it reached neither
title nor hangar, with no crash or abort. This selects `H-PortConsumerAbsent`
at the observed route, while leaving the upstream pre-640 divergence
unidentified. The range watch is sampled at the existing VI-commit accessor,
so it is not evidence that the full range was executed when the breadcrumb
was stale. This is single-source port evidence; no behavior change is
authorized. Evidence: `scratch/agent/s3126_m5_post_consumer_port/run.log`.

Session 3127's independent retail oracle passed the whole-RDRAM positive
control (10,000 writes), reached title `1024 @ 0x00790400` and hangar `512 @
0x006AB400`, and watched exact guest PC `0x800356A8`, the final instruction
before the previously qualified `0x800356AC:0x80035B00` continuation. The
candidate executed zero times overall, including both target phases. This
rejects it as the immediate pre-consumer handoff and selects
`H-RetailBoundaryAbsent`; the port divergence remains unexplained. This is
single-source retail evidence and does not authorize a port change.
Evidence: `scratch/agent/s3127_m5_retail_preconsumer/oracle.log`.

Session 3128's independent retail oracle passed the whole-RDRAM positive
control (10,000 visible writes), reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`, and watched the distinct origin-publication instruction
`0x80035788` inside `__osViSwapContext`. The instruction is the store to
`VI_ORIGIN_REG`; the previously watched `0x80035798` is the subsequent width
store. The candidate executed 2,569 times overall and fired in both target
phases, with title `v0=0x00790000` and hangar `v0=0x006AB000`. This selects
`H-NewStaticHandoff` and authorizes a port-side parity probe at the origin
publication edge. It is single-source retail evidence and does not authorize
an audio or route behavior change. Evidence:
`scratch/agent/s3128_m5_retail_origin_publish/AUDIT.md`.

Session 3129's port-side parity probe instrumented the host equivalent of the
retail `0x80035788` origin publication: `update_vi` immediately before its
`VI_ORIGIN_REG` store. The same run emitted eight bounded origin-publication
control rows, eight VI-context control rows, and one host voice-audit control.
It reached only pre-title VI 640 (`0x0066A500`), emitted zero target
publication rows, and reached neither title nor hangar; no crash or abort was
observed. This selects `H-PortPublicationAbsent` for the observed route and
places the divergence upstream of the VI consumer/publication edge. It does
not identify the upstream writer, and no audio or route behavior changed.
This is single-source port evidence. Evidence:
`scratch/agent/s3129_m5_origin_publish/run.log`.

Session 3130's independent retail oracle passed the whole-RDRAM positive
control (10,000 writes), reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`, and watched the newly audited direct `osViSetMode`
callsite `0x8001BC28` in `selectAndApplyViMode`. The candidate executed zero
times overall, including both target phases. This rejects that selected-mode
callsite as the retail target-phase handoff and leaves the upstream boundary
unidentified. This is single-source oracle evidence; no port behavior changed.

Session 3131's independent retail oracle passed the whole-RDRAM positive
control (10,000 callbacks), reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`, and watched the upstream callsite `0x800186C0` (the
`jal 0x8001BB6C` into `selectAndApplyViMode`). The candidate executed zero
times overall, including both target phases. This rejects that caller as the
retail target-phase handoff and leaves the upstream boundary unidentified.
This is single-source oracle evidence; no port behavior changed. Evidence:
`scratch/agent/s3131_m5_retail_186c0/oracle.log`.
Evidence: `scratch/agent/s3130_m5_retail_bc28/AUDIT.md`.

Session 3132's bounded caller/data-flow census found no hidden caller of
`freeRenderSubsystemResources` in the available generated snapshot, companion
tree, project symbols, or registration artifacts. The wrapper's only
represented call edge is `0x800186C0 → selectAndApplyViMode`; its complete body
only frees five resources, selects/copies a mode descriptor, calls
`osViSetMode`, and waits on the video queue. This selects H-AlreadyEnumerated
and supplies no new retail PC. It rules out another caller in this wrapper
chain but does not identify the upstream 640-to-1024 handoff. Static,
single-source evidence; no build, run, or behavior change.
Evidence: `scratch/agent/s3132_m5_vi_caller_audit.md`.

Session 3133's available-text census of the pending word,
selector/descriptor candidates, named VI helpers, and consumer/publication
symbols found no game-side writer/reader body or new transition-capable
instruction. The companion libultra bodies are `INCLUDE_ASM` stubs and the
matching generated-function snapshot is absent from the workspace. This
selects `H-StaticInsufficient`, rules out a static PC selection for this unit,
and leaves the M5 route blocker unresolved. Single-source static evidence; no
runtime behavior changed. Evidence:
`scratch/agent/s3133_m5_pending_descriptor_audit.md`.

Session 3134 repeated the prescribed companion-tree and project-tree census
for the pending VI word, selector/descriptor candidates, named VI helpers,
and the known consumer/publication PCs. It found only existing declarations
and probes: no restored generated body or disassembly, and no new
transition-capable retail PC outside the closed candidate sets. This selects
`H-StaticInsufficient` again and leaves the M5 route blocker unresolved.
This is single-source static evidence; it authorizes no port probe or
behavior change. Evidence:
`scratch/agent/s3134_m5_upstream_source_census.md`.

Session 3135 reran the exact bounded census across the companion and project
trees. Matches remained limited to existing declarations, symbol entries,
and existing probes/references; no restored generated body, disassembly, new
transition-capable retail PC, or new pending-to-descriptor edge appeared.
This selects `H-StaticInsufficient` again and leaves the M5 route blocker
unresolved. Static, single-source evidence; no build, run, port probe, or
behavior change. Evidence:
`scratch/agent/s3135_m5_upstream_source_census.md`.

## Next steps

Priority is maintenance, then M5 de-stubbing, then systematic M3, then the
generated-symbol sweep. Maintenance is complete and M5 design is complete;
the port-side VI publication parity probe is now exhausted for this route.
M3 is parked pending a new discriminator.

1. **M5 route blocker — obtain a retail-grounded upstream handoff.** The
   pending-request/descriptor static audit is insufficient because the
   generated snapshot is absent and the companion bodies are `INCLUDE_ASM`
   stubs. Do not invent a PC or add a port probe. Restore/provide an equivalent
   generated body/disassembly, or choose a genuinely new retail watch based on
   independent static evidence, then require whole-RDRAM and title/hangar
   controls. Do not change audio or route behavior.

2. **M5 route reachability — requalify target-phase audio/task rows after a
   route change.** Repeat the paired phase-keyed qualification only after the
   upstream boundary produces a new route arm or target-phase control.

3. **M5 audio de-stubbing — qualify Step 1, then implement one named edge.**
   Resume only when a port run reaches target phases. Use the phase-keyed
   task/DMA/return/service/slot/voice/MORT/PCM table with image and silent
   arms in one build/run. A qualification result alone does not authorize a
   gate, wait, voice, destination, or output change.

4. **M3 crash work — systematic idiom-class audits only.** A new unit must
   enumerate the entire idiom class, name its discriminator, and guard or
   prove every site. Passive crash recurrence belongs in the soak queue.

6. **External retail-entry boundary.** Parked after the candidate set was
   rejected; revisit only with a different static handoff and independent PC
   attribution.

7. **M4 accumulator origin.** Parked because the latest route qualification
   had no target-phase positive-control rows. Do not interpret its nulls.

8. **M5 SP-yield lifecycle and CPU-side MORT publication.** Parked pending a
   route angle that reaches target phases. The corrected MORT descriptor edge
   is `+0x190` to `dmaVoiceSampleAndSignal`; `+0x194` is the speech source.

## Durable boundaries and operating rules

Factor 5 uses [`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. Interpreter
limits, null-GBI guards, and similar defenses are safety mechanisms, not
explanations. Overlay dispatch is fixed enough for the validated route.

Ask the independent retail oracle for ground truth before adding port
instrumentation. Every instrument needs a positive control in the same run,
phase-scoped budgets, and two independent lines of evidence before a
conclusion is promoted. Phase-gate animated comparisons on VI transitions;
never use a stopwatch. Build every A/B arm together.

Regeneration order is `make_elf.py` → N64Recomp → `fixup_game_funcs.py` →
CMake. Never hand-edit generated functions for behavior changes. If `lib/`
changes, export submodule patches in the same iteration. Never run
`git submodule update`, `git checkout -- lib/...`, `git clean`, or
`git reset --hard`. Kill runs with SIGKILL and run from `build/`.

A mitigation-shaped change requires an `ORIGIN:` line naming the writer and
stating whether the value is legitimate. A null result without a positive
control is worthless. If three consecutive iterations on one hypothesis fail
to produce a discriminator, pivot or block with a specific question.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed. The full
failed experiments remain in `PORTING-STATE.md` and the archived overview.

Static boundary-only symbol classifications remain non-renames when companion
symbols, source/m2c, callers, and local semantics do not provide a defensible
name. Stable companion duplicate-prefix and preamble mappings belong in
`tools/rename/build_redefs.py`.

## Evidence index

Recent evidence directories include:

- `scratch/agent/s3111_m5_retail_mode_selector_range/`
- `scratch/agent/s3107_m5_retail_mode_callsites/`
- `scratch/agent/s3106_m5_retail_mode_writer/`
- `scratch/agent/s3112_generated_symbol_rename/`

Use `grep -n` plus a bounded `sed` window for `PORTING-STATE.md`; never read
that multi-megabyte ledger wholesale. The soak queue is consumed by the
automation between iterations; fold only new tail lines into the next audit.
