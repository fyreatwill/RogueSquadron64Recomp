# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact commands,
counts, and probe rows remain in the ledger and scratch artifacts.

Current maintenance marker: Session 2841 (2026-08-27).

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
- Session 2775 retried the same-build image/silent pair with C88 unset and
  the phase-gated driver, but its recipe still supplied no phase-relative
  probe-key schedule. The retail whole-RDRAM positive control passed and
  reached title 1024 plus hangar `0x006AB400`; both port arms stalled at VI
  640/origin `0x0066A500`. Image dispatch controls diverged from silent as
  expected, but all target-phase audio/PCM rows are invalid and select no
  publication hypothesis.
- Session 2776 repaired the driver twice and ran a same-build concurrent pair:
  explicit phase-relative keys were first blocked by the 1024 gate, and the
  restored autopilot plus a boot-time key schedule still left both arms at
  VI 640/origin `0x0066A500`. Quoting the zsh environment array fixed the
  launcher, and image/silent dispatch controls were positive (`48`/`47`,
  `real_ucode=1`/`0`), but neither arm reached title or hangar. The oracle
  whole-RDRAM control passed (`10000`) and independently reached both phases.
  The target-phase audio/PCM table is therefore invalid; no M5 publication
  hypothesis is selected.
- `osAiGetStatus_recomp` now reports runtime buffered-audio state instead of
  unconditionally returning zero. The Debug target compiled and linked;
  the same-build image/silent validation emitted positive set-next and
  audio-task controls but no status/length query in either arm. A generated
  source census independently finds no caller for either query. The shim's
  live/empty semantics are therefore not exercised; do not treat this API as
  the PCM blocker.
- Session 2777 corrected the AI status shim's nonzero result from boolean `1`
  to the N64 `AI_STATUS_FIFO_FULL` bit (`0x40000000`). This is a contract
  correction, not a publication-edge explanation; the generated source census
  still finds no qualified status caller, so runtime status remains unexercised.
- Session 2791 completed the SP-yield request lifecycle de-stub: a new
  `osSpTaskStartGo_recomp` clears the prior request before staging the next
  task. The Debug `librecomp` target builds successfully. The full target is
  currently blocked by the pre-existing duplicate generated definition of
  `lv2_initializeObjectTracking` in `funcs_43.c`; no task interruption or
  resumption behavior was added.
- Session 2792 reran the prescribed full Debug target and `git diff --check`.
  The build again stopped before linking at the duplicate generated
  `lv2_initializeObjectTracking` definition in `funcs_43.c`; whitespace
  validation was clean. This validates the known build boundary only and
  provides no runtime evidence about SP-yield behavior.
- Session 2798 corrected the generated-symbol batch that caused that build
  boundary. The companion map explicitly marks `0x80101CCC` as a four-byte
  fake/data entry before the real `lv2_initializeObjectTracking` at
  `0x80101CD0`; the generated declaration, definition, and overlay entry now
  use `data_gap_80101CCC`. The same correction was applied to the 13-entry
  `lv*` fake/data cluster from the prior batch and to the rename map. The
  generated target now builds successfully, with zero duplicate function
  definitions. This is a symbol/compile result, not audio-runtime evidence.
- Session 2799 rebuilt the full Debug executable successfully after that
  repair. The same-build retail oracle passed its whole-RDRAM control and
  independently reached title and hangar; both qualified port arms had live
  audio dispatch controls (52 each), no crash/abort, but stalled at VI 640 /
  origin `0x0066A500`. No target-phase SP-yield, task, or PCM rows were
  emitted, so the landed SP-yield lifecycle remains runtime-unvalidated.
- Session 2800 closed generated-symbol interval `0x80137000..0x80139000`.
  Four semantic companion entries (`gPlayers`, `gObjectiveCounts`,
  `gObjectiveBooleans`, and the voice-text fields) were already synchronized;
  the selector changed zero references, and an independent generated-tree
  scan found no `func_8013*` or `fake_func_8013*` placeholders. No rename or
  build was needed.
