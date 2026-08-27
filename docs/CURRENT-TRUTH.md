# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact commands,
counts, and probe rows remain in the ledger and scratch artifacts.

Current maintenance marker: Session 2770 (2026-08-27).

This file was compacted in Session 2748 because it exceeded the 60,000-byte
maintenance threshold. Run-by-run history removed here remains in git history,
the ledger, and the referenced scratch records.

## Live result

The qualified port route is `ROGUESQ_LLE_FORCE=1`,
`ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. `ROGUESQ_SPIN_YIELD=1`
is diagnostic. `ROGUESQ_AUTOPILOT` is the reliable in-process driver.

M5 defaults to the Factor 5 image arm. `ROGUESQ_AUDIO_UCODE=0` selects the
silent `musyx_stub` control. Stock `aspMain` is not the retail contract;
MORT is a separate CPU speech boundary.

The qualified driver reaches title (`VI 1024`, origin `0x00790400`) and
hangar (`VI 512`, origin `0x006AB400`) under the appropriate input path.
Retail oracle runs independently reach attract, title, and hangar, but not a
mission. A whole-RDRAM watch is the required positive control before any
narrow retail memory claim.

The latest durable M5 chain is:

- The image arm has live image DMEM/DMA/completion activity; the silent arm
  does not. This separates routing from the silent control.
- Image-stage and candidate ring destinations are live, but no legitimate
  writer, payload, and ordering edge has been named.
- The CPU MORT filter writes persistent voice state and the renderer consumes
  voice-local mixed words. The named renderer, mixer, streamed-voice,
  service, AI-worker, PI, queue, and host-AI audits found no copy into the AI
  source span.
- The AI worker allocates and clears `0x801496B0:0x8014C6B0`, then submits
  aliases directly through the pointer-preserving host AI bridge. The named
  source span has no generated scalar writer or named indirect producer.
- SP-yield state is now real API state, but the phase-gated validation did not
  reach the target yield phases; a generated call-site census found only the
  generic scheduler's two yield calls, with no audio-specific branch.
- The fresh `serviceVoicePoolFrame` audit found cadence, slot streaming state,
  startup, and reaping only. The `serviceStreamingVoice` audit found a
  legitimate ring write through `decodeAndFillVoiceBlock`, but no direct AI
  publication. Its callback-edge audit corrected the field identification:
  `serviceStreamingVoice` loads its indirect target from descriptor `+0x190`,
  while `+0x194` is the legitimate speech-sample source. The target is the
  fixed `dmaVoiceSampleAndSignal` routine, which performs sample DMA into the
  voice ring and sends a completion message; it has no AI publication edge.
- The bounded speech-loader surface audit found that `loadSpeechFile` writes
  only speech metadata and performs asset DMA, `initMusyXVoiceSlot` initializes
  slot pointers/state, and `consumeVoiceSamples` advances counters/status. It
  has no PCM/AI-visible payload writer or new ordering edge.
- `osAiGetStatus_recomp` now reports runtime buffered-audio state instead of
  unconditionally returning zero. The Debug target compiled and linked;
  the same-build image/silent validation emitted positive set-next and
  audio-task controls but no status/length query in either arm. A generated
  source census independently finds no caller for either query. The shim's
  live/empty semantics are therefore not exercised; do not treat this API as
  the PCM blocker.

The M5 publication edge remains unresolved. No writeback, remap, forced slot
state, gate bypass, or mitigation is authorized without a named writer,
legitimate payload, destination, and ordering relation. Any mitigation-shaped
diff must include an `ORIGIN:` line naming the writer and stating whether its
value is legitimate.

## Next steps

Priority follows the user directive: maintenance, then M5, then systematic M3,
then generated-symbol renaming when M5 is closed and M3 is parked.

1. **M5 Step 1 re-baseline — phase control still required.** Session 2769
   ran the retail oracle and both same-build audio arms, but the port stayed
   in 320/640 cinematic phases and never reached title `1024` or hangar
   `0x006AB400`; the row is invalid and selects no audio hypothesis. The
   oracle whole-RDRAM control did pass and independently reached title and
   hangar. Retry the same image/silent pair with the qualified AUTOPILOT route
   and the compiled C88 default (do not force `ROGUESQ_M5_C88_VALUE=0`) before
   interpreting any downstream null.

2. **Generated-symbol renaming sweep — next bounded fallback.** The M5
   AI-status shim is now validated as unreachable at the generated qualified
   route; preserve the shim but do not pursue its unexercised semantics.
   The `0x800F9000..0x800FB000` interval is synchronized. The widened
   `0x800FB000..0x800FF000` sweep renamed the two known invalid data gaps as
   `data_gap_800FBE14` and `data_gap_800FEF04`. The
   `0x80101000..0x80103000` interval is now synchronized; continue with
   `0x80105000..0x80107000`, `0x80107000..0x80109000`, and
   `0x80109000..0x8010B000` are now synchronized. Session 2770 also
   reconciled three address-encoded checked-in symbols with their companion
   names: `lvi/lvk/lvj_objectiveSlot1`. Continue with
   `0x8010B000..0x8010D000`, preserving
   ambiguous/fake/address-only symbols.

3. **M5 CPU-side MORT publication — unresolved, callback edge closed.** The
   corrected `+0x190` callback edge is `dmaVoiceSampleAndSignal`; its
   legitimate destination is the voice ring and its ordering edge is the
   completion queue. `+0x194` is the sample source. Do not repeat this edge or
   add a runtime watch until a new legitimate AI destination and order are
   named. The speech-loader surface is now closed as service-only; the
   remaining publication boundary is unresolved.

4. **External retail-entry boundary — parked revisit.** Only return with a
   genuinely new, phase-qualified oracle discriminator. The oracle's whole-
   RDRAM positive control is mandatory; it currently does not drive missions.

5. **M4 accumulator origin — parked.** The absolute-DMEM path is localized to
   its known producer, selector state, and indirect consumer. Pointer-relative
   `0xB00/B02/B04` matches are unrelated fields. The dynamic producer-slot /
   consumer-index equality remains unresolved; broad range watches are not a
   substitute.

6. **M3 crash work — parked.** Resume only as a complete idiom-class audit
   with a named discriminator. Passive recurrence belongs in the soak queue.

7. **M5 image task contract and hangar visual artifact — parked.** Implement
   no image writeback/remap without a named legitimate image writer and
   destination/order relation. H2 and consumer-mode H1 are refuted; H3 is
   unavailable because the oracle cannot screenshot the LLE path.

## Durable boundaries

### Route, rendering, and Factor 5

Factor 5 uses custom GBI mappings documented in
[`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md). Do not infer stream
semantics from standard F3DEX. The qualified route remains LLE-only for the
Factor 5 path, with existing defensive runtime guards retained until a named
writer explains a bad value.

