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
| 1 | s6659 corrected forced-route flight: off/on/off, 25 forces; two complete force/SEND/store/readback chains for id10, eight changing id10 readbacks. ids13/40/41 and Boolean6 stay zero. | Original ELF identifies 13/40/41 as friendly-loss counters, with id13>=5 failing. H-incidental selected by the planned direct-callback-counter discriminator; no named loss-counter response or fully VERIFIED promotion. Older ctl/tele paths have inconsistent instrument identity. |
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