- Session 2801 closed generated-symbol interval `0x80139000..0x8013B000`.
  The selector classified 18 companion entries: semantic entries were already
  synchronized and ambiguous/data entries were preserved. It changed zero
  references in zero files, and the independent generated-tree scan found no
  matching placeholders. No rename or build was needed.
- Session 2802 closed generated-symbol interval `0x8013B000..0x8013D000`.
  The selector changed zero references in zero files, and the independent
  generated-tree scan found no `func_8013*` or `fake_func_8013*` placeholders.
  No rename or build was needed.
- Session 2803 closed generated-symbol interval `0x8013D000..0x8013F000`.
  The selector classified one candidate at `0x8013D880` as ambiguous-or-fake,
  changed zero references in zero files, and the independent generated-tree
  scan found no `func_8013*` or `fake_func_8013*` placeholders. No rename or
  build was needed.
- Session 2804 closed generated-symbol interval `0x8013F000..0x80141000`.
  The selector changed zero references in zero files, and the independent
  generated-tree scan found no `func_8013*`, `fake_func_8013*`, `func_8014*`,
  or `fake_func_8014*` placeholders. No rename or build was needed.
- Session 2805 added four source-backed data-gap mappings and applied them to
  the generated snapshot: `fake_func_8000537C`, `fake_func_8000737C`,
  `fake_func_800074D8`, and `fake_func_80007908` became explicit
  `data_gap_*` names. The companion map marks each fake record immediately
  before a named function; the selector changed 12 references in four files.
  This is a symbol-clarity change, not audio or runtime evidence.
- Session 2806 closed generated-symbol interval `0x80143000..0x80145000`.
  The bounded selector found no companion candidates and changed zero
  references in zero files; the independent generated-tree placeholder scan
  was empty. The interval is already synchronized and no build was needed.
- Session 2807 closed generated-symbol interval `0x80145000..0x80147000`.
  The bounded selector changed zero references in zero files, and the
  independent generated-tree placeholder scan was empty. The interval is
  already synchronized; no build or game soak was needed.
- Session 2808 closed generated-symbol interval `0x80147000..0x80149000`.
  The bounded selector changed zero references in zero files, and the
  independent generated-tree placeholder scan found no `func_8014*` or
  `fake_func_8014*` definitions or references. The interval is already
  synchronized; no build or game soak was needed.
- Session 2809 closed generated-symbol interval `0x80149000..0x8014B000`.
  The bounded selector found one already-synchronized candidate,
  `0x80149470 aspTask`, changed zero references in zero files, and preserved
  it. The independent generated-tree placeholder scan found no `func_8014*`
  or `fake_func_8014*` definitions or references. No build or game soak was
  needed.
- Session 2810 closed generated-symbol interval `0x8014B000..0x8014D000`.
  The bounded selector changed zero references in zero files, and the
  independent generated-tree placeholder scan found no `func_8014*` or
  `fake_func_8014*` definitions or references. No build or game soak was
  needed.

- Session 2811 closed generated-symbol interval `0x8014D000..0x8014F000`.
  The bounded selector changed zero references in zero files, and the
  independent generated-tree placeholder scan found no `func_8014*` or
  `fake_func_8014*` definitions or references. No build or game soak was
  needed.

The M5 publication edge remains unresolved. No writeback, remap, forced slot
state, gate bypass, or mitigation is authorized without a named writer,
legitimate payload, destination, and ordering relation. Any mitigation-shaped
diff must include an `ORIGIN:` line naming the writer and stating whether its
value is legitimate.

