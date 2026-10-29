# G1(d) objective-response reconciliation

Session 6656, 2026-10-29. Offline analysis only; no build or game launch.
The appendix is reproduced by `python3 tools/g1_objective_evidence.py --check`.
It streams the saved plain/gzip logs and preserves decompressed line numbers,
route witnesses, explicit width epochs, counter records, firing controls,
writer calls, Boolean dumps and result-mode requests separately.

| Level | Response evidence | Success/failure meaning and coverage verdict |
| --- | --- | --- |
| 0 | Legacy s5843/s5844/s5845: lv0 caller observed; c1 pre-states 0..3 / 0..12 / 0..16, TELE records 0 / 10 / 10. | Named counter activity under the legacy route; single-source, cross-run. No forced-selector ctl/tele logs. First missing forced-route response. |
| 1 | id13 gets 0..2 ctl versus 0..4 tele; ctl also has snapshots of id10 and id13, tele has no snapshot records. | Saved arms have different instrument evidence; do not assume identical builds. Counter13 meaning and hit causality unresolved. Earlier ledger maxima of 4 in both arms do not describe the currently saved first epochs. |
| 2 | TELE fires; writer call records only. | No named counter response or controlled null. |
| 3 | TELE fires; writer call records only. | No named counter response or controlled null. |
| 4 | id15 0>1>2>3 in both arms; ctl additionally id5 0>1. | Shared baseline movement. No tele-specific objective response proved. Both arms request result mode a0=2. |
| 5 | tele id2 0>1, ctl id2 remains observed 0; id4 observed 0 in both. | Historical failure-counter interpretation; static lv5 tests id2>=4 through Bit4, id4>=9 separately. Does not prove a successful objective response. |
| 6 | TELE fires; no snapshot value changes; heartbeat occurs in both arms. | Inconclusive: hook execution is not a positive control for detecting changes. Neither full-table coverage nor a valid null is established. |
| 7 | tele id2 0>2>3>0, absent ctl; id1 moves in both. | Named response, single-source; id2 semantics are not established for this level. Three a0=1 death requests precede cleanup in both arms. The lv0 id2 threshold does not apply to lvl7. |
| 8 | tele id6 0>1>2>3>4, ctl get(id6)=0. | Named response, single-source; id6 purpose remains unclassified. Identical Boolean gate sets and a0=2 requests in both arms; no hit-driven end gate. Reset 4>0 is outside the first flight epoch. |
| 9 | id1/id3/id5 each 0>1 in both arms. | Baseline response; no tele-specific counter transition. The old extra id3 transition came from a later epoch. Both arms request a0=2. |
| 10–18 | No g1_lvlNctl/tele logs in the saved pair set. | Unknown response coverage; existing endurance/framebuffer evidence is a separate criterion. |

No level is promoted to fully VERIFIED by this reconciliation. Recorded
activity and causal objective success are different claims. Missing pair
logs are not evidence that no other historical run exercised the level.

## Instrument and semantic limits

The positive controls for this parser are the actual lvl7 id2 and lvl8 id6
value changes, with their silent ctl counterparts, and lvl9's matching
counter-id sets. A synthetic pre-flight/flight/post-flight sequence verifies
scope exclusion. All 18 pair logs have matching B40 selectors. These checks
pass; no null is promoted from a heartbeat.

The current saved logs are not immutable historical arms: recipes reused
`g1_lvlNctl/tele` paths. In particular, lvl1 ctl contains objsnap records
while tele does not, although s5946 predates that instrument. Preserve the
current file/line evidence instead of assuming a historical build pairing.
The tool intentionally does not convert call totals into counter writes.
The old `g1_d_compare.sh` remains a run-lifetime activity summary and should
not be used as a G1(d) verdict.

Two inspected sources constrain interpretation: saved guest-counter/request
logs and static generated instruction sequences. They are complementary,
not an independent retail behavioral oracle. Response causality remains
single-source. `docs/M6-PHASE-MACHINE.md` describes the a0=1 lives-loss path;
the saved lvl7 arms each show three such requests before cleanup. An a0=2
request alone does not prove success: s5847 observed it from lvl0's failure
arm. A shared request in ctl and tele cannot establish hit causality.