The overlay-dispatch explanation is historical, not the current blocker. The
current qualified path reaches the title and hangar boundaries described
above. RT64's interpreter safety limit and mid-task null-GBI guard remain
intentional diagnostics/safety mechanisms.

### M5 audio and image output

Factor 5 image tasks and CPU MORT speech are separate contracts. A `Broke`
return proves task completion only, not PCM correctness. The host AI bridge
preserves the guest pointer and length into SDL; no host remap or gate was
found. The named PI service carries descriptors and generic DMA only.

MusyX audio is not stock `aspMain`. The current image task is the qualified
audio-ucode route; the MORT CPU path is separately audited. Audio remains
partly stubbed, so every de-stub must be incremental and followed by a
phase-qualified validation with a same-run positive control.

### Safety and evidence

- Ask the retail oracle for ground truth before adding port instrumentation.
- Batch all discriminator counters in one build and one phase-gated run.
- A null result is invalid without a positive control in that same run.
- Scope counters and log budgets to the target phase; do not use stopwatch
  comparisons on animating scenes.
- Use the regeneration order `make_elf.py`, N64Recomp, fixup scripts, CMake.
  Never hand-edit generated game functions for behavior changes.
- Kill runs with SIGKILL, run from `build/`, and keep the ROM present.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. If `lib/` changes, export its patches in the same
  iteration.
