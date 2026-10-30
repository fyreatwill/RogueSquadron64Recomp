# G1(d) objective-response reconciliation

Initial reconciliation: Session 6656, 2026-10-29, offline only.
Session 6657 adds the live level-0 response experiment below.
The appendix is reproduced by `python3 tools/g1_objective_evidence.py --check`.
It streams the saved plain/gzip logs and preserves decompressed line numbers,
route witnesses, explicit width epochs, counter records, firing controls,
writer calls, Boolean dumps and result-mode requests separately.

| Level | Response evidence | Success/failure meaning and coverage verdict |
| --- | --- | --- |
| 0 | s6657: forced selector B40=0 and lv0 callback; same-flight off/on/off counter1 0→2→13→13, 13 live readback changes, eight exact force/send/store joins. | Named counter1 hit response observed in one instrumented flight, supported by original ELF descriptor-to-counter stores. Dynamic evidence remains single-source; no win, progression, player-shot or retail-equivalence claim. |
| 1 | s6661: exact seq4 ordinary hit HP390→386, then seq6 one requested387 dose HP386→−1; death effect, actual id13 store0→1, callback readback four VI later. | Named friendly-loss response observed. Original ELF proves id13>=5 fails and friendlies=19−(40+13+41). Stopped at1, Boolean6=0; no success, retail-equivalence or fully VERIFIED claim. Dynamic chain remains single-source. |
| 2 | s6668: same-owned rescue01 ordinary HP2000→1990, one requested1991 dose HP1990→−1, original counter40 store0→1, callback memory and getter return1 four VI later. | Named friendly-loss response observed, single-flight dynamic evidence. Original ELF/DAT independently establish damage/death and failure ordering. SIGSTOP before failure flags109/101; no win, progression, retail-equivalence or fully VERIFIED claim. |
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

## Session 6657: forced-level-0 response

One bounded adapter and its validation experiment, 2026-10-29. Maintenance
threshold was not triggered (51,237 bytes). No new queued-soak verdicts.
`tools/apply_s6657_objective_response.py` persists the generated diagnostics
through the vendored fixup replay. The opt-in `ROGUESQ_OBJECTIVE_RESPONSE=1`
gates the existing TELE lever inside the first flight confirmed by B40=0,
lv0_checkComplexObjectives, width 512 and origin 0x690400/0x620400. Retail
defaults and ordinary TELE behavior stay unchanged. Seven known objective
store PCs record actual pre/post words; the callback independently reads
counters 1–3. Budgets belong to the flight and each off/on/off arm.

The first binary completed the windows, counter1 0→1→12→12, 99 forced
segments, 0 crash lines, 169.87 s wall. Its candidate-to-victim join was
WRONG: the slot contains a parent node, not the NPC payload. Reading
node+0x34 produced meaningless descriptor words. Do not use its victim or
legacy health fields as damage proof. Original ELF `lw s1,4(s5)` at
0x8006CBF8 and the already-correct s5886 send helper identify node+4 as the
NPC payload. The corrected binary records node, payload and payload+0x34
descriptor separately, retaining identity through actual writer registers.

Corrected run: `scratch/agent/m6/g1_lvl0s6657_response_v2/`, 167.87 s wall,
0 crash lines, screen-lock flag clear at launch. Forced selector is B40=0,
cursor 0; initMission and the lv0 callback both execute. Epoch starts at
VI 4672 (raw log L205649); callback entry is later than the first flight
VI, deliberately excluding initialization and the hangar.

| Arm | Flight-relative VI interval observed | TELE segments | Counter1 | Counter2/3 |
| --- | --- | ---: | --- | --- |
| Off | 0..1801 | 0 | 0→2 | 0/0 |
| On | 1802..4199 | 77 | 2→13 | 0/0 |
| Off | 4200..5402 (stop) | 0 | 13→13 | 0/0 |

Thirteen independent callback readback changes agree with the actual
counter1 stores, including the two off-arm baseline changes. These are
live value-detector controls, not heartbeats or synthetic marks. No null
about another level, other counters, or omitted writers is inferred.

Eight complete same-run joins have exact node/payload/descriptor identity
and ordering force < accepted hit SEND < actual counter1 write. All use
writer 0x8006594C in datItemSetObjectiveBooleanCount; each delta is +1.
The existing `[eff2] SEND` hook is after accepted intersection selection
at 0x8005D35C. It visibly fires in the on arm, so its run-lifetime budget
does not invalidate these positive records. It would not qualify a null.

| Force seq | VI at store | Age (VI) | Node | NPC payload | Descriptor | Counter1 | Raw lines force / SEND / store |
| --- | ---: | ---: | --- | --- | --- | --- | --- |
| 9 | 6496 | 7 | `8021b718` | `803519b0` | `8031c520` | 2→3 | 230681 / 230783 / 230824 |
| 17 | 6527 | 5 | `8021b6a0` | `80353ca0` | `803175a4` | 3→4 | 231134 / 231177 / 231215 |
| 24 | 6549 | 4 | `8021b22c` | `80356230` | `8031aa94` | 4→5 | 231432 / 231488 / 231513 |
| 31 | 6573 | 4 | `8021ac8c` | `80359880` | `8031c244` | 5→6 | 231736 / 231798 / 231822 |
| 44 | 6650 | 3 | `8021a9f8` | `8035a8d0` | `8031c338` | 6→7 | 232551 / 232599 / 232623 |
| 55 | 6939 | 6 | `8021ae30` | `803599b0` | `8031c614` | 7→8 | 234971 / 235013 / 235038 |
| 57 | 7035 | 2 | `8021a980` | `803594b0` | `80317698` | 8→9 | 235819 / 235842 / 235850 |
| 60 | 7612 | 2 | `8021a944` | `8035bbd0` | `8031c7fc` | 9→10 | 240619 / 240643 / 240651 |

For example seq24 forces shape 0x8021F850 with projectile 0x8035421C at
VI 6545; SEND names node 0x8021B22C and descriptor 0x8031AA94; the writer
at VI 6549 changes counter1 4→5 with s1=0x80356230 and s5=0x8021B22C.
The legacy shooter classifier calls this SEND N (NPC), not P. The lever
historically treats all bolts as w=0; this run does not establish a
player-shot-specific response or improve aim. Eight of eleven on-arm
counter changes have the complete logged triad; no claim is made for the
other three (force rows are limited to 64 per arm).

Original ELF independently fixes the static semantics: npcProbeDriod at
0x800CB858..0x800CB884 loads payload+0x34, then descriptor+0x70/+0x74 as
counter index/delta and calls the setter; the setter adds the delta and
stores at 0x8006594C. The separate trigger writer 0x80065A34 was observed
statically, not selected by this runtime witness. lv0 at 0x80101834 tests
counter1>=21; stop was c1=13, c2=c3=0 at VI 10074, below all configured
stop thresholds. No win or progression was poked or tested.

This selects H-response for named counter1 activity from forced-hit
victims. H-incidental-only is ruled out for these eight writes: they are
counter1 stores, not counter2, Boolean-only effects or bare call totals.
The observed chain plus original ELF supports the address/type meaning;
dynamic behavior is still one runtime source, not independent retail
behavior or a randomized causal estimate. Arm-rate differences are not
the proof. No level is promoted to fully VERIFIED here.