Static source locations in the companion RecompiledFuncs tree:

- lv0: funcs_43.c, guest 0x801011B4..0x80101224 reads ids 2/3/10;
  0x80101834 reads id1 (threshold 21). Legacy `[cco]` logs independently
  identify the executing lv0 callback; `[ctr1]` c fields are pre-store reads.
- lv5: funcs_45.c, guest 0x80104168 reads id2 (threshold 4),
  0x80104190 calls setHudEnableBit4; 0x801041BC reads id4 (threshold 9).
  Do not transplant lv0's threshold 3 or its semantic name to every level.
- lv7: funcs_45.c, guest 0x8010465C/0x801046A8/0x801046F4 read
  ids 0x14/0x1E/0x28; 0x801049D0 reads 0x63. All are outside ids 1–15,
  the only slots the old get/snapshot instruments cover. Thus a silent
  fifteen-slot monitor cannot establish that a level's objective state
  did not move. This is a single-source static scope finding.
- lv8: funcs_46.c, guest 0x80104BF8/0x80104C3C read ids 3/5;
  neither alone identifies the role of the observed id6 transition.

The snapshot hooks also have separate static histories in the three
accessors and a run-lifetime budget. Neither heartbeat nor a TELE line
proves that every relevant counter write would have been observed.
No runtime, patch, mitigation, default or mission-win change was made.

## Next discriminating unit

First missing forced-route witness: level 0, counter1. Use the existing
ROGUESQ_TELE_BOLT lever and forced-selector recipe with LEVEL=0,
ROGUESQ_FORCE_UNLOCK=0, ROGUESQ_FORCE_SAVE_MISSION=0,
ROGUESQ_NO_SAVE_WRITE=1. Confirm B40=0 and lv0 callback identity.
PROBE_PHASE_WIDTH=512 is only the autopilot route gate: the hangar is also
512 wide. The measurement must start at the explicit first flight origin
0x00690400/0x00620400 after selection and stop on exit from that flight.

Implement one phase-scoped diagnostic adapter around the existing TELE
lever, with off/on/off windows in one run and a joined before/after witness
of the DAT counter1 write, victim identity and firing marker. Capture actual
writes (including a naturally changing counter as the value-detector
positive control), not additional call totals. Classify counter2 separately.
No aim/steer tuning, forced win, mission progression or repeat hold is needed.
Stop well below an objective end threshold; a nonzero response suffices.
NEXT.md carries the hypotheses, exact base recipe and build commands.

## Generated evidence appendix

# G1 objective-response saved-evidence table

Generated by `python3 tools/g1_objective_evidence.py --check`.

Scope: first explicit `[phase] vi_width=512` at origin 0x00690400
or 0x00620400, through the next width transition (exclusive).
L numbers refer to decompressed log lines. No ordinal or event VI is
invented. Scope is a width epoch, not proof of uninterrupted flight.
A missing epoch is unknown. Later re-entries are excluded.

TELE records are capped at 10 by the instrument: this is a firing
control, not a hit total or a damage receipt. SEGIN is geometric
intersection, not independently confirmed damage. Writer records are
rate-limited call activity, not successful writes or objective progress.
Snapshot accessors have separate static histories; repeated/discontinuous
records are not a single authoritative counter chain. The snapshot
instruments cover only ids 1–15 and have run-lifetime 400-record budgets.
Heartbeat proves execution only; it is not a value-detection control.
These are animating cross-run arms: differences are descriptive, not
causal A/B proof. All response claims remain single-source.