- A work unit is one experiment or one bounded change. Before building, write
  competing hypotheses and the outcome that discriminates them in `NEXT.md`.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed. The detailed
failed experiments remain in `PORTING-STATE.md` and the project overview.

Static boundary-only symbol classifications remain non-renames when companion
symbols, source/m2c, callers, and local semantics do not provide a defensible
name. Stable companion duplicate-prefix and preamble mappings belong in
`tools/rename/build_redefs.py`.

## Archived durable progression

The detailed s2–s2676 history was migrated to `PROJECT-OVERVIEW.md` during
earlier maintenance passes. Sessions s2677 onward remain in the append-only
ledger. The current late-chain checkpoints are:

- s2678–s2681: retail CPU edge, renderer/AI candidate ranges, and positive
  controls were established; candidate AI ranges were not joined to renderer
  output.
- s2682–s2698: renderer, mixer, stream, service, queue, AI allocation,
  registration, PI, and host-AI audits rejected the named publication paths.
- s2699–s2738: rename tooling was hardened and adjacent generated regions were
  classified as synchronized or ambiguous/fake; exact matches were applied
  only when source-backed.
- s2739–s2741: SP-yield state was de-stubbed and its generic call sites were
  censused; target audio yield reachability remains unevaluable.
- s2742–s2745: MORT publication, callback, command-list, and voice-pool
  service boundaries were audited; no legitimate AI publication edge was
  found.
- s2746–s2747: verified fragment batches were renamed through the
  regeneration-safe map, changing references in the external generated tree.
- s2749–s2750: the streaming callback audit corrected the field offset,
  identified `dmaVoiceSampleAndSignal` as the fixed target, and ruled out AI
  publication in that callback.
- s2751: the speech-loader/voice-slot/cursor surface was audited; metadata,
  asset DMA, slot initialization, and cursor/state work were found, but no new
  PCM/AI publication edge.
- s2752: the generated-symbol interval `0x800E7000..0x800E9000` was fully
  synchronized; two fake/address-only placeholders were preserved and the
  next interval was advanced to `0x800E9000..0x800EB000`.
- s2753: the generated-symbol interval `0x800E9000..0x800EB000` was fully
  synchronized; three ambiguous/address-only placeholders were preserved and
  the next interval was advanced to `0x800EB000..0x800ED000`.
- s2754: the generated-symbol interval `0x800EB000..0x800ED000` was fully
  synchronized; three fake/address-only placeholders were preserved and the
  next interval was advanced to `0x800ED000..0x800EF000`.
- s2755: generated-symbol intervals through `0x800F3000` were already
  synchronized, so no rename was selected. The M5 AI status stub was then
  de-stubbed to report buffered-audio state; the Debug target built and linked.
- s2756: the AI-status validation built image and silent arms together. Both
  emitted set-next and audio-task controls, but neither called status/length;
  generated-source census independently found no caller. The status shim is
  not a qualified-route PCM blocker, and the rename sweep resumes.
- s2757: the generated-symbol interval `0x800ED000..0x800EF000` had no stale
  placeholders eligible for renaming. Twelve semantic symbols were already
  synchronized; `fake_func_800ED148` was preserved as ambiguous/fake. The
  next interval is `0x800EF000..0x800F1000`.
- s2758: the generated-symbol interval `0x800EF000..0x800F1000` had no stale
  placeholders eligible for renaming. Semantic companion entries were already
  synchronized; `fake_func_800EFD74` and `fake_func_800EFDDC` were preserved
  as ambiguous/fake. The next interval is `0x800F3000..0x800F5000`.