Validation: both builds succeeded; extracted C helper checks cover default
behavior, hangar exclusion, exact VI boundaries, parent/payload resolution,
register join, actual store/readback and stop. Parser checks accept a
measured triad and reject a deliberately mismatched descriptor. Adapter
reapplication is idempotent for all five files. The wrapper watches itself,
SIGKILLs its recipe process group at done (360 s hard timeout), refuses
reused output tags and records binary/source hashes for future runs.
Legacy HP samples are not used as evidence of damage or victim identity.

Reproduce the analysis without launching the game:

```sh
python3 tools/g1_objective_response_run.py s6657_response_v2 --analyze
```

This prints eight linked changes and thirteen readback changes. The raw
log, joined response.log/response.json and binary manifest stay under the
fresh run directory. Original ELF windows and helper controls are under
`scratch/agent/s6657_response/`. First-version evidence is retained under
`scratch/agent/m6/g1_lvl0s6657_response/`; it is a failed join control, not a
second independent behavioral source.

## Next discriminating unit

Level 1 remains the first level without a named forced-victim objective
response. Generalize this same adapter for a selected callback/level only
after checking lv1's counter/gate semantics in the original ELF. Keep the
same in-run windows, actual-store/readback controls and node→payload→
descriptor→hit-SEND join; never inherit lv0's counter1 or its stop limits.
Preserve ordinary TELE behavior, retail defaults and the owner's win /
progression / aim scope. NEXT.md carries the bounded unit and commands.

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

## Session 6659: level-1 adapter and diagnostic address correction

2026-10-30. Maintenance not triggered (52,392 bytes); no new soak verdicts.
The persistent adapter supports `ROGUESQ_OBJECTIVE_RESPONSE_LEVEL=0|1`
(default 0), a selected lv1 callback, all 128 count readbacks and Boolean6.
The runner accepts `--level 1`, preserves fresh evidence paths, and now kills
the recipe group immediately on a crash marker, before retries overwrite it.
Seven existing actual-store hooks remain. Analyzer reports relevant and
incidental exact-identity chains separately and records its own source hash.
All windows are within one selected flight; no cross-run rate comparison.

Original ELF at 0x80101BEC..0x80101C44 computes friendlies saved as
19-(count40+count13+count41). At 0x80101C60..0x80101C8C, id13>=5 sets
Bit4; Boolean6==1 separately sets Bit8/complete1. The probe stops at a
read-back id13>=3 or Boolean6, or the original 5400-VI/flight-exit bound.
These are loss semantics, not a successful objective-progress claim.
ELF disassembly and SHA are in `scratch/agent/s6659_response/`.

First flight, `scratch/agent/m6/g1_lvl1s6659_response/`, reached B40=1
and lv1 callback at VI5313, then crashed before TELE-on. One SIGSEGV,
37 crash-related lines; no completed epoch or changing-value control.
The handler names rs5857_hp+212, called by dealDamageToNpc+168 from
npcProbeDriod, host address 0x400319130 with rdram=0x300000000.
This is a diagnostic-address defect, not a new guest corruption finding.

ORIGIN: rs5857_hp forms MEM_W(int32_t(b), uint32_t(4*index)). C converts
the sum to unsigned 32-bit before the macro subtracts the 64-bit guest
base, giving physical_offset+0x100000000. The original MIPS health reader
0x800F20EC performs SLL/ADDU then a signed guest-address load; it does not
create that extra 4 GiB. The host diagnostic is the erroneous address
writer; a valid effective guest address can trigger it. No wild-value
skip or guest guard was added. The corrected persistent s5857 helper
first forms the complete uint32 address, then sign-extends it for MEM_W.
A same-input two-arm reproduction with the real memory macro returns
SIGSEGV (-11) for the old expression and passes for the corrected one:
index0, base0x80319130, old offset0x100319130 vs correct0x319130. Fixed
indices0..3 return7..10, and the immediate-health branch returns-2.
Evidence: health_control.c/json in the above diagnostic directory.

Corrected flight: `scratch/agent/m6/g1_lvl1s6659_response_v2/`, screen
unlocked, first launch, 176.59 s wall, epoch VI5271..10674, 0 crash lines.
The first failed flight is preserved; it is not an animated A/B arm.

| Arm | VI boundaries | Forces | Counter10 | ids13/40/41; Boolean6 |
| --- | --- | --- | --- | --- |
| off | 5271..7071 | 0 | 0→4 | 0; 0 |
| on | 7072..9471 | 25 | 4→8 | 0; 0 |
| off | 9472..10674 | 0 | 8 | 0; 0 |

Eight changing id10 readbacks and ten actual-store records (eight id10
increments, two id1 unchanged stores) control value detection in this same
flight. Exact on-arm chains:

| Force seq | node / NPC / descriptor | SEND line | Actual store | Readback |
| --- | --- | --- | --- | --- |
| 14, VI8656 | 8021b790 / 803586b0 / 8031929c | 300414, N, cls10 | 300420, VI8659, pc8006594c, id10 6→7 | 300445, VI8662, 6→7 |
| 17, VI8843 | 8021b754 / 803589e0 / 803191b0 | 301916, N, cls10 | 301922, VI8846, pc8006594c, id10 7→8 | 301952, VI8850, 7→8 |

The writer is datItemSetObjectiveBooleanCount. Register/live-descriptor
identity is a join, not an independently captured stack. N SENDs do not
prove player shots. Actual id10 changes select H-incidental under this
unit's direct-callback-used-counter definition; the lv1 callback reads
id13 and Boolean6, while friendlies-saved reads 13/40/41. This does not
prove id10 is irrelevant to every data-driven mission script. The zero
loss-counter values mean those named responses remain unexercised here;
they are not proof of broken objective logic or a universal null. Dynamic
causality is single-source; ELF semantics independently constrain meaning,
not retail behavioral equivalence. No win, progression or aim test.

Validation: both builds passed; helper controls cover selected callback,
VI boundaries, readbacks and early stops; final parser controls reject
wrong NPC, missing SEND and missing changing readback, and separate id10
incidental chains; all six live fixup replay checks are stable. Final
analyzer hash is in response.json (the launch manifest preserves its
pre-analysis-edit source hash). No lib/ edit or default change.
Next: target a descriptor whose documented loss-counter field is13/40/41
and stop at the first named loss response, below failure thresholds.


## s6660: descriptor-targeted level-1 hits stay above the death gate

One build and one retail-settings selected-level1 flight, screen unlocked,
175.61 s wall, epoch VI5234..10634, off/on/off at5234/7034/9434. Zero
crash lines, no win/progression, no library or default changes. The persistent
adapter now selects actual descriptor counter13/40/41 with nonzero delta in
either +70/+74 or +80/+84 pair, excludes Boolean6 setters, and records live
slots, eligibility, exact projectile SEND identity, stores and readbacks.
Original ELF initNpcSlotList allocates0x4000 bytes for2048 eight-byte entries;
80130BB4 is the free-list head, not the capacity. Census every300 VI is a
sample, not exhaustive lifetime coverage. Candidate logs cap at4096 rows
per arm (all three budgets reached); unseen later candidates remain unknown.

The same-run mark-all control records id10 candidates in every arm (unique
identities3/1/2); six actual changing id10 readbacks independently control
value detection. Named eligible candidates include id13 and40 with c1f=0,
so the old c1f-only lever excluded them. Eight unique named identities appear
in both sampled live and eligible candidate populations in each arm. The
census's45–46 selected slot entries are aliases, not45 distinct victims.

