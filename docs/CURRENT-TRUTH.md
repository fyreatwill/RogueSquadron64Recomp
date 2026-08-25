# Rogue Squadron 64 Recomp — current truth

Operational front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history through s2357 is archived in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md)
§48; the append-only ledger remains authoritative for exact commands, counts,
and probe rows.

Maintained in Session 2359 (2026-08-24). The M5 retail task-field payload/order
capture passed its controls after the recipe was corrected to include the
watch-5 phase histogram. The exact writer is positive for every task-matched
phase/field key, but its nonzero values do not match the retained port payload
at the comparable rows. Two phase/field keys have no retained port profile, so
the remaining source relation is unresolved there.

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The old boot/menu-overlay explanation is closed.
- The qualified route is
  `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_SPIN_YIELD=1`,
  `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. Spin yield is gated and
  default-off.
- Product multi-header freelist restore is on. Garbage-CIMG and wrap-drop
  mitigations are off. Any future mitigation requires a named writer, a
  legitimacy judgment, and an `ORIGIN:` line.
- M5 defaults to the Factor 5 image arm. `ROGUESQ_AUDIO_UCODE=0` selects the
  silent `M_AUDTASK` `Broke` stub used for controls. The image arm performs
  real DMEM work, returns `Broke`, emits generated DMA, and can publish PCM;
  its host canary is probe data only. Stock `aspMain` is not this game's
  contract. MORT is a separate CPU speech asset.
- `docs/M5-AUDIO-PLAN.md` is the design gate for incremental audio
  de-stubbing. The current measured boundary is retail task-field writer
  source/payload relation; no port contract change is authorized.
- The independent retail oracle is the witness for game-side memory claims.
  Its whole-RDRAM, target-window, phase, status/task, and named-PC controls
  must pass before a retail null is interpreted. It reaches attract, title,
  and hangar, not a mission.
- The M5 task ABI address relation is independently real: retail type-2 tasks
  point at the watched field set through `data_ptr+0x100`. Retail PC
  `0x80090CA4` then stores nonzero values at every task-matched phase/field key
  in the s2359 capture, but 910 comparable values mismatch the retained s2352
  port field payload and none match. This is a payload/source discriminator,
  not permission to alter task data or port writeback.

## Latest evidence

- **s2357 — task ABI names the exact field destination.** A fresh retail
  capture passed whole-RDRAM `59,327`, target window `44,120`, exact fields
  `492/1,734/1,492/1,489`, four phase histories, writer histograms, named PCs,
  and the retained four-arm port controls. The task probe at `0x80033FCC`
  recorded `2,477` bounded type-2 rows, with zero invalid pointers or
  overflow; every `data_ptr+0x100` matched one of four watched fields. The
  writer/port join had `1,153` nonzero relations and `1,324` zero/sentinel-only
  rows. This selects `H-RetailTaskAbiNamesPortField` at capture scope. It does
  not authorize writeback, task-data edits, consumer/default changes, or a
  guard. Artifacts: `scratch/agent/s2357_m5_task_abi/`.
- **s2359 — exact writer is present but payload-mismatched.** The corrected
  capture passed whole-RDRAM `59,303`, target window `44,100`, exact fields
  `491/1,733/1,491/1,488`, all four phase histories, 25/25 named PCs, the
  task dump, four port controls, and post-value detail with zero detail
  overflow. The writer histogram and post-value rows were positive for all
  four task-matched phase/field keys. Of 2,038 joined post rows, 910
  nonzero values mismatched the retained s2352 field payload, 0 matched, 17
  were zero/sentinel-only, and 1,111 had no retained port profile. The task
  ordinal can only be carried as a phase/field range because the oracle emits
  task ordinal and writer VI separately. Artifacts:
  `scratch/agent/s2359_m5_task_value_order/`.
- **s2356 — value-only role join was ambiguous.** Controls passed, but the
  candidate writer/value join had zero nonzero matches and only zero/sentinel
  intersections. This is superseded by s2357's independent address relation.
- **s2355 — hangar writer values did not match port fields.** All nine positive
  writer keys were retained after the detail cap was raised; the only shared
  value was the common zero sentinel. This selected
  `H-RetailWriterIsUnrelated` at that capture scope, before the independent
  task-ABI naming result.
- **s2354 — first payload capture overflowed.** The result was rejected as a
  capture-capacity failure, not as evidence of a null writer.
- **s2343–s2353 — C88 and field provenance.** Retail independently writes
  `0x8008EC88 -> 0x01000000`; the port arms requested nonzero but stored zero.
  An opt-in C88 treatment restores the gate and exposes intermediate
  key-on/slot/filter work, but not a complete PCM/voice contract. Subsequent
  output and writer censuses found zero port ABI output metadata, closed
  `0x80094648` as an unrelated sentinel writer, and mapped known retail writer
  PCs to the exact title/hangar field set. The payload/order contract remains
  open. See §48 for the durable sequence and independent controls.

## Active backlog

Closed investigations are not active work items. This is one monotonic
sequence; #1 is the next campaign priority.

1. **M5 audio de-stubbing — active.** Keep `docs/M5-AUDIO-PLAN.md` as the
   design gate and proceed only with ground-truth-first, positive-control-
   qualified steps. The next queued boundary is #2.
2. **M5 retail writer source relation — next.** Add phase-gated execution
   GPR rows for `0x80090CA4` and join them by writer VI/field to the existing
   task-field and post-value records. Determine whether the writer's source
   pointer/arguments resolve to the task `data_ptr`, a retained port field, or
   a separate retail state buffer. Do not write back a field, alter task data,
   change a consumer/default, or add a guard.
3. **M5 A1 second-origin transition — parked.** Resume only with a new
   discriminator that restores `0x00696100`/`0x00696600` coverage; do not repeat
   the failed four-arm/two-wave matrix.
4. **M3 crash work — parked.** Resume only as a systematic idiom-class audit
   with a named discriminator; do not chase a single recurring crash.
5. **Hangar visual artifact — parked.** Malformed-triangle H2 and consumer-mode
   H1 are refuted. H3 is unavailable because the oracle cannot screenshot the
   LLE path; do not repeat the capped `0xD60` scan.

## Durable boundaries

### Route, rendering, and Factor 5

The accepted route table selects `LLE_UNGATED=1, LLE_SOLO=1`: `11` reaches
title and hangar, `01` reaches title only, and `10`/`00` reach neither. Menu
spin yield is a diagnostic route aid, not a default behavior change. Factor 5
command mappings and the required independent controls are documented in
[`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md) and
[`tools/oracle/README.md`](../tools/oracle/README.md). Read them before
reasoning about a DL/RDP anomaly; the runtime cannot witness its own null.