| Level | ctl TELE / tele TELE | ctl values | tele values |
| --- | --- | --- | --- |
| 0 | unknown | unknown (missing log or explicit flight scope) | unknown (missing log or explicit flight scope) |
| 1 | 0 / 10 | objsnap id=10: 0>1@L298385, 1>2@L310547, 2>3@L310719, 3>4@L311591, 4>5@L311726, 5>6@L318548; objsnap id=13: 0>1@L364935, 1>2@L366329; get id=13: 0@L286262, 1@L364936, 2@L366330 | get id=13: 0@L269114, 1@L347737, 2@L349284, 3@L370238, 4@L437095 |
| 2 | 0 / 10 | no value-change records (not a controlled null) | no value-change records (not a controlled null) |
| 3 | 0 / 10 | no value-change records (not a controlled null) | no value-change records (not a controlled null) |
| 4 | 0 / 10 | objsnap id=5: 0>1@L300443; objsnap id=15: 0>1@L280080, 1>2@L304519, 2>3@L307860; get id=15: 0@L227633, 1@L280130, 2@L304542, 3@L307861 | objsnap id=15: 0>1@L251617, 1>2@L258815, 2>3@L266776; get id=15: 0@L225894, 1@L251674, 2@L258839, 3@L266777 |
| 5 | 0 / 10 | get id=2: 0@L217659; get id=4: 0@L217660 | objsnap id=2: 0>1@L257171; get id=2: 0@L218059, 1@L257172; get id=4: 0@L218060 |
| 6 | 0 / 10 | no value-change records (not a controlled null) | no value-change records (not a controlled null) |
| 7 | 0 / 10 | objsnap id=1: 0>4@L296246, 4>0@L301309 | objsnap id=1: 0>4@L296700, 4>0@L300362, 0>4@L302901, 4>0@L307195, 0>4@L309902, 4>0@L313189, 0>4@L319027, 4>0@L321118, … (22 records); objsnap id=2: 0>2@L354462, 2>3@L354486, 3>0@L354644 |
| 8 | 0 / 10 | get id=3: 0@L282426; get id=5: 0@L282427; get id=6: 0@L445022 | objsnap id=6: 0>1@L341130, 1>2@L355878, 2>3@L356936, 3>4@L395069; get id=3: 0@L279340; get id=5: 0@L279341; get id=6: 4@L434200 |
| 9 | 0 / 10 | objsnap id=1: 0>1@L254489; objsnap id=3: 0>1@L318276; objsnap id=5: 0>1@L447764; get id=5: 0@L241821, 1@L447765 | objsnap id=1: 0>1@L254919; objsnap id=3: 0>1@L305374; objsnap id=5: 0>1@L387822; get id=5: 0@L242124, 1@L387823 |
| 10 | unknown | unknown (missing log or explicit flight scope) | unknown (missing log or explicit flight scope) |
| 11 | unknown | unknown (missing log or explicit flight scope) | unknown (missing log or explicit flight scope) |
| 12 | unknown | unknown (missing log or explicit flight scope) | unknown (missing log or explicit flight scope) |
| 13 | unknown | unknown (missing log or explicit flight scope) | unknown (missing log or explicit flight scope) |
| 14 | unknown | unknown (missing log or explicit flight scope) | unknown (missing log or explicit flight scope) |
| 15 | unknown | unknown (missing log or explicit flight scope) | unknown (missing log or explicit flight scope) |
| 16 | unknown | unknown (missing log or explicit flight scope) | unknown (missing log or explicit flight scope) |
| 17 | unknown | unknown (missing log or explicit flight scope) | unknown (missing log or explicit flight scope) |
| 18 | unknown | unknown (missing log or explicit flight scope) | unknown (missing log or explicit flight scope) |

## Level 1 provenance and separate gate evidence

- ctl: `scratch/agent/m6/g1_lvl1ctl/run.log.gz`
  Selector B40 witnesses: [(114822, 1)]; scope start (286162, '[phase] vi_width=512 (was 640) origin=0x00690400 at 82.9s update_screen #4914'); stop EOF.
  TELE lines []; SEGIN lines [297379, 297450, 297935, 297981, 298006, 298268, 298323, 301537, 301628, 302033]; heartbeat [].
  Writer call records: applyDatObjectiveTriggerEffect=16, datItemSetObjectiveBooleanCount=4, executeActorType1Effect=120, updateNpcEffectIntensity=21.
  Transition requests: none.
  Cleanup: []; Boolean gate dumps: [].