All46 force records survive the log budget. Exact node/NPC/descriptor plus
projectile/sequence joins find23 SENDs, all in on:14 to node8021b358,
NPC8035ab5c, descriptor8031b278 (counter40), and9 to node8021b628,
NPC8035b35c, descriptor80319af4 (counter13). There are no13/40/41 stores or
changes and Boolean6 stays0. id10 goes0→5→6→6 (five off changes, one on).
This is the bounded H-effect observation: accepted relevant hits did not
reach the descriptor writer in the measured flight. It is not broken
objective logic or a level VERIFIED result.

The boring limit is damage dose: on-arm health samples are14 calls on
actor80362000,999→859, and9 on actor8035d3a0,400→322. Both remain positive.
The latter actor also appears at node8021b628+0x10 in the earlier ctx41
snapshot. These health records have force_seq=0: the old damage join does
not resolve actor subobjects, so per-hit parent attribution remains
single-source temporal/layout evidence, not a completed force→damage join.
Independent original ELF npcGroundTransportUpdate at800DF830 loads the
health actor from NPC+0x38, takes damage from message+6, calls800F2120,
then bgtz at800DF840 skips to800DF928 while health remains positive.
Only the death branch loads the descriptor pairs and calls80065914 at
800DF8C8. Original dealDamageToNpc subtracts the requested damage at
800F2140/800F2150 and returns remaining health. Thus nonlethal hits are
not expected to increment these destruction counters. No mitigation added.

Artifacts: scratch/agent/m6/g1_lvl1s6660_targeted/{manifest.json,run.log,
response.json,response.log}; scratch/agent/s6660_targeted/chains.tsv contains
all46 force→SEND rows (empty store/readback columns are deliberate).
Original ELF windows, helper controls and six-file replay hashes are in the
same scratch directory. Analyzer was tightened after launch; manifest keeps
the launch hash, and final --analyze records the final analyzer hash.
Helper controls cover defaults, both descriptor pairs, Boolean6 exclusion,
and immediate force inhibition followed by actual readback stop. Parser
controls accept the exact projectile chain and reject wrong NPC, projectile,
sequence or missing readback. No queued-soak verdicts were added.

Next: one opt-in, single-victim lethal-dose test in a forced-route level1
flight, with actual health actor→accepted SEND→damage return→death branch→
named store→callback readback. Inspect original handler/health code first;
never write an objective counter directly or force a win. Stop after the
first named loss response (id13 must remain below5).

## Session 6661: level-1 one-victim death threshold

One adapter build and one flight, unlocked screen; retail aspect/draw-distance
settings. `ROGUESQ_OBJECTIVE_RESPONSE_LETHAL=1` permits only one damage-request
register change after an ordinary exact accepted hit has visibly reduced
positive health on the same node/NPC/descriptor/health actor. All forced
segments stop after that dose. No health or counter is directly written.

| Witness | VI / raw-log line | Result |
| --- | --- | --- |
| Flight/callback | 5265 / 266035 | B40=1, width512, origin690400 |
| Ordinary accepted SEND seq4 | 7076 / 295090 | projectile80359A5C, node8021B628, NPC8035B35C, descriptor80319AF4 |
| Ordinary pre/return | 7076 / 295094–295097 | actor8035D3A0=NPC+38; raw/requested4, HP390→386, return386 |
| Later force/SEND seq6 | 7744 / 303260,303268 | same victim and descriptor, projectile8035A65C |
| Lethal pre/return | 7744 / 303272–303275 | raw10, requested387, HP386→−1, return−1 |
| Actual death-effect call | 7744 / 303276 | Boolean24=1, counter13 delta1, second counter0 delta1 |
| Actual counter writer | 7744 / 303278 | guest8006594C, id13 old0 new1, exact victim and seq6 |
| Callback readback/stop | 7748 / 303310,303314 | id13 old0 new1; no further forces |

128.32s wall, six forces in arm1 only, 0 crashes. Five changing id10
readbacks in natural arm0 control value detection; mark-all eligible id10
identities count3/2 in arms0/1. Eight sampled named live and eligible
identities in both arms. Arm2 is absent because the safe readback stop
ends the experiment early. c13=1, c40=c41=0 and Boolean6=0; no end gate
was intentionally reached and no win/progression was tested.

H-dose is selected for this victim: the ordinary message survives and
skips effects, the one lethal request invokes them. H-routing is not
selected: the original NPC+38 load and measured actor agree. H-effect
is not selected: the measured return, effect call, real store and callback
all agree. The runtime remains the only behavioral witness; label dynamic
causality single-source. Independent original-ELF disassembly proves the
load chain, damage subtraction and positive-return branch semantics; its
SHA256 f6809909002b407b339ca0331e54faea895ac2730f15152ab5221307442f6cc9
matches the prior saved original. This is loss-response coverage only.

Adapter replay is idempotent. Build passes; extracted-C controls pass for
defaults, exact SEND eligibility, ordinary reduction, lethal opt-in off,
Boolean6 exclusion, actor mismatch, globally single dose and force stop.
Analyzer now reports pre/return/effect and requires a prior ordinary exact
hit with a different sequence for a qualified lethal chain. Launch manifest
preserves the initial analyzer hash; response.json stores the final analyzer
hash after re-analysis. Binary and adapter hashes match the launch manifest.
Evidence: `scratch/agent/m6/g1_lvl1s6661_dose/`,
`scratch/agent/s6661_dose/{chain.json,helper_control.c,helper_control.log,
transport_damage_elf.txt,health_elf.txt,elf.sha256}`. No queued-soak verdicts
were added. No library worktree changed.

Parser controls: complete saved chain accepts; removing the ordinary control,
changing the lethal projectile, omitting the actual store, or omitting the
callback readback all yield zero qualified completed lethal chains. Evidence:
`scratch/agent/s6661_dose/parser_control/results.json`.


## Session 6662: level-2 ordinary-dose adapter and target boundary

Original ELF was consulted before the level-2 extension. At 801020B8 the
callback reads counter40; a positive value sets Boolean109 at 801020D8,
then Boolean109==1 requests failure at 80102124. Friendlies saved at
80102A74..84 is 1−counter40. Success at 80102658..A8 requires
Booleans31/32/33/99. Counter40 is therefore a loss witness, not a safe
completion target. Lethal dosing is hard-disabled for level2. The filter
excludes success Boolean1/2/3/4/31/32/33/99 setters and allows at most one
ordinary forced segment per matched NPC/descriptor. No direct state writes.

The completed fresh capture is `scratch/agent/m6/g1_lvl2s6662_lvl2_final/`:
169.97s, B40=2 and lv2 callback, first-flight VI5080..10483. All three
arms occur; zero crashes, zero forced segments, zero exact damage/effect
chains. All seven manifest file hashes match the final files/binary.
An inherited incomplete capture `g1_lvl2s6662_lvl2/` stops in arm0;
its binary/helper hashes differ and it is not combined with this flight.
An attempted launch with that existing tag was rejected without overwrite.

| Per-arm witness | Natural 0 | Forced 1 | Natural 2 |
| --- | ---: | ---: | ---: |
| Unique mark-all eligible identities | 5 | 13 | 10 |
| Counter40-selected sampled live/candidates | 0/0 | 0/0 | 0/0 |
| Logged candidate rows (budget) | 4096 | 4096 | 4096 |
| Forced segments | 0 | 0 | 0 |

