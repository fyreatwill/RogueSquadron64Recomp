# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
background and archived lineages are in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md);
exact run recipes and evidence remain in the append-only ledger and scratch
artifacts. This file is intentionally compact and is the required pre-work
read.

Current maintenance marker: Session 3117 (2026-08-28).

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

The strongest route boundary remains the independent comparison: retail
reaches title at 1024 and hangar at 512, while the recent same-build port
capture issues only widths 320, 2, 640, and 640 and remains at VI 640. The
port's audio-arm dispatch controls are positive in earlier qualified runs,
so a zero target-phase audio row is not evidence of absent dispatch.

## Next steps

Priority is maintenance, then M5 de-stubbing, then systematic M3, then the
generated-symbol sweep. Maintenance is complete and M5 design is complete;
Step 1 is route-blocked. M3 is parked pending a new discriminator.

1. **M5 VI publication — test the new handoff.** Use the retail oracle to
   watch guest PC `0x800C2984` with a whole-RDRAM positive control and
   title/hangar phase controls. Transition-time execution selects the new
   handoff; target-only execution makes it a consumer; no execution with
   valid controls makes it dead or aliased. Do not repeat closed ranges.

2. **M5 audio de-stubbing — qualify Step 1, then implement one named edge.**
   Resume only when a port run reaches target phases. Use the phase-keyed
   task/DMA/return/service/slot/voice/MORT/PCM table with image and silent
   arms in one build/run. A qualification result alone does not authorize a
   gate, wait, voice, destination, or output change.

3. **M3 crash work — systematic idiom-class audits only.** A new unit must
   enumerate the entire idiom class, name its discriminator, and guard or
   prove every site. Passive crash recurrence belongs in the soak queue.

4. **External retail-entry boundary.** Parked after the candidate set was
   rejected; revisit only with a different static handoff and independent PC
   attribution.

5. **M4 accumulator origin.** Parked because the latest route qualification
   had no target-phase positive-control rows. Do not interpret its nulls.

6. **M5 SP-yield lifecycle and CPU-side MORT publication.** Parked pending a
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