- tele: `scratch/agent/m6/g1_lvl1tele/run.log.gz`
  Selector B40 witnesses: [(124422, 1)]; scope start (269008, '[phase] vi_width=512 (was 640) origin=0x00690400 at 84.4s update_screen #5001'); stop EOF.
  TELE lines [269731, 269775, 270613, 270617, 271708, 271712, 272488, 273786, 273789, 274169]; SEGIN lines [269182, 269268, 269734, 269777, 269964, 270616, 270620, 270644, 271711, 271714]; heartbeat [].
  Writer call records: applyDatObjectiveTriggerEffect=24, datItemSetObjectiveBooleanCount=22, executeActorType1Effect=120, updateNpcEffectIntensity=48.
  Transition requests: none.
  Cleanup: []; Boolean gate dumps: [].

## Level 2 provenance and separate gate evidence

- ctl: `scratch/agent/m6/g1_lvl2ctl/run.log.gz`
  Selector B40 witnesses: [(123819, 2)]; scope start (241013, '[phase] vi_width=512 (was 640) origin=0x00690400 at 80.9s update_screen #4789'); stop EOF.
  TELE lines []; SEGIN lines [245458, 245671, 245674, 245676, 245677, 245678, 245711, 253536, 253662, 253717]; heartbeat [].
  Writer call records: applyDatObjectiveTriggerEffect=114, datItemSetObjectiveBooleanCount=4, executeActorType1Effect=120, updateNpcEffectIntensity=20.
  Transition requests: none.
  Cleanup: []; Boolean gate dumps: [].
- tele: `scratch/agent/m6/g1_lvl2tele/run.log.gz`
  Selector B40 witnesses: [(124615, 2)]; scope start (241427, '[phase] vi_width=512 (was 640) origin=0x00690400 at 80.9s update_screen #4775'); stop EOF.
  TELE lines [244511, 244527, 245485, 253972, 254334, 254338, 254341, 254904, 254915, 254925]; SEGIN lines [244513, 244529, 244647, 244777, 245382, 245440, 245487, 245512, 253807, 253974]; heartbeat [].
  Writer call records: applyDatObjectiveTriggerEffect=42, datItemSetObjectiveBooleanCount=17, executeActorType1Effect=120, updateNpcEffectIntensity=16.
  Transition requests: a0=1: 1 records, first L319088 ph=0 vi=10949.
  Cleanup: []; Boolean gate dumps: [].

## Level 3 provenance and separate gate evidence

- ctl: `scratch/agent/m6/g1_lvl3ctl/run.log.gz`
  Selector B40 witnesses: [(124019, 3)]; scope start (262912, '[phase] vi_width=512 (was 640) origin=0x00690400 at 86.3s update_screen #5116'); stop EOF.
  TELE lines []; SEGIN lines [273567, 273580, 273584, 273586, 273590, 273592, 273607, 273609, 273611, 273613]; heartbeat [].
  Writer call records: applyDatObjectiveTriggerEffect=44, executeActorType1Effect=120, updateNpcEffectIntensity=22.
  Transition requests: none.
  Cleanup: []; Boolean gate dumps: [].
- tele: `scratch/agent/m6/g1_lvl3tele/run.log.gz`
  Selector B40 witnesses: [(124167, 3)]; scope start (262380, '[phase] vi_width=512 (was 640) origin=0x00690400 at 86.1s update_screen #5102'); stop EOF.
  TELE lines [366637, 366652, 368640, 369044, 369440, 369699, 369876, 370255, 370523, 374319]; SEGIN lines [273080, 273093, 273095, 273097, 273100, 273103, 273117, 273119, 273123, 273125]; heartbeat [].
  Writer call records: applyDatObjectiveTriggerEffect=20, datItemSetObjectiveBooleanCount=8, executeActorType1Effect=120, updateNpcEffectIntensity=18.
  Transition requests: a0=1: 1 records, first L402673 ph=0 vi=18117.
  Cleanup: []; Boolean gate dumps: [].

## Level 4 provenance and separate gate evidence