Session 2831 revisited the parked M4 producer/consumer join after the recent
15-session sweep streak made another sweep interval ineligible. The rebuilt
qualified LLE-solo run had positive `[f5-fetch-control]` activity (8 rows) and
M4 control markers (514 rows), but stopped at VI 640/origin `0x0066A500`
before title or hangar and emitted zero producer/consumer `[m4-index]` rows.
This is single-source control-only evidence: it makes the M4 join
unevaluable in this window, and does not select either a live join or an index
mismatch. Keep the accumulator boundary parked until a phase-qualified title
or hangar route exists.

Session 2812 pivoted from the already-synchronized `0x8014F000..0x80151000`
interval to a bounded source-backed data-gap rename batch. The selector now
maps `0x80064294`, `0x80064934`, and `0x80065A5C` to explicit `data_gap_*`
names and changed 9 generated references in the external snapshot. This is a
symbol-clarity change only; it adds no M5 or runtime evidence.

Session 2813 closed generated-symbol interval `0x80151000..0x80153000`.
The selector found one companion candidate, `0x801529C0 D_801529C0`, and
classified it as ambiguous-or-fake; it changed zero references in zero files.
The independent generated-tree placeholder scan found no `func_8015*` or
`fake_func_8015*` definitions or references. No build or game soak was needed.

Session 2814 closed generated-symbol interval `0x80153000..0x80155000`.
The selector preserved one ambiguous-or-fake candidate at `0x80153420` and
found three semantic entries already synchronized (`numSpeechSamples`,
`speechSampleOffsets`, and `speechFile`); it changed zero references in zero
files. The independent generated-tree placeholder scan found no
`func_8015*` or `fake_func_8015*` definitions or references. No build or game
soak was needed.

Session 2815 closed generated-symbol interval `0x80155000..0x80157000`.
The bounded selector changed zero references in zero files, and the
independent generated-tree placeholder scan found no `func_8015*` or
`fake_func_8015*` definitions or references. No build or game soak was
needed.

Session 2818 closed generated-symbol interval `0x8015B000..0x8015D000`.
The bounded selector changed zero references in zero files, and the
independent generated-tree placeholder scan found no `func_8015*` or
`fake_func_8015*` definitions or references. The interval is already
synchronized; ambiguous/data entries remain preserved. No build or game soak
was needed.

Session 2824 closed generated-symbol interval `0x80167000..0x80169000`.
The bounded selector changed zero references in zero files, and the
independent generated-tree placeholder scan found no `func_8016*` or
`fake_func_8016*` definitions or references. No companion candidates were
selected; ambiguous/data entries remain preserved. No build or game soak was
needed. This is symbol-clarity evidence only.

Session 2825 closed generated-symbol interval `0x80169000..0x8016B000`.
The bounded selector changed zero references in zero files, and the
independent generated-tree placeholder scan found no `func_8016*` or
`fake_func_8016*` definitions or references. No companion candidates were
selected; ambiguous/data entries remain preserved. No build or game soak was
needed. This is symbol-clarity evidence only.

Session 2819 renamed four source-backed non-callable main-overlay fragments
(`0x80005568`, `0x8000595C`, `0x80006BFC`, and `0x8000751C`) to explicit
`data_gap_*` names across the regeneration-safe selector and external
generated snapshot. The bounded selector changed 12 references in four
generated files; companion semantic candidates in the same range were already
synchronized or ambiguous. This is symbol clarity only, not runtime or M5
evidence.

Session 2833 renamed three additional short main-overlay fragments
(`0x8001C3FC`, `0x80023968`, and `0x80024128`) to explicit `data_gap_*`
names through the regeneration-safe selector and external generated snapshot.
The selector changed 9 references in five generated files; an independent
scan found all three names in declarations, bodies, and overlay registration
with no stale placeholder references. Their companion entries immediately
precede named routines, so this is symbol clarity only, not runtime or M5
evidence.