### M5 audio and image output

Direct service entry/exit, the service gate/loop, and task/AI boundary are live
on the port. The image arm changes DMEM, completes, emits generated DMA, and
can publish a nonzero PCM join; destinations and stage/consumer polarity
rotate by capture. The C88 treatment reaches intermediate key-on/slot/filter
work, but exact task publication and voice completion remain open.

The durable recent sequence is: s2346 found completed image tasks with zero
output metadata and zero generated-range overlap; s2347 found an independent
retail output-span writer while port ABI output stayed zero; s2348 closed that
writer as unrelated to the computed task field; s2349–s2353 mapped the exact
field set across title and hangar; s2354 rejected an overflowing payload
capture; s2355 found no nonzero value match; s2356 left the task-ABI relation
open; s2357 closed the address/naming boundary with `1,153` nonzero
task/field/writer/order relations; and s2359 found the exact retail writer but
a payload mismatch at the comparable rows. The remaining question is writer
source/provenance, not permission to patch the port.

No behavior change is authorized by these results. In particular, do not
promote the C88 writer, invent output metadata, remap destinations, alter task
data, force a consumer, or add a defensive guard without a new discriminator
and a named legitimate/illegitimate writer.

### VI state and second origin

Retail's `__osViNext` context uses `framep` plus the selected field to produce
the next origin. The port has matching framebuffer/mode candidates, but its
default selector, guest `comRegs.vCurrent`, and published current-line bit
remain zero. Opt-in field/current-register/timing/total-VI arms recover the
split, but the natural host publisher and cadence are unidentified. The A1
matrices were route-invalid and do not select a VI arm.