- ctl: `scratch/agent/m6/g1_lvl4ctl/run.log.gz`
  Selector B40 witnesses: [(125120, 4)]; scope start (227523, '[phase] vi_width=512 (was 640) origin=0x00690400 at 83.9s update_screen #4965'); stop (314011, '[phase] vi_width=640 (was 512) origin=0x00696100 at 208.4s update_screen #12436').
  TELE lines []; SEGIN lines [237937, 237939, 237940, 237941, 237942, 237943, 237945, 237946, 237947, 237948]; heartbeat [].
  Writer call records: applyDatObjectiveTriggerEffect=2, datItemSetObjectiveBooleanCount=7, executeActorType1Effect=120, updateNpcEffectIntensity=19.
  Transition requests: a0=2: 1 records, first L307973 ph=0 vi=11609.
  Cleanup: [(309185, '[mend] fn=endMissionCleanup n=1 ra=00000000 flags=00000040 phase=00000006 w1=00000000 w2=00000000 vi=11771')]; Boolean gate dumps: [(307878, '[hudbit4dump] #1 bools: 1=31 2=1 5=1 6=1 7=1 A=1 B=1 1F=1 ')].
- tele: `scratch/agent/m6/g1_lvl4tele/run.log.gz`
  Selector B40 witnesses: [(125115, 4)]; scope start (225789, '[phase] vi_width=512 (was 640) origin=0x00690400 at 82.5s update_screen #4887'); stop (272907, '[phase] vi_width=640 (was 512) origin=0x00696100 at 150.9s update_screen #8987').
  TELE lines [236964, 236981, 237699, 238483, 238485, 238498, 238773, 238777, 238781, 238996]; SEGIN lines [236240, 236242, 236243, 236244, 236245, 236246, 236248, 236249, 236250, 236251]; heartbeat [].
  Writer call records: applyDatObjectiveTriggerEffect=2, datItemSetObjectiveBooleanCount=3, executeActorType1Effect=120, updateNpcEffectIntensity=11.
  Transition requests: a0=2: 1 records, first L266899 ph=0 vi=8143.
  Cleanup: [(268064, '[mend] fn=endMissionCleanup n=1 ra=00000000 flags=00000040 phase=00000006 w1=00000000 w2=00000000 vi=8322')]; Boolean gate dumps: [(266794, '[hudbit4dump] #1 bools: 1=31 2=1 5=1 6=1 7=1 1F=1 ')].

## Level 5 provenance and separate gate evidence

- ctl: `scratch/agent/m6/g1_lvl5ctl/run.log.gz`
  Selector B40 witnesses: [(124371, 5)]; scope start (217556, '[phase] vi_width=512 (was 640) origin=0x00690400 at 76.7s update_screen #4535'); stop EOF.
  TELE lines []; SEGIN lines [241246, 241275, 242161, 242498, 242547, 242548, 242576, 242661, 242685, 242741]; heartbeat [].
  Writer call records: applyDatObjectiveTriggerEffect=8, datItemSetObjectiveBooleanCount=4, executeActorType1Effect=120, updateNpcEffectIntensity=11.
  Transition requests: none.
  Cleanup: []; Boolean gate dumps: [].
- tele: `scratch/agent/m6/g1_lvl5tele/run.log.gz`
  Selector B40 witnesses: [(124494, 5)]; scope start (217947, '[phase] vi_width=512 (was 640) origin=0x00690400 at 76.7s update_screen #4537'); stop EOF.
  TELE lines [241630, 242772, 243014, 243475, 244043, 244149, 244580, 244590, 244899, 245639]; SEGIN lines [241524, 241559, 241632, 242580, 242758, 242774, 242890, 242891, 242918, 243013]; heartbeat [].
  Writer call records: applyDatObjectiveTriggerEffect=2, datItemSetObjectiveBooleanCount=6, executeActorType1Effect=120, updateNpcEffectIntensity=10.
  Transition requests: none.
  Cleanup: []; Boolean gate dumps: [].

## Level 6 provenance and separate gate evidence