Session 2838 ran the independent retail gate watch and a fixed same-build
image/silent pair. The retail whole-RDRAM control fired 10,000 callbacks and
the gate watch fired twice from PCs `0x8008EA34` and `0x8008EB40`, but retail
remained at VI 320 with no title/hangar phase. Both port arms reached the same
pre-title VI 640/origin `0x0066A500`, each had 42 positive dispatch controls
(`real_ucode=1` versus `0`), and neither emitted target-phase gate, writer,
service, MORT, or PCM rows. The gate route is therefore unevaluable here; no
writer change or gate explanation is selected. The new recipe is
`scratch/agent/run_s2838_m5_gate_writer.sh`.

Session 2839 ran that recipe with the first-task boundary census enabled. The
retail whole-RDRAM control again fired 10,000 callbacks. Both port arms
reached the same pre-title VI 640/origin `0x0066A500`, produced 43 dispatch
controls, and produced the first 16 task-entry rows. For every ordinal, type,
ucode, ucode data, data pointer/size, output/yield fields, VI state, and task
staging fields matched; only the task-function pointer differed as the
intentional image (`real_ucode=1`) versus silent (`real_ucode=0`) arm choice.
No title/hangar, gate, writer, service, MORT, or PCM rows appeared. This
rejects a pre-title task-field selector mismatch in this run and selects the
post-dispatch or scheduling side of the route split; target-phase audio
behavior remains unevaluable.

Session 2841 renamed two additional source-backed short main-overlay records
(`0x80041EEC` and `0x800457CC`) to explicit `data_gap_*` names through the
regeneration-safe selector and companion map. The bounded selector selected
exactly those two records and changed six generated references across four
files; an independent scan found no stale placeholder references. The
callable-ambiguous `fake_func_8004661C` was preserved. This is symbol clarity
only, not M5 or runtime evidence.

Session 2842 continued the regeneration-safe symbol sweep at
`0x80049000..0x8004A000`. The only stale companion candidate,
`fake_func_800496F4`, was classified ambiguous-or-fake; the selector changed
zero references and preserved it. Neighboring callable symbols were already
synchronized. This is symbol-clarity evidence only; the next interval is
`0x8004A000..0x8004B000`.

## Next steps

Priority follows the user directive: maintenance, then M5, then systematic M3,
then generated-symbol renaming when M5 is closed and M3 is parked. The
generated-symbol sweep is also subject to the 15-title revisit rule.

1. **M5 audio de-stubbing — design gate complete (s2832); Step 1 route-gated
   baseline (s2834).** The refreshed
   `docs/M5-AUDIO-PLAN.md` inventories the active task, RSP, SP, guest-gate,
   voice, wait, AI, host, and MORT boundaries. The source survey found no new
   active audio stub or gate; it corrected the plan's stale description of
   `osAiGetStatus_recomp` to match its FIFO-full-bit implementation. The
   external generated snapshot is absent from this checkout, so generated
   audio behavior remains represented by checked-in anchors and fixup scripts.
   Do not change runtime behavior until Step 1's same-build qualification.
   Session 2834 passed the independent retail whole-RDRAM control and title /
   hangar route, and the same-build image/silent pair passed dispatch controls
   but both stalled at pre-title VI 640 / origin `0x0066A500`. All target-phase
   service, slot, MORT, and PCM nulls are therefore unevaluable; no contract,
   degeneracy, mixed-pipeline, or gate hypothesis was selected. The next M5
   unit needs a genuinely new route angle, not another target-phase null.

   Session 2835 reran the independent retail whole-RDRAM control and reached
   title `1024 @ 0x00790400` plus hangar `512 @ 0x006AB400`. In the same-build
   pair, the silent arm reached VI 640 / origin `0x0066A500`, while the image
   arm stayed at VI 320; both had positive audio-dispatch controls and no
   crash or abort. This selects an audio-route divergence in this window, but
   neither arm reached title or hangar, so all target-phase service, slot,
   MORT, and PCM rows remain unevaluable. The launch order/scheduling
   contribution is unresolved.

   Session 2836 inverted the pair launch order, starting image before silent.
   The independent retail control again passed (`whole_rdram=10000`, title,
   and hangar). Both port arms had positive dispatch controls and no crash or
   abort, but both stopped at pre-title VI 640 / origin `0x0066A500`; all
   target-phase rows remain unevaluable. Relative to s2835, this refutes a
   stable image-first launch-order advantage and leaves a nondeterministic or
   otherwise scheduling-sensitive route split unresolved.

   Session 2837 inserted a barrier after the image arm reached 40 positive
   dispatch rows before launching silent. The retail whole-RDRAM control again
   passed and independently reached title and hangar. Both port arms had
   positive dispatch controls (`real_ucode=1`/`0`), no crash or abort, and the
   same pre-title VI 640 / origin `0x0066A500` boundary; neither reached a
   target phase. The barrier did not select an initialization-race
   explanation; target-phase audio rows remain unevaluable and no behavior
   change is authorized.