### Key-on, M3, M4, and symbols

Retail reaches the alternate key-on transfer path and skips the eight port
divide PCs. The port has positive normal-tail/slot behavior with divisor
`0xC0` and no guard hits. Exact `(origin,width,PC)` buckets differ in both
directions; the common cross-runtime pointer/source/state witness is not
restored. The `-0x25A4` pointer-chase, six-site PIC, ten-site audio-slot,
slot-dispatch, two-line overlay-move, and leftover `fake_func_*` size-class
audits are closed at their stated scopes. Generated-symbol renaming is closed
at the useful boundary; do not invent names for
`func_8000040C`, `func_800927B0`, `func_80092A54`, `func_80092CF0`, or
`func_800E9AE0`.

## Superseded conclusions

These were believable before qualified routes and independent controls, but
are superseded at their measured scopes:

- The old overlay/menu explanation, intrinsic 640 flakiness, missing
  input/wait-return claims, and unqualified PCM-null claims.
- Clean-stub, canary-poison, final-E50, uniform-gate, host-isolator, and
  global-zero image-DMA explanations.
- s2190–s2197 second-origin/caller explanations and s2283/s2284 A1 matrices;
  both were coverage artifacts and do not identify a VI publisher.
- s2228 and s2242–s2259 image/pair crash splits; they were intermittent route
  loads, not intrinsic image or writer defects.
- s2288's stub-first route conclusion and s2286's logger-removal explanation;
  explicit input qualified both arms, while logger removal changed timing but
  did not restore the route.
- s2320's broad retail zero-only result and s2321's target-absence result;
  later requested-writer/status tables found target `01/02` stores and
  complete `01 -> 02 -> 03 -> 00` cycles.
- s2304's route-wide same-ordinal PCM gap, s2307's fixed target addresses,
  s2308's retail-normal zero-fill interpretation, and s2325's destination-role
  split; later captures showed temporal joins, rotating destinations, an
  independent retail nonzero ring, and exact PCM joins.
- s2331's unevaluable filter/voice null; s2332 added a host-positive span
  control and showed the real port audit still had zero rows while retail
  executed the caller/callee.
- s2335–s2342's successive inactive-parent/gate labels; each was refined by a
  deeper positive control until the measured boundary reached the C88 byte
  test. s2343 then identified the port writer mismatch, and s2344 showed the
  opt-in gate treatment was real but incomplete.
- s2345's task-output-gap label; s2346 found completed image task intervals
  whose output metadata and DMA overlap were both zero.
- s2346's output-metadata-writer-absent label; s2347 found a positive retail
  output-span writer, and s2348 closed the observed candidate as unrelated to
  the task field.
- s2349–s2356's successive retail writer-placement/value ambiguities; s2357's
  independent task dump established the exact `data_ptr+0x100` field relation.

## Evidence and safety rules

- Ask the retail oracle for ground truth before adding an instrument. Arm its
  whole-RDRAM positive control first; watches are physical and phase-gated by
  VI callbacks.
- A null requires a same-run positive control. Batch all counters and A/B
  arms in one build/run, scope budgets to the phase, and use VI gates rather
  than elapsed time for animated scenes.
- Regenerate in order: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then
  CMake. Diagnostics in generated output belong in fixup scripts.
- Kill runs with SIGKILL, never SIGTERM. Run from `build/` with the ROM
  present. Capture paths must not start with `.` in the final component.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. If `lib/` changes, export submodule patches in the same
  iteration.
- A mitigation is not an explanation: name the writer, state legitimacy, and
  add an `ORIGIN:` line before landing a skip, allow, guard, or restore.
- Never add a diagnostic field without a complete discriminating table and an
  outcome that can select among hypotheses.