- ctl: `scratch/agent/m6/g1_lvl6ctl/run.log.gz`
  Selector B40 witnesses: [(124366, 6)]; scope start (286674, '[phase] vi_width=512 (was 640) origin=0x00690400 at 93.5s update_screen #5544'); stop (327004, '[phase] vi_width=640 (was 512) origin=0x00696100 at 150.9s update_screen #8990').
  TELE lines []; SEGIN lines [288373, 288375, 288684, 288686, 289387, 289389, 289690, 289692, 289975, 289977]; heartbeat [(298902, '[objsnap-t] hb ticks=1 s_k=0')].
  Writer call records: applyDatObjectiveTriggerEffect=30, datItemSetObjectiveBooleanCount=2, executeActorType1Effect=120, updateNpcEffectIntensity=1.
  Transition requests: a0=1: 1 records, first L298876 ph=0 vi=6494, a0=2: 1 records, first L318402 ph=0 vi=7970.
  Cleanup: [(322402, '[mend] fn=endMissionCleanup n=1 ra=00000000 flags=00000040 phase=00000006 w1=00000000 w2=00000000 vi=8354')]; Boolean gate dumps: [(318367, '[hudbit4dump] #1 bools: 40=1 41=1 42=1 ')].
- tele: `scratch/agent/m6/g1_lvl6tele/run.log.gz`
  Selector B40 witnesses: [(124131, 6)]; scope start (287007, '[phase] vi_width=512 (was 640) origin=0x00690400 at 93.4s update_screen #5541'); stop (395849, '[phase] vi_width=1024 (was 512) origin=0x00790400 at 246.8s update_screen #14749').
  TELE lines [289128, 289907, 290469, 290755, 291331, 291679, 292360, 293099, 293569, 294179]; SEGIN lines [288685, 288687, 289022, 289024, 289130, 289392, 289736, 289738, 289909, 289930]; heartbeat [(313475, '[objsnap-t] hb ticks=1 s_k=0')].
  Writer call records: applyDatObjectiveTriggerEffect=10, datItemSetObjectiveBooleanCount=8, executeActorType1Effect=120, updateNpcEffectIntensity=4.
  Transition requests: a0=1: 3 records, first L313449 ph=0 vi=7309.
  Cleanup: [(390451, '[mend] fn=endMissionCleanup n=1 ra=00000000 flags=00000140 phase=00000006 w1=00000000 w2=00000000 vi=14017')]; Boolean gate dumps: [].

## Level 7 provenance and separate gate evidence

- ctl: `scratch/agent/m6/g1_lvl7ctl/run.log.gz`
  Selector B40 witnesses: [(123927, 7)]; scope start (260412, '[phase] vi_width=512 (was 640) origin=0x00690400 at 84.8s update_screen #5030'); stop (365156, '[phase] vi_width=1024 (was 512) origin=0x00790400 at 250.8s update_screen #14991').
  TELE lines []; SEGIN lines [293021, 293023, 293024, 293026, 293028, 293080, 293082, 293769, 293875, 293965]; heartbeat [].
  Writer call records: applyDatObjectiveTriggerEffect=16, executeActorType1Effect=120.
  Transition requests: a0=1: 3 records, first L290753 ph=0 vi=7592.
  Cleanup: [(359843, '[mend] fn=endMissionCleanup n=1 ra=00000000 flags=00000140 phase=00000006 w1=00000000 w2=00000000 vi=14280')]; Boolean gate dumps: [].
- tele: `scratch/agent/m6/g1_lvl7tele/run.log.gz`
  Selector B40 witnesses: [(125029, 7)]; scope start (261523, '[phase] vi_width=512 (was 640) origin=0x00690400 at 85.2s update_screen #5048'); stop (387773, '[phase] vi_width=1024 (was 512) origin=0x00790400 at 267.3s update_screen #15971').
  TELE lines [291382, 291398, 291888, 292102, 292230, 292452, 292454, 292726, 292729, 292877]; SEGIN lines [291194, 291196, 291197, 291199, 291201, 291253, 291255, 291384, 291400, 291824]; heartbeat [].
  Writer call records: applyDatObjectiveTriggerEffect=112, datItemSetObjectiveBooleanCount=5, executeActorType1Effect=120.
  Transition requests: a0=1: 3 records, first L289005 ph=0 vi=7298.
  Cleanup: [(383098, '[mend] fn=endMissionCleanup n=1 ra=00000000 flags=00000140 phase=00000006 w1=00000000 w2=00000000 vi=15332')]; Boolean gate dumps: [].