2. **M5 audio de-stubbing — Step 1 route repair / qualification.** The
   initialization-barrier and gate-writer angles are currently unevaluable:
   s2837 waited for 40 image dispatches, and s2838 independently found retail
   gate writers but no target phase; both port arms still stopped at VI 640 /
   origin `0x0066A500`. Session 2839 found identical pre-title task fields and
   staging rows across the image and silent arms; only the intentional task
   function pointer differed. The selector mismatch hypothesis is rejected
   for this boundary. The next unit must discriminate post-dispatch execution
   or scheduling, then qualify the target phases.
   Once the
   title/hangar phases are reached, require the task-field, DMEM/DMA, image
   exit, SP completion, service/slot/voice, MORT, and PCM source/consumer
   rows. Do not land a behavior change from another pre-target null.

3. **Generated-symbol renaming sweep — next bounded batch.** The full
   Debug target now links after the fake/data collision repair, but the
   phase-gated validation still stalled before the target phases. Sessions
   2800–2809 closed intervals through `0x8014B000`; each had either
   already-synchronized symbols or preserved ambiguous/data entries, with no
   stale generated placeholders selected. Continue with
   preserving ambiguous/data entries and applying only source-backed names.
   Sessions 2815–2818 closed intervals through `0x8015D000`; all four
   selectors changed zero references in zero files and all independent
   placeholder scans were empty. Session 2819 classified four isolated
   main-overlay fragments as explicit `data_gap_*` names. Session 2820 closed
   `0x8015F000..0x80161000` with zero selected references and an empty
   independent placeholder scan. Session 2821 closed
   `0x80161000..0x80163000` with zero selected references, no companion
   candidates, and an empty independent placeholder scan. Session 2822 closed
   `0x80163000..0x80165000` with zero selected references, no companion
   candidates, and an empty independent placeholder scan. Session 2823
   closed `0x80165000..0x80167000` with zero selected references, no
   companion candidates, and an empty independent placeholder scan. Preserve
   ambiguous/data entries. The latest source-backed batch renamed three short
   main-overlay fragments at `0x8001C3FC`, `0x80023968`, and `0x80024128`.
   Continue with the next explicitly classified short data-gap batch; do not
   invent semantic names for callable-ambiguous placeholders.
   Session 2826 added five source-backed mechanical data-gap mappings for
   short defined records at `0x80093E74`, `0x80094348`, `0x8009711C`,
   `0x800EC6EC`, and `0x800ECE04`; the external generated snapshot changed
   12 references in three files and has no stale references for that batch.
   Session 2827 closed `0x8016D000..0x8016F000`: the selector changed zero
   references in zero files, and the independent generated-tree placeholder
   scan was empty. No companion candidates were selected; ambiguous/data
   entries remain preserved. No build or game soak was needed. Continue with
   the next bounded interval `0x8016F000..0x80171000`. Session 2828 closed
   that interval: the selector changed zero references in zero files, and the
   independent generated-tree placeholder scan was empty. No companion
   candidates were selected; ambiguous/data entries remain preserved. No
   build or game soak was needed. Continue with the next bounded interval
   `0x80171000..0x80173000`. Session 2829 closed that interval: the
   selector changed zero references in zero files, and the independent
   generated-tree placeholder scan was empty. No companion candidates were
   selected; ambiguous/data entries remain preserved. No build or game soak
   was needed. Session 2830 closed `0x80173000..0x80175000`: the selector
   changed zero references in zero files, and the independent generated-tree
   placeholder scan was empty. No companion candidates were selected;
   ambiguous/data entries remain preserved. No build or game soak was needed.
   Continue with `0x80175000..0x80177000`; that interval is already
   synchronized, so select the next explicitly source-backed short data-gap
   batch and preserve callable-ambiguous entries.