Eight changing counter readbacks (ids61 and3) and seven Boolean changes
control the full-table readback detector; all are natural. Eligibility
controls have valid nonzero NPC/descriptor joins, positive radius and c1f1.
The census samples every300 VI, yielding18 snapshots and33..628
pointer-like entries. It is NOT a typed entity census: some interpreted
counter fields are outside the objective-id range. Counter71 is seen in
18 descriptor rows, but its meaning is unproven. Every arm exhausts its
4096 candidate-log budget, so late candidates are unknown.

The measured selection boundary precedes forcing: no observed descriptor
passes the counter40 predicate. This distinguishes unexercised damage
from a positive-health survival result; it does not prove that no level2
loss target exists, that damage routing is broken, or that objective logic
fails. H-response and H-dose remain untested. Dynamic population evidence
is single-source; original ELF independently establishes gate semantics,
not the completeness of our host census. No VERIFIED promotion.

Build and seven-file idempotent replay pass. Extracted current-helper C
controls pass level1 behavior and level2 exact SEND, ordinary health
control, all success exclusions, once-per-victim force and lethal-env
inhibition. Artifacts: `scratch/agent/s6662_lvl2/{population.json,
callback_elf.txt,getters_elf.txt,health_gate_elf.txt,helper_control.c,
helper_control.log,level1_control.c,level1_control.log,elf.sha256}`.
Next: use original level2 initialization and object-table consumers to
establish typed descriptor ownership, then correct the complete census
and target predicate before another flight. No repeat of this recipe.


## Session 6663: slot ownership correction

Original ELF establishes a specific flaw in the earlier population census.
`initNpcSlotList` allocates 0x4000 bytes (2048 records of eight bytes) at
8003E56C..E584. BB0 holds that table. BB4 is a halfword free-list head;
record+4 and +6 are halfword links, with 0xFFFF as sentinel. Original
`unregisterAndFreeNpcSlot` 8003E88C..E8C8 puts a slot on the free list but
**does not clear record+0**. Pointer-looking free records are legitimate
stale aliases, not live NPCs or corruption. Zero/nonzero alone is invalid.
Original `allocNpcContextArrays` 8003FD58..FDA8 allocates BB8's 192 contexts
of 60 bytes. The spawn stores at 8003FF60..FFAC and 800400B0..400FC set
context+0=handler, +4=payload, +0x16=primary slot. Additional registered
slots may share a context; slot counts are not object counts.

The opt-in level2 adapter now walks the free list with cycle/bounds checks,
records every non-free slot and its context ownership, handler, payload,
primary slot, generation, observed birth and retirement. It scans at the
objective callback, dispatcher entry/return from a handler, and slot-free
returns. Birth means first observation, including objects present at epoch
start; this is not an omniscient spawn timeline. Invalid lists suppress
experimental forcing and are reported explicitly. No game memory is changed
by ownership classification. The original slot-free writer is named above;
its retained pointers are legitimate, and the fix corrects the host witness.

Descriptor typing is deliberately incomplete. Independently read original
handlers CABD4 (CAC18/CAC5C/CAC64) and DE80C (DE860/DE88C) establish
context+4 -> NPC+0x34. Only those kinds can select a level2 forced target;
other kinds retain their handler/payload identity and `typed=0`, with no
invented objective fields. The original shuttle handler D3894 also uses
NPC+0x34, including a flag0x20 spawn variant (D3920/D394C), and its death
path D4B80..D4BA8 passes the descriptor fields to the objective writer.
That static observation is not yet in this binary's type map.

Candidate records no longer stop at4096 per arm. The analyzer preserves the
whole ownership/lifetime table plus handler, candidate, accepted SEND,
health/effect and actual objective-store joins. Local same-phase selector
fixtures accept40 and reject success Boolean31 without guest writes. These
validate predicate sensitivity, not the presence of a genuine count40 target.
Real mark-all eligible candidates and changing callback readbacks remain
separate controls. Unknown handlers forbid an absent-target conclusion.

Validation flight `scratch/agent/m6/g1_lvl2s6663_owner/` completed in171.84s,
B40=2, first epoch VI4939..10339, off/on/off, zero crashes or forced hits.
All20 census snapshots have valid free lists: active slots33..516,
stale nonzero free slots0..235, typed slots0..46, unresolved slots33..470.
This selects H-stale-free for part of the old inflated population, supported
by independent original instructions and the live membership witness.
It does not close H-kind or H-late for an actual counter40 target.
8,763 observed slot generations,8,364 retirements;23 handlers (22 unresolved),
117 probe-droid slot generations across12 reused context addresses.
Zero ground-transport handler identities observed. Candidate rows per arm
59,747/134,473/64,666; eligible mark-all identities15/17/11. All three
local selector controls accept40/reject-success; six real counter changes
control readback sensitivity. No selected descriptor, damage-dose test,
objective-response claim, win or VERIFIED promotion. All six launch-manifest
hashes match at completion. Original ELF hash and bounded disassemblies,
helper control sources/logs, build log and computed summary are preserved in
`scratch/agent/s6663_lvl2_owner/`. First helper compilation lacked string.h;
adding the fixture include fixed it; both helper control executables then
passed. Generated replay is idempotent across8 files; build passes.

The runner's ownership summary retains explicit unresolved status, full
slot-generation records, retirements, handlers, phase-scoped candidate totals
and selection controls. This run is single-source dynamic evidence;
original ELF independently establishes ownership semantics, not retail
behavioral equivalence. No new queued-soak verdicts or library edits.


### s6664 — complete captured level-2 handler class

Original ELF SHA256: `f6809909002b407b339ca0331e54faea895ac2730f15152ab5221307442f6cc9`.

Original ELF audit covers all 23 handler addresses in the s6663 roster, using
symbol-bounded disassembly and the original dispatch tables, rather than
inferences from placeholder names or host execution. Typed values now mean
1 = ordinary objective damage, 2 = excluded from that route, 3 = DAT spawn
trigger, 0 = unknown. An unknown kind still rejects forcing. A classified
kind is not proof that a count40 target exists. This table covers the captured
roster, not every handler the game could ever spawn.