## Level 8 provenance and separate gate evidence

- ctl: `scratch/agent/m6/g1_lvl8ctl/run.log.gz`
  Selector B40 witnesses: [(123374, 8)]; scope start (282317, '[phase] vi_width=512 (was 640) origin=0x00690400 at 97.5s update_screen #5774'); stop (449384, '[phase] vi_width=640 (was 512) origin=0x00696100 at 342.9s update_screen #20493').
  TELE lines []; SEGIN lines [293670, 294105, 294570, 295497, 296565, 296567, 296698, 296700, 296750, 296752]; heartbeat [].
  Writer call records: applyDatObjectiveTriggerEffect=11, executeActorType1Effect=120, updateNpcEffectIntensity=6.
  Transition requests: a0=2: 55 records, first L441576 ph=7 vi=19211.
  Cleanup: [(444993, '[mend] fn=endMissionCleanup n=1 ra=00000000 flags=0000014C phase=00000006 w1=00000000 w2=00000000 vi=19882')]; Boolean gate dumps: [(441531, '[hudbit4dump] #1 bools: 5=1 A=1 E=1 15=1 16=1 17=1 18=1 ')].
- tele: `scratch/agent/m6/g1_lvl8tele/run.log.gz`
  Selector B40 witnesses: [(121911, 8)]; scope start (279238, '[phase] vi_width=512 (was 640) origin=0x00690400 at 96.7s update_screen #5738'); stop (440195, '[phase] vi_width=640 (was 512) origin=0x00696100 at 334.9s update_screen #20023').
  TELE lines [293561, 293577, 294500, 294963, 294965, 295267, 295844, 295846, 295851, 295855]; SEGIN lines [292864, 292867, 292869, 292870, 292923, 292925, 292926, 292949, 292953, 292979]; heartbeat [].
  Writer call records: applyDatObjectiveTriggerEffect=11, datItemSetObjectiveBooleanCount=4, executeActorType1Effect=120, updateNpcEffectIntensity=6.
  Transition requests: a0=2: 55 records, first L430851 ph=7 vi=18671.
  Cleanup: [(434184, '[mend] fn=endMissionCleanup n=1 ra=00000000 flags=0000014C phase=00000006 w1=00000000 w2=00000000 vi=19207')]; Boolean gate dumps: [(430809, '[hudbit4dump] #1 bools: 5=1 A=1 E=1 15=1 16=1 17=1 18=1 ')].

## Level 9 provenance and separate gate evidence

- ctl: `scratch/agent/m6/g1_lvl9ctl/run.log.gz`
  Selector B40 witnesses: [(124862, 9)]; scope start (241704, '[phase] vi_width=512 (was 640) origin=0x00690400 at 76.4s update_screen #4514'); stop (456061, '[phase] vi_width=640 (was 512) origin=0x00696100 at 370.9s update_screen #22184').
  TELE lines []; SEGIN lines [253625, 253728, 254232, 254295, 254323, 254434, 254504, 254606, 254680, 254708]; heartbeat [].
  Writer call records: applyDatObjectiveTriggerEffect=2, datItemSetObjectiveBooleanCount=4, executeActorType1Effect=120, updateNpcEffectIntensity=4.
  Transition requests: a0=1: 1 records, first L383942 ph=0 vi=13356, a0=2: 1 records, first L447829 ph=0 vi=21152.
  Cleanup: [(451107, '[mend] fn=endMissionCleanup n=1 ra=00000000 flags=00000040 phase=00000006 w1=00000000 w2=00000000 vi=21506')]; Boolean gate dumps: [(447782, '[hudbit4dump] #1 bools: 6=1 E=1 F=1 18=1 19=1 1A=1 1B=1 1C=1 1D=1 1E=1 1F=1 20=1 ')].