Session 2840 pivoted from the pre-title M5 post-dispatch rerun to the required
generated-symbol sweep because the queued recipe exited at launch (`rc=127`).
Three companion records explicitly classified as short non-callable gaps
(`0x800186D8`, `0x80019808`, and `0x80024878`) were renamed to mechanical
`data_gap_*` names in the regeneration-safe selector and companion map; the
external generated snapshot has three new-name references per address and no
stale placeholder references. This is symbol clarity only, not M5 evidence.

Session 2841 continued the source-backed batch with `0x80041EEC` and
`0x800457CC`; six generated references changed in four files and the
independent scan found no stale placeholders. Preserve
`fake_func_8004661C` as callable-ambiguous and continue with the next
explicitly classified short data-gap record.

4. **M5 SP-yield lifecycle validation — parked pending a new route angle.** The
   generated-target build boundary is clear, but the qualified driver still
   stalls before the target phases. Preserve the lifecycle change; do not infer
   task interruption or audio progress from the reset alone.

Historical generated-symbol sweep route note: M5 Step 1
   route note).** M5 Step 1
   input-recipe repair is now exhausted at this discriminator: boot-time
   probe keys, phase-relative probe keys, and the existing autopilot all
   failed to move the qualified port arms beyond VI 640 in this iteration.
   Audit `0x8011D000..0x8011F000`, preserving ambiguous/data entries and
   applying only source-backed names. The `0x80113000..0x80115000` census
   found one ambiguous-or-fake candidate, selected zero renames, and found
   zero generated placeholder references.
   Session 2779 closed `0x80115000..0x80117000`: the bounded selector
   selected zero references, and the independent generated-tree scan found no
   placeholder function symbols in the interval. Session 2780 closed
   `0x80117000..0x80119000`: the companion selector found no candidates and
   the corrected independent symbol inventory found zero placeholder
   definitions in the interval. Session 2781 closed
   `0x80119000..0x8011B000`: three ambiguous-or-fake candidates were
   preserved, the selector changed zero references, and the corrected
   independent symbol inventory found zero placeholder definitions. Session
   2782 closed `0x8011B000..0x8011D000`: no candidates were found, the
   selector changed zero references, and the independent symbol inventory
   found zero placeholder definitions. Continue with
   `0x8011D000..0x8011F000`: the selector changed zero references in zero
   files, and the independent generated-tree scan found no placeholder
   definitions or references in the interval. Session 2784 applied 14
   source-backed level-handler renames (`lv2` through `lvj`) at
   `0x80101CCC..0x80109618`, changing 42 generated references in 8 files;
   the companion comments explicitly identify each function. Continue with
   `0x80121000..0x80123000`. Session 2785 closed that interval: the selector
   changed zero references in zero files, and the independent generated-tree
   scan found no placeholder definitions or references. Session 2786 closed
   `0x80123000..0x80125000`: the selector changed zero references in zero
   files, and the independent generated-tree scan found no placeholder
   definitions or references. Session 2787 closed
   `0x80125000..0x80127000`: the selector changed zero references in zero
   files, and the independent generated-tree scan found no placeholder
   definitions or references. Session 2788 closed
   `0x80127000..0x80129000`: the selector changed zero references in zero
   files, two companion entries were preserved as ambiguous/fake, and the
   independent generated-tree scan found no placeholder definitions or
   references. Session 2789 closed `0x80129000..0x8012B000`: the selector
   changed zero references in zero files and the independent generated-tree
   scan found no placeholder definitions in the interval. Continue with
   `0x8012B000..0x8012D000`: six companion entries were already
   synchronized, the selector changed zero references in zero files, and the
   independent generated-tree scan found no placeholder definitions or
   references. Session 2793 closed `0x8012D000..0x8012F000`: 18 companion
   entries were already synchronized, the selector changed zero references
   in zero files, and the independent generated-tree scan found no
   placeholder definitions or references in the interval. Continue with
   `0x8012F000..0x80131000`: 31 companion entries were already
   synchronized; the selector changed zero references in zero files, and
   the independent generated-tree scan found zero placeholder definitions or
   references. Continue with `0x80131000..0x80133000`: 31 companion entries
   were already synchronized; the selector changed zero references in zero
   files, and the independent generated-tree scan found zero placeholder
   definitions or references. Session 2796 closed
   `0x80133000..0x80135000`: the selector changed zero references in zero
   files, and the independent generated-tree scan found zero placeholder
   definitions or references. Session 2797 closed `0x80135000..0x80137000`:
   two companion entries (`hmpFile` and `gDoublyLinkedNodePool12`) were
   already synchronized, the selector changed zero references in zero files,
   and the independent generated-tree scan found zero placeholder definitions
   or references. Session 2798 repaired the prior 14-entry level-handler
   batch's fake/data collisions: the entries at `0x80101CCC`, `0x80102A98`,
   `0x8010357C`, `0x80103D08`, `0x80104208`, `0x801044D8`, `0x80105B54`,
   `0x8010619C`, `0x80106BE8`, `0x8010721C`, `0x80107EA4`, `0x80108B8C`,
   `0x80109428`, and `0x80109618` now have mechanical `data_gap_*` names;
   the real following functions retain their semantic names. The generated
   target has zero duplicate definitions. Continue with
   `0x80137000..0x80139000` after full-target M5 validation.