| Original handler | Message-5 route / original witness | Class |
|---|---|---|
| 800403EC randomBurstNpcHandlerVariant | switch falls to 80040978 | 2 |
| 80044724 cutsceneActorNpcHandler | switch falls to 80044BC4 | 2 |
| 8004C6C8 byteAnimatedDebrisNpcHandler | switch falls to 8004CBE0 | 2 |
| 8005427C attachedMeshOverlayNpcHandler | switch falls to 800543DC | 2 |
| 8005BCC4 cinematicSplineWalkerNpcHandler | switch falls to 8005C59C | 2 |
| 8005C874 audioCueDispatcherNpcHandler | table 8003AFA8[4] = 8005D914, return | 2 |
| 80060690 randomlyScaledEffectNpcHandler | switch falls to 800608E8 | 2 |
| 80060D8C minimalRandomNpcHandler | switch falls to 80061074 | 2 |
| 8006F6A0 npcDebris1Update | switch falls to 8006FC70 | 2 |
| 8006FC90 orientedNpcHandler | switch falls to 80070088 | 2 |
| 800700A8 multiEventTemplateNpcHandler | table 8003CC30[4] = 80071038, return | 2 |
| 80072EC4 npcWaterSprayUpdate | switch falls to 8007372C | 2 |
| 80076BE4 npcWakeUpdate | switch falls to 80077220 | 2 |
| 800B7168 playerAwingUpdate | table 800A5AE0[4] = 800B745C; sound, slot cleanup | 2 |
| 800BF4A0 attached3DSoundEmitterNpcHandler | switch falls to 800BF764 | 2 |
| 800C0084 handleHUD | table 800A6458[4] = 800C1050; shake floats +248/+24C, random byte +F7F | 2 |
| 800C68A0 hangarVehicleDisplayNpcHandler | switch falls to 800C6FD8 | 2 |
| 800CABD4 npcProbeDriod | table 800A6C10[4] = 800CB8D4; damage CB934, objective CBD34 | 1 |
| 800D5208 npcDebrisFieldUpdate | table 800A7610[4] = 800D5AA0; ordinary damage D5D1C, objective D5DA8 | 1 |
| 800D93C0 npcWingmanUpdate | table 800A7A00[4] = 800D9BB0; damage D9C54, objective D9D28 | 1 |
| 800DB11C npcTieVariantUpdate | table 800A7C10[4] = 800DBE08; damage DBECC, objective DBF68 | 1 |
| 800ECC28 craftMountedAnimationNpcHandler | switch falls to 800ECDCC | 2 |
| 800ECE10 datItemActorNpcHandler | no message5; default ED130, descriptor store ECE48 | 3 |

Table indices are zero-based after message-minus-one dispatch. All damage
rows use node+4 payload, payload+34 descriptor, payload+38 actor and the
six descriptor fields +70..+84 on ordinary death. Original descriptor stores:
CAC64, D52A4/D52D0, D94B0, DB1B0/DB1B4. D5208 has a distinct message5
subevent12 path (D5AA0..D5C10) whose objective fields start at +B0. The
adapter does not treat those as ordinary death fields or dose that event.

ECE10 stores the incoming spawn descriptor at payload+0. Its +34 is a
float, zeroed at ECEC4. The descriptor's +34/+38/+3C are Boolean/counter
conditions (ECF04..ECF58); +6C/+70 limit spawn totals (ECF60..ECFCC).
It eventually calls spawnDatStructureNpcByType, not the ordinary damage
writer. Thus payload+0 is recorded for ownership, but its +70 is never
interpreted as an objective index and it cannot select a projectile force.
This establishes a script boundary, not a claim that this script writes40.

The persistent adapter now classifies the whole roster and extends the
existing exact SEND / ordinary-health / death-effect witness to all four
damage handlers. NPC/message registers come from the original sites:
probe r17/r19, debris r17/r19, wingman r16/r18, TIE r17/r16. The additional
witness runs only for the opt-in level2 probe; level0/1 and disabled behavior
are preserved. No lethal level2 dose is enabled. Fixture checks cover all23
kinds, every descriptor variant, deliberately count-like data in excluded
kinds, free/stale/unknown/cyclic cases, parameterized health context,
success exclusions and the level1 controls. These are local controls, not
retail evidence. Generated replay is idempotent on nine files; build passes.
Original hash, disassemblies, tables, fixtures and build logs are in
`scratch/agent/s6664_lvl2_kinds/`.


The single flight completed in 171.81 s, first epoch VI4955..10356, B40=2,
off/on/off, zero crashes and zero forces. All20 free-list snapshots validate;
active slots33..607, stale pointers0..335. The23 mapped kinds classify
7,836 slot generations (688 damage,7,130 excluded,18 DAT trigger).
Two later kinds contribute six more generations and up to three concurrent
unknown slots: 8006C3A0 splineWalkerCraftNpcHandler and 80075720
heavyRandomBurstNpcHandler. Their original switches send message5 directly
to 8006C4E0 and 80075B88 respectively; neither has an ordinary damage path.
Both are now class2 in the final adapter and reject count-like fixtures.
That last two-kind change was applied AFTER the flight and rebuilt/tested,
not flight-tested; both class0 and class2 reject forcing. The saved
captured_adapter.py and six all-true capture_hash_check.json entries identify
the actual capture revision. Do not retroactively report unknown=0 for it.

All25 observed kinds now have an original-backed classification. This closes
the sparse-handler-map work unit; it does not close target availability.
No count40 live descriptor, eligible candidate or accepted forced SEND was
observed. Some birth/retirement rows have uninitialized/cleared descriptor
pointers; classification alone does not make those valid descriptor reads.
The run does not test a forced count40 hit or exclude later script spawns.
Positive controls: mark-all eligible identities15/17/16; all three local
selector fixtures accept40/reject success; six actual callback counter
changes. The new health witness records ten natural damage pre/returns:
200→190,20→10,10→0,20→10,20→10,10→0,10→2,10→0,20→10,10→0;
all match raw damage and returned health, including four deaths. Those
actual reductions control health sensitivity; no force_seq is associated
with them. Descriptor death fields are count0, not40. Thus natural damage
route observability is established; forced objective causality is not.
Candidate rows62498/125562/61216;7,842 slot generations and7,481 retirements.
Full rows/joins are in scratch/agent/m6/g1_lvl2s6664_kinds/response.json;
compact summary is scratch/agent/s6664_lvl2_kinds/summary.json. Dynamic
findings remain single-source; independent ELF backs structure/dispatch
only. No VERIFIED promotion, win, default change, library edit or new soak
verdict. Next is the original level2 DAT producer/spawn boundary for count40,
not a repeat of this map flight or another per-handler census.

### s6665 — count40 is a gated rescue-shuttle death effect