- tele: `scratch/agent/m6/g1_lvl9tele/run.log.gz`
  Selector B40 witnesses: [(125003, 9)]; scope start (242009, '[phase] vi_width=512 (was 640) origin=0x00690400 at 76.4s update_screen #4520'); stop (394331, '[phase] vi_width=640 (was 512) origin=0x00696100 at 254.9s update_screen #15230').
  TELE lines [254137, 254681, 254921, 254926, 255062, 255075, 255274, 255449, 255460, 255600]; SEGIN lines [242203, 242251, 242255, 253909, 253992, 254064, 254140, 254176, 254367, 254447]; heartbeat [].
  Writer call records: applyDatObjectiveTriggerEffect=2, datItemSetObjectiveBooleanCount=10, executeActorType1Effect=120, updateNpcEffectIntensity=4.
  Transition requests: a0=1: 1 records, first L300535 ph=0 vi=8090, a0=2: 1 records, first L387876 ph=0 vi=14332.
  Cleanup: [(388838, '[mend] fn=endMissionCleanup n=1 ra=00000000 flags=00000040 phase=00000006 w1=00000000 w2=00000000 vi=14480')]; Boolean gate dumps: [(387839, '[hudbit4dump] #1 bools: 6=1 E=1 F=1 18=1 19=1 1A=1 1B=1 1C=1 1D=1 1E=1 1F=1 20=1 ')].

## Legacy level-0 evidence (separate route)

These runs use g1_fire.sh rather than the forced level-selector
recipe. Caller identity is recorded directly; do not silently
substitute them for missing g1_lvl0ctl/tele logs. `ctr1` logs
counter pre-state at setter entry, not the resulting write.

- `scratch/agent/m6/s5843/run.log.gz`: scope (204968, '[phase] vi_width=512 (was 640) origin=0x00690400 at 76.6s update_screen #4536') through EOF.
  Caller [(205075, 'lv0_checkComplexObjectives')]; TELE lines [].
  Counter pre-states (line, c1, c2, c10): [(223112, 0, 0, 0), (225841, 1, 0, 0), (284140, 2, 0, 0), (310577, 3, 0, 0)].
- `scratch/agent/m6/s5844/run.log.gz`: scope (205010, '[phase] vi_width=512 (was 640) origin=0x00690400 at 76.6s update_screen #4533') through EOF.
  Caller [(205112, 'lv0_checkComplexObjectives')]; TELE lines [278585, 278609, 278631, 278652, 278669, 279513, 279516, 279518, 279520, 282218].
  Counter pre-states (line, c1, c2, c10): [(223409, 0, 0, 0), (230212, 1, 0, 0), (278782, 2, 0, 0), (282595, 3, 0, 0), (282802, 4, 0, 0), (285819, 5, 0, 0), (286413, 6, 0, 0), (287964, 7, 0, 0), (288124, 8, 0, 0), (289914, 9, 0, 0), (290588, 10, 0, 0), (307048, 11, 0, 0), (310061, 12, 0, 0)].
- `scratch/agent/m6/s5845/run.log.gz`: scope (205604, '[phase] vi_width=512 (was 640) origin=0x00690400 at 77.1s update_screen #4563') through EOF.
  Caller [(205695, 'lv0_checkComplexObjectives')]; TELE lines [280306, 280330, 280352, 280373, 280390, 280704, 280708, 280711, 280713, 281100].
  Counter pre-states (line, c1, c2, c10): [(223724, 0, 0, 0), (230636, 1, 0, 0), (280503, 2, 0, 0), (280770, 3, 0, 0), (281469, 4, 0, 0), (284845, 5, 0, 0), (285331, 6, 0, 0), (287755, 7, 0, 0), (289576, 8, 0, 0), (289870, 9, 0, 0), (290009, 10, 0, 0), (292192, 11, 0, 0), (292395, 12, 0, 0), (308337, 13, 0, 0), (311458, 14, 0, 0), (314594, 15, 0, 0), (376801, 16, 1, 0)].