- s2759: the generated-symbol interval `0x800F3000..0x800F5000` had nine
  semantic companion entries, all already synchronized. No stale placeholder,
  fake/address-only candidate, or conflicting alias was found; the next
  interval is `0x800F5000..0x800F7000`.
- s2760: the generated-symbol interval `0x800F5000..0x800F7000` had four
  semantic companion entries, all already synchronized. No stale placeholder,
  fake/address-only candidate, or conflicting alias was found; the next
  interval is `0x800F7000..0x800F9000`.
- s2761: the generated-symbol interval `0x800F7000..0x800F9000` had three
  semantic companion entries, all already synchronized. No stale placeholder,
  fake/address-only candidate, or conflicting alias was found; the next
  interval is `0x800F9000..0x800FB000`.
- s2762: the generated-symbol interval `0x800F9000..0x800FB000` had 28
  semantic companion entries, all already synchronized. The sole placeholder
  was `fake_func_800FA248`, classified as fake/ambiguous and preserved; no
  stale semantic placeholder or conflicting alias was found. The next interval
  is `0x800FB000..0x800FD000`.
- s2763: the widened generated-symbol interval `0x800FB000..0x800FF000`
  contained only already-synchronized semantic entries plus two invalid
  generated data gaps. The regeneration-safe map renamed those gaps to
  `data_gap_800FBE14` and `data_gap_800FEF04` across declarations, bodies, and
  overlay registration; no function body or runtime behavior changed. The next
  interval is `0x800FF000..0x80101000`.
- s2764: the generated-symbol interval `0x800FF000..0x80101000` had eight
  companion candidates, all already synchronized. An independent generated-tree
  scan found no placeholder in the interval, so no generated-tree change or
  build was needed. The next interval is `0x80101000..0x80103000`.
- s2765: the generated-symbol interval `0x80101000..0x80103000` had only
  already-synchronized semantic candidates plus `fake_func_80101CCC` and
  `fake_func_80102A98`, both preserved as ambiguous/fake. The regeneration-safe
  selection changed zero references and returned its expected no-rename status;
  an independent scan confirmed those were the only placeholders in the
  interval, and `git diff --check` passed. The next interval is
  `0x80103000..0x80105000`.
- s2766: the generated-symbol interval `0x80103000..0x80105000` had only
  already-synchronized semantic candidates plus four placeholders classified
  as ambiguous/fake: `fake_func_8010357C`, `fake_func_80103D08`,
  `fake_func_80104208`, and `fake_func_801044D8`. The regeneration-safe
  selection changed zero references; an independent scan confirmed no stale
  semantic placeholder in the interval, and `git diff --check` passed. The
  next interval is `0x80105000..0x80107000`.
- s2767: the generated-symbol interval `0x80105000..0x80107000` had 11
  semantic companion candidates, all already synchronized. The three
  placeholders `fake_func_80105B54`, `fake_func_8010619C`, and
  `fake_func_80106BE8` were preserved as ambiguous/fake. The regeneration-safe
  selection changed zero references; an independent scan confirmed no stale
  semantic placeholder in the interval, and `git diff --check` passed. The
  next interval is `0x80107000..0x80109000`.
- s2768: the generated-symbol interval `0x80107000..0x80109000` had 23
  semantic companion candidates, all already synchronized. The three
  placeholders `fake_func_8010721C`, `fake_func_80107EA4`, and
  `fake_func_80108B8C` were preserved as ambiguous/fake. The regeneration-safe
  selection changed zero references; an independent scan confirmed no stale
  semantic placeholder in the interval, and `git diff --check` passed. The
  next interval is `0x80109000..0x8010B000`.
- s2770: the checked-in symbol map reconciled three address-encoded objective
  slot names at `0x801091F8`, `0x801095CC`, and `0x80109628` with the
  companion semantic names `lvi/lvk/lvj_objectiveSlot1`. The generated tree
  already contained those names, so no regeneration or build was needed.
Exact counts, evidence tables, and rejected hypotheses are authoritative in
the corresponding scratch directories and ledger entries.