Offline work only: no game launch, new soak, regeneration or runtime build.
`tools/g1_dat_inventory.py` walks the retail ROM manifest, inflates
`level/lv_2/dat`, bounds-checks all offset lists/records/names and rejects
record overlap. It emits all 401 definitions: type0=127, type3=59,
type6=99, type7=116. Unknown layouts remain raw words, not objective fields.
Only audited type0 subtypes 0x21/0x24 receive semantic death fields.
This is a complete structural inventory, not a claim that all subtypes have
been semantically decoded. Asset ROM offset 0x008F11C8, inflated size86040,
compressed size23683 (including the format's ten extra bytes), SHA256
`7e27a6753b1fa491a29ee17abff4aa955720f90daaf1381adf50106263d75616`.

| DAT offset | Type/subtype | Name | Activation Boolean / counter / minimum | HP | Death counter/delta |
| --- | --- | --- | --- | --- | --- |
| 1270 | 0/21 | SHIP_01 | 1 / 0 / 0 | 4500 | 71/+1; Boolean7=1 |
| 1350 | 0/21 | SHIP_02 | 2 / 0 / 0 | 4500 | 71/+1; Boolean8=1 |
| 1430 | 0/21 | SHIP_03 | 3 / 0 / 0 | 4500 | 71/+1; Boolean9=1 |
| 1510 | 0/24 | 40_Rebel_Rescue_Shuttle_01 | 21 / 0 / 0 | 2000 | 40/+1 |
| 1628 | 0/24 | 50_Rebel_Rescue_Shuttle_02 | 22 / 0 / 0 | 2000 | 40/+1 |
| 1740 | 0/24 | 60_Rebel_Rescue_Shuttle_03 | 23 / 0 / 0 | 2000 | 40/+1 |

Offsets/subtypes above are hexadecimal; counters, Booleans and HP are decimal.
The known D5208-associated id71 ships are the positive decode control, not a
claim of new hits. All three shuttle death tuples are (40,1,0,0,0,1).

Original ELF, independent of generated runtime code:

- 8003BFF0[0x24] = 800657DC: subtype24 returns category1 because
  descriptor+88 is zero for these definitions. Grid activation checks
  reference range at 80047554, then isDatItemConditionMet at 80047570.
- 8003C140[0x24-12] = 80065854: nonzero descriptor+60 requires the
  corresponding Boolean at 801388A0[id-1]; +64/+68 are a counter minimum.
- 8003BDB8[0x24-12] = 800654C8 dispatches npcShuttleUpdate800D3894;
  8003BED8[0x24-12] = 80065708 selects the same handler for structure
  spawning. Therefore this is not ECE10's incompatible payload+0 layout.
- Shuttle message1 stores descriptor to payload+34 at 800D3920 (or
  incoming wrapper+0C at 800D3948). 800A74C8[4] = 800D49FC is message5.
  It calls dealDamageToNpc at 800D4B0C. Nonpositive health enters
  destruction, then reads descriptor+70..+84 and calls80065914 at
  800D4BA8. Actual counter store is8006594C. This names the original
  damage-to-counter producer; no live shuttle or hit is asserted.
- lv2_checkComplexObjectives at80102174..8010226C requires Boolean59=0 and timer1>=100.0 before
  considering rescue. If Boolean1=1 and7=0 it sets21=1,59=1; corresponding
  alternatives are2=1/8=0 ->22, and3=1/9=0 ->23. The constant at800A95F4
  is IEEE754100.0. GNU mips64-elf-objdump independently decodes
  80102194 as `c.le.s $f2,$f0` and8010219C as `bc1f`, confirming direction.
  Timer1 is read from8010C9FC by800C76E0; it is guest time, not wall time.

Saved s6664 first flight epoch, VI4955..10356 (5401 VIs), joins to the
original predicates: Booleans21/22/23 and59 initialize0 and never report a
change; Boolean1 becomes1 atVI5881;2/3 and7/8/9 stay0. Five actual Boolean
changes control monitor sensitivity (128,1,127,71,72). Start/end and exact
line provenance are in inventory.json; no later epochs are pooled. The
phase-scoped readback logs are sampled at callbacks, so they do not exclude
an unobserved transient between callbacks. No timer value was captured:
the tempting "90 VI-seconds < 100" explanation remains unproved because
timer initialization and accumulation have not been joined dynamically.

Result: the retail level2 definition-without40 hypothesis is refuted; an
ordinary shuttle layout supplies the real count40 producer. H-activation
is supported for the saved capture by original predicates plus observed
closed gate values. Why the timer gate never opened remains unresolved.
No forced response, success, retail equivalence or VERIFIED promotion.
No guard, lethal dose, counter/health write or default change.

Reproduce:
`python3 tools/g1_dat_inventory.py --check-level2 --log scratch/agent/m6/g1_lvl2s6664_kinds/run.log --output scratch/agent/s6665_lvl2_producer/inventory.json`.
All assertions pass, including original dispatch/store opcodes and known
id71 decode. Malformed list and record bounds are rejected. Original ELF
disassemblies, GNU gate disassembly and full inventory live in
`scratch/agent/s6665_lvl2_producer/`. Next: one fully joined timer/gate/spawn
capture with original shuttle ownership and ordinary-hit witness, rather
than repeating the old sparse map census.

### s6666 — timer, rescue activation and ordinary damage join

The persistent adapter now carries the whole original-source table in one
build: timer reset800FA618, timer tick800FA924, timer setter800C7714,
Boolean setter800C7564, callback80102174 and actual timer return after
80102184, loaded DAT base plus six known offsets, grid range47554 /
condition47570 / setup47640, D3894 ownership and its message5 health/effect
path. Original ELF words are asserted by g1_dat_inventory.py --check-level2;
the decoded retail DAT independently supplies the three rescue offsets and
the three id71 SHIP controls. These are independent of generated execution.
The adapter never writes timer, Boolean, counter or health state. Level2
lethal dosing remains disabled. --flight-vi12000 extends the first epoch;
force stays off until a named live arrival after1800VI, on1800VI, then off.
The default5400VI level0/1 behavior is preserved. Reapplying all11 files is
idempotent; CMake target built successfully.

One new unlocked-screen flight, `scratch/agent/m6/g1_lvl2s6666_activation/`,
B40=2, retail aspect/draw distance. It ends at VI17021, dv12001, after281.27s
wall; no crash lines, SIGKILL at probe completion. Off/on/off transitions
VI5020 /14864 /16665; exactly one forced segment, in on only. The raw log
is about180MB; read response.json/response.log or bounded windows.

| Boundary | Observed evidence | Discrimination |
|---|---|---|
| Initialization / tick | VI5018 reset timer1=0 at800FA618; VI5020 tick0.0333333351 at800FA924 | Actual changing-value positive control, not callback execution alone |
| Old cutoff | VI10421, dv5401, timer1=55.5496902; actual get return agrees;59=0,1=1,7=0,21=0 | H-duration selected for this recipe; old5400VI cannot reach100 |
| Threshold / gate writer | VI14859,dv9839,100.033333; original setObjectiveBoolean store800C7564 writes21 and59 to1 | Other predicates permit activation; H-state blocked-gate explanation rejected here |
| Named live shuttle | VI14863, canonical slot254, node80219E04, payload80375F0C, handler800D3894, descriptor8031D2A0=DAT8031BD90+1510 | Original rescue01 definition matches; H-spawn prevents any live shuttle rejected here |
| Ordinary force / SEND / health | force VI14873 seq1 projectile80376D0C; accepted SEND VI14881; same node/payload/descriptor/projectile; health actor803721EC, requested10,2000->1990, return1990 | Exact ordinary hit control passes; H-hit excludes named shuttle rejected here |
| Counter40 | No forced objective store or callback change; lethal_count0 | Expected surviving-shuttle behavior, not evidence of broken death/objective logic |

All35 sampled actual timer returns equal memory values. Sampled timer range
0.0333333351..120.3508; nine counter and thirteen Boolean readback changes
control monitors. Mark-all produces38 positive eligible candidate rows;
local fixtures accept40 and reject success31 in every arm. SHIP_01 id71
also matches the final DAT base+1270 and a live canonical slot251. The
scanner records redundant slot aliases; these are not extra objects.
Only rescue01 is proved live/hit. Rescue02/03 stay gated by their own ship
states; no conclusion about their hit routes.

Grid trace sees two preflight SHIP setup returns, no rescue range/condition/
setup return in the first flight epoch. Thus the exact rescue spawn caller
is not dynamically attributed; do not claim that grid path executed. The
positive descriptor/primary-slot join still proves the named shuttle exists.
The original ELF independently supports D3894 descriptor+34 and message5
ordinary damage; dynamic changes match those contracts. Timing/route
repeatability remains single-flight evidence. No retail equivalence,
objective(d) completion, level VERIFIED, win or progression claim.

Original-source command first failed because its fresh output directory did
not exist; mkdir then rerun passed. An early postprocessor call preceded
completion of the asynchronous reanalysis and read the old schema; waiting
and rerunning succeeded. No extra game run/build was needed. Evidence:
`scratch/agent/s6666_lvl2_activation/{original.json,timer_init.txt,timer_tick.txt,
build.log,summary.json,analysis.txt}`. No new queued-soak verdicts.


### s6668 — level-2 named loss response qualification

Original ELF audit: message5 calls damage800F2120 at800D4B0C; the
800D4B14 positive-health branch skips the death effect. When health is
nonpositive, descriptor fields feed datItemSetObjectiveBooleanCount at
800D4BA8. The later level2 callback calls getObjectiveCount(40) at
801020B8; its returned value is tested at801020C0. Failure flags109/101
are first set at801020D8/20E8. Retail DAT identifies rescue01 at+1510,
health2000, counter40 delta1. g1_dat_inventory.py --check-level2 now
asserts those original instruction words before a run.

The opt-in lethal adapter admits only original DAT rescue01/02/03
(+1510/+1628/+1740), handlerD3894. Each has the same counter40+1 death contract.
An exact ordinary force/SEND and surviving health reduction must establish
the same node/NPC/descriptor/health actor before one currentHP+1 request
can enter the original damage handler. That dose disables further forcing.
After actual counter store and callback memory readback, a host hook after
the original counter40 getter flushes the completion record and SIGSTOPs;
the runner SIGKILLs the process group. Guest failure code is neither
suppressed nor resumed. No direct health, counter, Boolean or timer writes.
Level2 remains ordinary-only unless OBJECTIVE_RESPONSE_LETHAL=1.

Analyzer self-test: `python3 tools/g1_objective_response_run.py --self-test`.
Complete chain accepts; wrong actor/projectile, missing ordinary control,
force, actual store, readback or getter, failure already set, and a second
lethal request (including an unmatched pre-call) reject. The full adapter
replays byte-identically on all11 generated files. CMake target passes.
The analyzer source at launch is retained in the evidence directory because
its later strengthening counts unmatched lethal pre-calls and adds full
synthetic fixtures; final reanalysis records its own source hash.

First attempt `g1_lvl2s6668_loss`: 281.03s, VI5090..17092, 0 crashes,
0 forces/doses. Timer100 activates Boolean22 and rescue02 at DAT+1628;
rescue01-only selection therefore cannot test the death path. Ordinary
controls0, so this is explicitly inconclusive for objective response. The
first-build adapter source is reconstructed and SHA256-verified against its
launch manifest in `adapter_rescue01_at_launch.py`. The corrected build
allows only the three original-backed named rescues and retains same-actor
control/dose requirements. Evidence from the two builds is never pooled.


Corrected attempt `g1_lvl2s6668_named` supplies the positive result. All six
launch-manifest hashes match the current binary, adapter, analyzer and recipe
sources. Screen-lock preflight passed; manifest contains only response/TELE/
hit logging opt-ins, no aspect/dd/FPS opt-ins. Epoch VI4941..14694. This
flight activates rescue01; permitting the three original-backed definitions
does not force extra victims. Live descriptor8031D2A0 equals DAT8031BD90+1510,
subtype36, initialHP2000, activation21, counter40+1. Node802191D4,
NPC8037680C and health actor80372398 remain identical across both hits.

| Arm | VI observed | Forces | Actual controls / response |
| --- | --- | ---: | --- |
| Off | 4941..14662 | 0 | Getter40 returns0 with memory0; changing counter readbacks and17 mark-all eligible identities. |
| On | 14663..14694 | 2 | Seq1 ordinary damage then seq2 one dose;8 mark-all eligible identities; original store and callback getter0→1. |
| Off2 | Not reached | 0 | Deliberate process stop before the failure branch; no null claimed. |

Seq1 force14664, accepted SEND14669, ordinary damage10: HP2000→1990,
return1990 (raw log735124/735127). Seq2 force14684, SEND14690, raw10
changed only at the original damage call to requested1991: HP1990→−1,
return−1 (736326/736329). Death effect736424 feeds writer8006594C;
actual counter40 store0→1 at736426. Callback memory readback736689 and
original getter return736690 both see1 atVI14694, flags109/101 still0.
Completion736691 flushes before SIGSTOP. Eight actual changing counter
readbacks and the getter's observed0→1 control detection. All further
forcing is inhibited at the dose. H-dose selected for this named victim;
H-routing and H-observation are contradicted by the exact positive chain.

ORIGIN: legitimate original shuttle damage/death effect is the counter40
writer (datItemSetObjectiveBooleanCount at8006594C). The opt-in changes one
requested damage argument after an ordinary control; it does not repair
corruption, bypass a death effect, or write health/objective memory directly.
Dynamic causality remains single-flight, single-source; original ELF/DAT
independently corroborate the contracts, not runtime or retail equivalence.
Level2 named response unit closes; full VERIFIED remains unclaimed.

The observer was interrupted before writing analysis; the saved game log
already contains completion. Reanalysis recovered it without another game
run. The wrapper later reports three30s stalls while the process is
intentionally SIGSTOPped: these do not establish a flight stall. An active
flight wall duration was not preserved by that observer and is not inferred
from the wrapper hold. First rescue01-only flight remains separate. One
postprocessing display asked for nonexistent definition field `name` after
printing all qualification checks; corrected display uses definition fields,
with no evidence change. Final analyzer fixtures, original-word assertions,
11-file byte-identical adapter replay, no-op CMake target and six manifest
hash comparisons pass. No lib edit, default change or new soak verdict.
Compact proof: `scratch/agent/s6668_lvl2_loss/qualification.json`; full joins:
`scratch/agent/m6/g1_lvl2s6668_named/response.json` and raw736326..736691.

## s6669 — level 3 checked retail contract; live response remains open

One bounded tool change before enabling level3 forcing. The prior proposed
shuttle-style counter/death probe does not match this level's inspected
contracts. `tools/g1_dat_inventory.py --level 3 --check-level3 --output PATH`
now checks 62 original ELF instructions and four named retail DAT definitions.
It decodes subtype0x14 as `unregistered-damage-objective`, with a separate
`damage_effect` field and `health_detail0`; it does not label this a death
trigger or apply the shuttle activation layout to it. Existing subtype0x21/
0x24 fields and legacy level2 checks remain unchanged.

Original callback80102D08 reads Booleans4/18/21 into failure calls800C7738;
that helper ORs bit4 at800C7754. It separately reads counter22 into the
completion helper800C776C (bit8 at800C7788). Friendlies reader80103530 reads
c27/c28, adds them, subtracts from100, and calls800C77B0. These are different
contracts: a death Boolean is not a named loss counter.

| Retail definition | DAT offset | subtype | +6C word | Effect at +70..84 | Qualification choice |
|---|---|---|---|---|---|
| City_1 | 0x048C | 0x14 | 2000 | c28+1, no Boolean, no second counter | selected static candidate |
| GVT_BLDG_main | 0x1548 | 0x14 | 6000 | c28+1 and Boolean4=1 | exclude failure setter |
| Tech_Center_Main | 0x391C | 0x14 | 5000 | c7+1 and Boolean18=1 | exclude failure setter |
| Madine_Shuttle | 0x7788 | 0x24 | 200 | Boolean21=1; both counter IDs0 | exclude; no named counter |

There are95 subtype0x14 counter28+1 candidates without any Boolean setter or
second counter; this is a static inventory, not95 live hittable objects.
Original `dealDamagetoDatItem`800C7390 checks DAT halfword+6 againstFFFF at
800C73BC/C0. The FFFF branch800C748C subtracts damage from the detail-indexed
word at+6C, stores at800C74AC, tests subtype0x14 at800C74B4/B8, then loads
+70/+74/+78/+7C/+80/+84 and calls80065914 at800C74E0. There is NO health
threshold between the store and effect call in this branch. The original
writer8006594C applies the first counter delta;80065928 stores the Boolean.
The registered-slot branch instead sends message5 at800C73F8; its actual
handler and effect timing have NOT been qualified by this unit. Do not
assume live City_1 is unregistered, or that every projectile hit follows the
fallback. A currentHP+1 request is not justified by this static result.

Competing hypotheses: H-shuttle counter target is contradicted for the
inspected shuttle; H-building-death is contradicted ONLY for the FFFF path;
H-building-message selects the explicit subtype0x14 fallback contract.
DAT fields and original consumer/reader instructions corroborate semantics;
all code-path evidence is original-source static evidence. No independent
emulator/live damage observation, dynamic causality, retail equivalence or
VERIFIED promotion is claimed. Saved level3 ctl/TELE writer-call counts
above still do not establish the named chain.

Validation: all19 playable-level inventories match the prior tool after
removing only the new subtype0x14 fields (100 new layouts on level3).
Level2 --check-level2 passes with the same three rescues/three SHIP controls.
Positive controls decode the three excluded named definitions and selected
City_1; all11 negative fixtures reject (six changed ELF branch/call/writer/
reader instructions, five changed named DAT counter/Boolean fields).
Compile and diff checks pass. Reproduce and inspect:

```sh
python3 tools/g1_dat_inventory.py --level 3 --check-level3 --output scratch/agent/s6669_lvl3_response/checked.json
python3 tools/g1_dat_inventory.py --level 2 --check-level2 --output scratch/agent/s6669_lvl3_response/level2_regression.json
python3 scratch/agent/s6669_lvl3_response/check_contract.py
```

Artifacts: `scratch/agent/s6669_lvl3_response/checked.json`, `validation.json`,
original callback/helper/shuttle disassembly and rejection fixture script.
No game build/run, generated adapter change, lib edit or default change.
Next: one complete ordinary City_1 hit/slot/health/store/friendlies-readback
experiment, with original registered-handler audit in the same unit. Stop
forcing after one named change; exclude all success/failure setters. Do not
reuse the level2 NPC+34/D3894 ownership layout for subtype0x14.

## s6670 — level 3 ordinary named-damage route qualification

Original-ground-truth audit preceded runtime changes. The original subtype20
setup-table entry8003BDD8 selects800653F4, whose handler is8006CBB0. Its
spawn store8006CC24 sets payload+34=DAT; message5 table8003CA30 selects
8006CF88. Health is DAT+6C+4*detail; store8006CFE8 subtracts message+6.
The positive-health branch8006D278 skips effect8006D6F0. This differs from
C7390's FFFF fallback, which applies subtype20 effect without a death gate.
The retail City_1 definition independently supplies subtype20, health2000,
counter28+1 only. No shuttle layout or lethal threshold was assumed.

Two failed hit controls are retained separately:

| recipe | first-flight VI epoch | wall s | requests | crash lines | limit |
|---|---|---:|---:|---:|---|
| s6670_response |5255..10657|176.42|0|0|No projectile-context candidates or accepted hits; no damage conclusion|
| s6670_script |5312..10712|178.00|0|0|Adapter eligibility prevented script request; which extra filter stopped it was unmeasured|

Both had actual counter readback changes3/12. The second also explicitly
invoked original pure getterC761C: getter3 changes0→1 and equals memory.
City_1 is observed with owned registered handler6CBB0 during the first
epoch, but that does not establish its registration at a later request.
No game-invoked friendlies-reader events were observed in either flight;
there is no positive-control qualification of that hook here.
Thus neither flight qualifies a silent objective or damage-path null.

The corrected instrument calls original named script-damage API C7390 once
with request10, after original name lookup equals the selected DAT entry and
its health is positive. It observes the registration tuple and lets the API
choose registered vs FFFF. This is a script-route test, not player-shot proof.
A copied context preserves caller registers; the original API uses ordinary
guest call-stack space. Explicit probe calls to the original stackless pure
getter read3/27/28; they are labelled probe_call=1. The friendlies routine
writes UI state and is never invoked by the probe. No direct health, counter,
Boolean or timer stores, win or progression test are introduced.

Original validation now checks97 literal ELF anchors, including handler
tables, health arithmetic/gate, name lookup, pure getter and existing lv3
script API callers. All97 individually changed instruction/table fixtures
reject; level2 DAT controls remain unchanged. Both completed builds pass;
the corrected third build passes. Positive/negative analyzer fixtures cover
missing stages, mismatched identity/message, duplicate request and wrong
health arithmetic/handler/return; generated-hook replay is idempotent.

Corrected result (`s6670_script_v3`): one178.00s flight, epochVI5291..10692,
off/on/off starts5291/7095/9491,0 crash lines. One request atVI7095:

| link | observed value |
|---|---|
| original lookup | City_1 pointer80325F94 returns DAT80325EEC, base80325A60+048C |
| live ownership | canonical slot429, generation1/birth5414, node8021A728, payload8038770C, handler8006CBB0 |
| API / message5 | request10, stack message80165E80, sourceFFFF (script), api_seq1 |
| original health writer | pc8006CFE8, DAT80325EEC+6C at80325F58, detail0,2000→1990 |
| handler / API return | same message/node/payload/DAT; health1990, API return1990 |
| counter28 |0 before and after; explicit original getter returns0/memory0 atVI9493 |

The actual changing health store is the damage instrument's positive control.
Actual getter3 changes0→1 atVI5361 and equals memory; all getter samples
match memory. No second damage request occurs. `forces=0,0,0` is the separate
TELE counter, not the script-request count. No fallback or effect-hook events
were observed; those silent hooks have no same-run firing control and are NOT
independent proof of absence. The original positive-health branch plus the
joined store/return establishes a surviving registered ordinary hit; counter28
remaining0 is consistent with it. H-registered selected for this request.
The original game-invoked friendlies routine remains unqualified, with zero
events; its100-(c27+c28) arithmetic is original-source evidence only. Explicit
probe getters are not mislabelled as game invocations.

ORIGIN: legitimate request10 enters original C7390, forwards message5 at
C73F8, and original8006CFE8 writes1990 to the detail0 DAT health word. The
value is ordinary surviving health, not corruption. No mitigation was added.
Dynamic causality is single-flight; static retail DAT/ELF independently
corroborate identity, health and route contracts. No death/counter response,
retail equivalence, player-shot result or VERIFIED promotion is claimed.

All6 current launch hashes match; twelve generated files replay unchanged.
Build logs: scratch/agent/s6670_build{,_v2,_v3}.log. Compact proof with log
line numbers/ownership/readers: scratch/agent/s6670_qualification.json; final
full rows: scratch/agent/m6/g1_lvl3s6670_script_v3/response.{json,log}. Original
97-anchor report and mutation controls: s6670_lvl3_original_v2.json and
s6670_original_validation_v2.json under scratch/agent/. The two failed hit
controls remain in g1_lvl3s6670_response/ and g1_lvl3s6670_script/. All runs
were screen-unlocked at launch, retail rendering settings, SIGKILL stopped.
Next bounded unit: same-flight ordinary control then one exact-owned City_1
destruction dose, requiring actual counter28 store/readback/getter, with all
Boolean setters excluded and no win/progression test.