4. **M5 Step 1 phase-qualified pair — parked pending a new input angle.** The M5
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
   `0x8010B000..0x8010D000` is now synchronized: all six semantic
   candidates were already synchronized and no generated placeholder remained
   in the interval; ambiguous/data entries were preserved. Session 2772 also
   closed `0x8010D000..0x8010F000`: two candidates were already synchronized
   and five ambiguous/fake entries were preserved, with zero generated
   references selected. Session 2773 closed `0x8010F000..0x80111000`: 15
   semantic candidates were already synchronized and 17 ambiguous/fake entries
   were preserved, with zero generated references selected. Continue with the
   next bounded interval after this region, preserving ambiguous/data entries.

5. **M5 CPU-side MORT publication — unresolved, callback edge closed.** The
   corrected `+0x190` callback edge is `dmaVoiceSampleAndSignal`; its
   legitimate destination is the voice ring and its ordering edge is the
   completion queue. `+0x194` is the sample source. Do not repeat this edge or
   add a runtime watch until a new legitimate AI destination and order are
   named. The speech-loader surface is now closed as service-only; the
   remaining publication boundary is unresolved.

6. **External retail-entry boundary — parked revisit.** Only return with a
   genuinely new, phase-qualified oracle discriminator. The oracle's whole-
   RDRAM positive control is mandatory; it currently does not drive missions.

7. **M4 accumulator origin — parked.** The absolute-DMEM path is localized to
   its known producer, selector state, and indirect consumer. Pointer-relative
   `0xB00/B02/B04` matches are unrelated fields. The dynamic producer-slot /
   consumer-index equality remains unresolved; broad range watches are not a
   substitute.

8. **M3 crash work — parked.** Resume only as a complete idiom-class audit
   with a named discriminator. Passive recurrence belongs in the soak queue.

9. **M5 image task contract and hangar visual artifact — parked.** Implement
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
- s2778: the generated-symbol interval `0x80113000..0x80115000` was closed;
  one ambiguous-or-fake candidate was preserved, zero source-backed renames
  were selected, and an independent generated-tree scan found zero
  placeholders. The next interval is `0x80115000..0x80117000`.
- s2779: the generated-symbol interval `0x80115000..0x80117000` was closed;
  the selector changed zero references in zero files, and the independent
  scan found no placeholder function symbols. No build was needed; continue
  after `0x80117000`.
- s2780: the generated-symbol interval `0x80117000..0x80119000` had no
  source-backed companion candidates and zero generated placeholder symbols;
  the bounded selector changed zero references and no build was needed. The
  next interval begins after `0x80119000`.
- s2782: the generated-symbol interval `0x8011B000..0x8011D000` had no
  source-backed candidates; the selector changed zero references and the
  independent scan found zero placeholders. The interval was closed without
  a build.
- s2783: the generated-symbol interval `0x8011D000..0x8011F000` selected zero
  renames and the independent generated-tree scan found no in-range
  placeholders. The interval is closed; continue with `0x8011F000..0x80121000`.
- s2785: the generated-symbol interval `0x80121000..0x80123000` selected zero
  renames and the independent generated-tree scan found no in-range
  placeholders or references. The interval is closed without a build; the
  next interval is `0x80123000..0x80125000`.
- s2787: the generated-symbol interval `0x80125000..0x80127000` selected zero
  renames and the independent generated-tree scan found no in-range
  placeholders or references. The interval is closed without a build; the
  next interval is `0x80127000..0x80129000`.
- s2781: the generated-symbol interval `0x80119000..0x8011B000` had three
  ambiguous-or-fake candidates. The regeneration-safe selector changed zero
  generated references, and a corrected independent generated-tree symbol
  inventory found zero placeholder definitions in the interval. The interval
  is closed without inventing names; the next interval begins after
  `0x8011B000`.
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
- s2771: the generated-symbol interval `0x8010B000..0x8010D000` had six
  semantic companion candidates, all already synchronized. The remaining
  data/ambiguous candidates were preserved; an independent generated-tree
  scan found zero placeholder hits in the interval. The regeneration-safe
  selection changed zero references and no build was needed. The next interval
  is `0x8010D000..0x8010F000`.
- s2772: the generated-symbol interval `0x8010D000..0x8010F000` had two
  already-synchronized candidates and five ambiguous/fake candidates. The
  regeneration-safe selection changed zero references in zero files; no
  generated placeholder was selected. The next interval is
  `0x8010F000..0x80111000`.
- s2773: the generated-symbol interval `0x8010F000..0x80111000` had 15
  already-synchronized semantic candidates and 17 ambiguous/fake entries.
  Zero generated references were selected; an independent placeholder scan was
  empty. The interval is closed without inventing names; the next rename
  interval begins after `0x80111000`.
- s2774: the retail oracle whole-RDRAM control passed, while both same-build
  AUTOPILOT arms stalled at VI 640 under both the original and eleven-Start
  schedules. Target-phase audio/PCM rows are invalid; no M5 hypothesis was
  selected, and the next step is input-recipe repair.
- s2775: the retail oracle whole-RDRAM control passed and reached title plus
  hangar, but the phase-gated port driver still did not launch phase-relative
  probe keys; both image and silent arms stalled at VI 640/origin `0x0066A500`.
  Image/silent dispatch controls were positive, while target-phase rows were
  invalid. The next recipe must explicitly wire `PROBE_KEYS` into
  `tools/probe.sh` with `PROBE_KEYS_FROM_PHASE=1`.
Exact counts, evidence tables, and rejected hypotheses are authoritative in
the corresponding scratch directories and ledger entries.
