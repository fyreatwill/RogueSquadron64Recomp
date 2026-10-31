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
| 3 | s6671: City_1 script request10 HP2000→1990, then same-owned request1991 HP1990→−1; death effect, counter28 store0→1, callback and explicit getter1. | Named friendly-loss response observed, single-flight dynamic evidence; original DAT/ELF corroborate contracts. Flags4/18/21 and successcounter22 stay0. No player-shot, win, retail-equivalence or fully VERIFIED claim. |
| 4 | s6674: same-owned Hobbie API10 HP380→370, then request371 HP370→−1; death effect(40,1,0,0,0,1), original counter40 store0→1, callback/getter1. | Named friendly-loss response observed, single-flight dynamic evidence. Original ELF/DAT corroborate contracts. c15/c16/c28 and Boolean26 stay0; SIGSTOP then SIGKILL. Actual getter40 change controls sensitivity. No player-shot, win, retail-equivalence or fully VERIFIED claim. |
| 5 | s6677: same-owned Wedge API10 health200→190, then one API191 health190→−1; death effectD9D28 tuple(40,1,0,0,0,1) -> writer6594C counter40 0→1 -> callback/original getter1. | Original friendlies=7−(c40+c2); c2>=4 sets Bit4, c4>=9 sets Bit8. Named loss response observed, c2/c4/latches remain0 at stop. Dynamic causality single-flight; no player-shot, retail-equivalence or VERIFIED promotion. Historical id2 writer stays unknown. |
| 6 | s6678 original Barracks two-counter contract; s6679 corrected ordinary admission capture: lookup matches, registrationFFFF/owned0 in all3 arms, no API request. Original getters change; target owned control absent. | No health/objective response tested. Sampled admission boundary only, not absence or counter null. Counter90 consumers/fallback safety next; no lethal admission or VERIFIED promotion. |
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


## s6671 — level 3 controlled City_1 destruction response

One unlocked retail-settings flight, VI5384..7211,120.13s total runner wall
(includes boot/route),0 crash lines. Baseline arm0 then arm1 atVI7192;
off2 intentionally not reached. One binary carries both ordinary and lethal
arms, selected by VI. `ROGUESQ_OBJECTIVE_RESPONSE_LETHAL=1` permits the
second request only after an exact observed ordinary health store and API
return on the same owned target. No guest health/counter/timer stores or
success setters were added. SIGSTOP after callback/getter then runner SIGKILL.

| Link | Observed value |
| --- | --- |
| Definition / lookup | Original City_1 DAT+048C; relocated80325EEC, name80325F94; original lookup returns80325EEC |
| Ownership before both requests | slot429, generation1, node8021A728, payload8038770C, handler8006CBB0, detail0 |
| Ordinary API seq1, VI7192 | request10; original message5 stack80165E80; pc8006CFE8 writes2000→1990 at80325F58; handler/API return1990 |
| Dose API seq2, VI7202..7203 | request1991; same message/owner; pc8006CFE8 writes1990→−1; handler/API return−1 |
| Original effect8006D6F0 | Boolean0/value0, counter28/delta1, counter2=0/delta2=1 |
| Actual writer, VI7203 | pc8006594C id28 0→1; victim8038770C, DAT80325EEC, inside seq2 API window |
| Callback then explicit getter, VI7211 | actual readback28 0→1, original getter28 returns1/memory1; flags4/18/21=0, successcounter22=0 |

Same-run value controls: actual getter3/memory changes0→1 atVI5446; the
ordinary health reduction controls the damage witness, and actual counter28
change controls the named response detector. All observed probe getter values
match memory. The named API and pure getters are instrument invocations,
not player shots or proof the game called the friendlies reader. Dynamic
causality remains single-flight; original retail DAT/ELF independently support
the identity, subtract/bgtz/death-effect and objective contracts. H-dose is
selected for this request. No full VERIFIED or retail-equivalence promotion.

The first analyzer rejected the chain because it demanded delta2=0 when
counter2=0. Original DAT+84 is1, and the original effect passes1. Counter ID0
disables the second counter; the contract is not a zero unused delta. Corrected
the analyzer to require the original tuple(28,1,0,0,0,1), reprocessed this same
capture, and qualified the chain. No binary rerun or runtime correction was
needed. Fixtures now reject missing entry/store/effect/return/readback/getter,
wrong message/owner/generation/dose/store/writer/victim, nonzero second counter,
wrong original delta2, repeat dose and pre-set failure flags. Replay of all12
generated files is unchanged; builds and all analyzer fixtures pass.

ORIGIN: legitimate script requests10 and1991 reach original registered
handler8006CBB0. Original8006CFE8 writes health1990 then−1; original death
effect8006D6F0 invokes80065914 and original8006594C increments counter28.
These are intended game damage/objective values, not corruption. Added only
opt-in test dosing and read-only witnesses, no runtime mitigation/default/lib
change, win or progression test. Slot generation is observed by the existing
census; it is not a hardware lifetime oracle.

Reproduce: `env ROGUESQ_OBJECTIVE_RESPONSE_LETHAL=1 python3 tools/g1_objective_response_run.py <fresh-tag> --level 3`.
Saved evidence: `scratch/agent/m6/g1_lvl3s6671_dose/response.{json,log}`,
`manifest.json`, `run.log`; compact joined proof
`scratch/agent/s6671_qualification.json`; original97-anchor report
`scratch/agent/s6671_original.json`; build `scratch/agent/s6671_build.log`.
Five of six current launch hashes match; the analyzer differs solely because
its post-run contract correction and stricter message-chain checks are recorded
above. Binary, adapter and launch helpers match. No new queued-soak verdicts.
Next: bounded level4 original objective/target contract qualification.


## s6672 — level 4 original wingman loss contract

One bounded offline tool change, no game build or run. Added
`--check-level4` and `--mutation-check-level4` to `tools/g1_dat_inventory.py`.
The original ELF callback80103720..80103990 and reader80103CC4..80103D04
establish friendlies saved =6−(counter40+counter15). The callback tests counters
16>=3 and15>=3 and Boolean26==1 for Bit4 failure. Its success test is counter28>0
with word8010D060==1, calling800C776C (Bit8). It also reads counters29/30/31
and Booleans12/32 for speech/staging. Historical counter15 is thus named loss;
counter5 is not read by these functions. This does not classify every other
mission script or prove the writer of historical id5.

Retail DAT `level/lv_4/dat` (ROM00929AF0,68652 bytes) independently supplies:

| Definition | DAT offset | Subtype | Detail0 health | Effect (counter,delta,Boolean,value,counter2,delta2) | Selection |
| --- | --- | --- | --- | --- | --- |
| x_wing_hobbie | 6A7C | 0x27 | 400 | 40,1,0,0,0,1 | Selected ordinary-control target |
| x_wing_dack | 6E08 | 0x27 | 9999 | 40,1,0,0,0,1 | Alternate, no live availability claim |
| x_wing_corpselighter | 6F08 | 0x27 | 300 | 40,1,0,0,0,1 | Alternate, no live availability claim |
| Y_Wing_uno | 62F4 | 0x27 | 180 | 15,1,5,1,0,1 | Excluded; counter15 plus Boolean5 |
| Y_Wing_dos | 6888 | 0x27 | 300 | 15,1,6,1,0,1 | Excluded; counter15 plus Boolean6 |
| Y_Wing_tres | 6980 | 0x27 | 300 | 15,1,7,1,0,1 | Excluded; counter15 plus Boolean7 |

Original subtype0x27 table8003BE24 selects setup80065510, which registers
handler800D93C0 through80065664; runtime slot is stored to DAT+6 at80065688.
Handler loads payload=node+4 at800D93F4 and stores DAT at payload+34 via800D94B0.
Message5 table800A7A10 selects800D9BB0. Actor is payload+38. Initialization
callback800D7850 passes DAT+6C into original setNpcHealth800F2070; damage uses
original getNpcCurrentHealth800F20EC and dealDamageToNpc800F2120. When actor+1A7
is zero, actor+190 points at the detail health array; otherwise it is inline
health. Actual subtraction writers are800F2148/800F2158. Do not assume DAT
health is always the live storage or reuse City's inline store hook.

Message5 requires prehealth>0 (800D9BBC), subtracts message halfword+6 at
800D9C54, and skips the death effect if returned health>0 (800D9C5C). Otherwise
800D9D00..D2C loads the six DAT effect fields and calls80065914 at800D9D28.
Counter writer8006594C adds delta; Boolean/counter2 indices zero disable those
slots. Hobbie's counter40 effect therefore changes named friendlies arithmetic
without setting a Boolean or satisfying the callback's direct failure/success
tests. Other script reactions remain untested. The named API800C7390's registered
branch sends message5 at800C73F8; the FFFF fallback is a different route.

Validation:332 original instruction/table assertions;380 deliberately changed
inputs rejected (all332 ELF anchors, plus subtype/health/six effect fields on
all six DAT definitions). The first mutation fixture changed the ignored
halfword at record+2 instead of subtype+0 and was correctly accepted; corrected
the fixture to mutate the actual subtype, then reran the complete batch.
Raw struct decoding agrees for all six selected/excluded tuples. All19 level
inventories exactly match the pre-change tool; level2 and level3 contract checks,
Python compilation and diff whitespace check pass.

Reproduce:

```sh
python3 tools/g1_dat_inventory.py --level 4 --check-level4 --mutation-check-level4 --output scratch/agent/s6672_lvl4_checked.json
python3 tools/g1_dat_inventory.py --level 3 --check-level3 --output scratch/agent/s6672_lvl3_regression.json
python3 tools/g1_dat_inventory.py --level 2 --check-level2 --output scratch/agent/s6672_lvl2_regression.json
```

Artifacts: `scratch/agent/s6672_validation.json`, checked inventories above,
and `scratch/agent/s6672_wingman.disasm`. DAT SHA256
`df908872f2c38081e1452c184b63ac3eefaf2fe49bb832ad782b52198179b8c5`;
ELF SHA256 `f6809909002b407b339ca0331e54faea895ac2730f15152ab5221307442f6cc9`.
These are complementary static contracts, not an independent behavioral replay.
No live target availability, damage, objective response, retail equivalence or
fully VERIFIED claim. No runtime/default/library change or new soak verdict.
Next: one original named API ordinary request10 on an actually owned Hobbie,
with complete registered-handler/actor-health/return/getter joins; no lethal dose.


## s6673 — level 4 owned ordinary wingman health chain; counter control absent

Persistent adapter/analyzer/runner now support level4. One named original
API800C7390 request10 is allowed after original name-lookup equality, valid
BB4 free-list exclusion, BB8 ownership, canonical slot and handler validation.
The original F2148 array and F2158 inline stores are both hooked; handler live
arguments and actual store actor/address are observed separately from the API
identity snapshot. Legacy projectile forcing is disabled in this opt-in arm.
All runtime changes require OBJECTIVE_RESPONSE=1/LEVEL=4; defaults unchanged.

Ground truth preceded the instrument: original ELF/DAT checker332 anchors,
380 rejected mutations, original D9BB0..D9D40/F20EC..F215C disassembly.
The subtype is **0x27 (39 decimal)**. The first adapter incorrectly compared
it to decimal27; stopped that attempt with SIGKILL after73.03s,0 crashes,
no epoch/API request, and retained it as `g1_lvl4s6673_lvl4_ordinary`.
The loaded mission DAT and original checker agree on39; corrected predicate
and live-argument/store observations went into the second binary before launch.
Pre-flight DAT loads are not mission definitions: earlier callbacks atVI1770
and2732 show unrelated subtype0 bytes. The final flight DAT base is8031CF50.

Corrected unlocked run `scratch/agent/m6/g1_lvl4s6673_lvl4_ordinary_v2`:
172.03s runner wall, first epochVI4971..10371, width512/origin690400,
B40=4 plus lv4 callback. Arms off/on/off atVI4971/6771/9171;0 crash lines.
Saved frame `fbd/fb_0002500_w512.ppm` visually contains craft, HUD and terrain;
this is flight presence, not a retail equivalence comparison. OS capture not used.

| Link | Observation | run.log line |
| --- | --- | --- |
| Original-owned live target | slot187/gen1, canonical187, node8021B268, NPC8035F68C, handler800D93C0, DAT803239CC | 245844 |
| Same-run mark-all health control | actor80361D58, mode0/detail0, address80323A38, HP400 (off0),370 (on) | 245919,370656 |
| Original lookup equality | lookup=DAT803239CC, owned=valid=1, same slot/gen/node/NPC/actor/address | 370655 |
| API request | one request10, VI6777, prehealth370, counter40=0 | 370657 |
| Accepted handler | action5, exact node/NPC/DAT/actor, message80165E80 | 370663–370666 |
| Actual original writer | F2148, actor register80361D58, address80323A38;370→360 | 370667–370668 |
| Damage/API returns | both360; exact original storage reads360 | 370671–370673 |
| Original getter after hit | id40 returns0, memory0, VI6784 | 371459 |

Mode0 selects actor+190's detail array; detail0 aliases DAT+6C here. H-registered
is supported for this API health route; no unexpected storage branch was seen.
The original positive-return branch atD9C5C skips effectD9D28; no scoped death
effect event was seen, and no destruction dose was requested. HP400→370 before
the API is uncontrolled natural damage; its individual attackers were not joined.
ORIGIN: original dealDamageToNpc800F2120, store800F2148, legitimately subtracts
message damage10 from this owned actor's selected-detail health. No corruption
mitigation, direct health/counter store, library edit or default change landed.

**Control limit:** all128 explicit original counter getters match memory, but
none changes value in this epoch. Actual counter readback changes=0. Mark-all
health-address controls fire in off/on; the real health store is a positive
health control. Those do NOT control counter sensitivity. Analyzer reports
`exact_health_chain=true`, `qualified_ordinary=false`, `changing_getter_ids=[]`.
Thus zero counter40 is an observation, NOT a controlled counter-response null.
No named loss response, player-shot/game-invoked friendlies-reader proof,
retail equivalence or fully VERIFIED promotion. Dynamic health causality remains
single-flight; original independent ELF/DAT support semantics, not live timing.

Validation: both builds pass; the corrected build is the only interpreted
flight. All6 launch manifest hashes match. All13 generated files replay
idempotently; removing the three new hook groups and replaying restores them
exactly. Level2/3 analyzer fixtures pass; new inline/array fixtures reject missing
ownership/lookup/health/getter controls, live-argument mismatches, wrong writer,
wrong dose/return, duplicate request and unexpected effect. Level2/3 original
contract regressions pass. No new queued-soak verdicts. Artifacts:
`scratch/agent/s6673_qualification.json`, `s6673_replay.json`,
`s6673_hook_replay.json`, `s6673_selftest.log`, `s6673_lvl4_original.json`.

Next: one same-owned ordinary-then-lethal API pair, stop at actual counter40
store/getter response before later script progression. The lethal response itself
can supply a changing-value counter control; a silent counter remains uncontrolled
unless another actual getter change occurs. Do not repeat ordinary-only holds.


## s6674 — level 4 named wingman loss response qualified

One opt-in adapter/analyzer change and one unlocked flight. Independent ground
truth was checked before instrumenting: retail ELF/DAT332 anchors/380 mutations;
D9C4C..D9D40 proves positive health skips the death effect and passes the DAT
six-field effect tuple on death. F2120..F215C establishes array/inline storage.
Level2/3 original contract regressions still pass. Static contracts are independent
of the live runtime; dynamic causality remains single-flight/single-source.

The existing adapter now admits exactly one requestHP+1 only after a prior
same-owned ordinary request10 has actual entry/store/return observations. It
revalidates canonical slot/free-list ownership, generation, NPC/DAT/actor,
mode/detail/storage, name lookup, current health and the original effect tuple.
Counter40 and the monitored loss/success fields must be zero before dosing.
The actual effect registers/stack arguments, original counter store, callback
readback and explicit original getter are joined in the analyzer. The flight
latch permits the dosed response through to getter agreement, then SIGSTOP;
the runner SIGKILLs its process group. No direct health/counter stores, library
edit, win/progression test or default changes.

Run: `scratch/agent/m6/g1_lvl4s6674_lvl4_loss/`,113.56s runner wall,
first flight epochVI4966..6784, B40=4 and lv4 callback. Off/on at4966/6766;
off2 intentionally not reached.0 crash lines. Exact Hobbie identity:
DAT803239CC,slot187/gen1,node8021B268,NPC8035F68C,actor80361D58,
handler800D93C0,mode0/detail0,health address80323A38.

| Link | Observation | run.log line |
| --- | --- | --- |
| Ordinary control | seq1 API10 atVI6768; actual F2148 store380→370, damage/API returns370 | 361871..361887 |
| Same-owned dose | seq2 atVI6776, request371 on observed HP370 | 362819 |
| Actual accepted message | action5, message80165E80, same node/NPC/DAT/actor | 362823..362825 |
| Original health writer | F2148, exact actor/address,370→−1; damage/API return−1 | 362827..362871 |
| Death effect | D9D28 passes(40,1,0,0,0,1) | 362865..362867 |
| Objective writer |8006594C counter40 0→1, victimNPC8035F68C/DAT803239CC, VI6777 |362869 |
| Callback and getter | VI6784: initialized c40 0→1, original getter returns1/memory1 |363454..363455 |
| Stop/safety | c15=0,c16=0,c28=0,Boolean26=0 |363456 |

qualification.json retains the exact joined line table. The dose's actual getter40 0→1 is the
changing-value counter control missing in s6673; mark-all owned health controls
also fire in both reached arms. H-death selected for this named victim. H-route
mismatch and H-identity change were not observed for the qualified pair.
ORIGIN: original dealDamageToNpc800F2120 store800F2148 legitimately writes
selected-detail health minus accepted message damage. Original wingman death
effectD9D28 invokes datItemSetObjectiveBooleanCount; its8006594C store legitimately
increments counter40. No mitigation-shaped guard/skip/restore was introduced.

Both ordinary and loss analyzers qualify; all6 launch hashes match. Build,
level2/3/4 analyzer fixtures and inline/array controls pass; missing-link,
identity/message/storage, wrong dose/effect/writer/getter, unsafe fields and
duplicate-dose fixtures reject. Saved s6673 ordinary chain still qualifies as
health only, with its uncontrolled counter-null limitation retained. All13
adapter outputs are idempotent; hook-free replay of all3 level4 hook groups
is exact. The replay harness initially removed the wrong number of blank lines;
corrected removal restores byte identity. No failed game attempts or new queued
soak verdicts this iteration. Proof: scratch/agent/s6674_qualification.json,
s6674_replay.json,s6674_selftest.log,s6674_lvl4_original.json.

Named level4 loss response is observed, not player-shot proof, game-invoked
friendlies-reader proof, retail equivalence or full VERIFIED status. Next:
original-backed level5 callback/target contract qualification.


## s6675 — level 5 original friendly-loss contract

One bounded offline tool change, 2026-10-30; no game build/run. Added
`--check-level5` and `--mutation-check-level5` to `tools/g1_dat_inventory.py`.
Shared wingman instruction anchors and mutation runner are reused by level4/5;
the level4 contract output remains exactly unchanged.

Original reader80104118..80104158 computes friendlies saved=7−(counter40+counter2).
Callback8010415C..80104204 reads counter2, compares against4 and, when
word8010D080 is zero, sets that latch and calls800C7738 (Bit4), then schedules
speech. Counter4>=9 with word8010D084 zero sets that latch, calls800C776C
(Bit8), and sets Booleans1/3. Original getter800C761C reads the 1-based counter
array at80138060. Thus the historical id2 transition is consistent with a
friendly-loss count, but neither its writer nor victim is established by the
old cross-run logs. Counter4 is a separate success path, excluded here.

Retail `level/lv_5/dat`, ROM00949038, 43760 decompressed bytes supplies:

| Definition | DAT offset | Subtype | Raw detail0 HP | Raw effect words +70..84 (counter,delta,Boolean,value,counter2,delta2) | Decision |
| --- | --- | --- | --- | --- | --- |
| x_wing_wedge | 1AFC | 0x27 | 200 | 40,1,0,0,0,1 | Selected ordinary control |
| x_wing_kasan | 19F4 | 0x27 | 9999 | 40,1,0,0,0,1 | Alternative; availability unknown |
| x_wing_rogue_meat | 1C04 | 0x27 | 100 | 40,1,0,0,0,1 | Alternative; availability unknown |
| Reb_combat1..4 | 2070/2170/2270/2370 | 0x2E | 125 | 2,1,21..24,1,0,1 | Excluded coupled raw tuples; handler route unqualified |

H-other selects a simpler callback-relevant response through counter40;
H-loss's id2 interpretation is corroborated by the original reader, not
refuted. H-route applies to the excluded subtype0x2E definitions: the raw
common-offset fields alone do not prove their damage/death handler consumes
them. Unknown layouts remain raw. No historical id2 writer attribution.

Original subtype0x27 setup table8003BE24 points at80065510, registering
handler800D93C0 via80065664. Handler payload=node+4; DAT=payload+34;
message5 table800A7A10 selects800D9BB0 and actor is read from payload+38.
Initialization800D7880 calls800F2070 with DAT+6C. Actor+190 is a detail-health
array pointer if actor+1A7==0, otherwise inline health; live detail must be
observed. Message5 rejects prehealth<=0 at800D9BBC, subtracts the message
halfword+6 through800F2120 at800D9C54, writers800F2148/800F2158, and skips
the effect while returned health>0 at800D9C5C. On death,800D9D28 passes the
six DAT fields to80065914; counter writer8006594C increments40. Wedge's
zero Boolean/counter2 indices disable those effects. Original named
API800C7390's registered branch sends message5; its FFFF fallback differs.
No live identity, availability, health, route, player-shot causality, retail
behavioral equivalence or full VERIFIED status follows from this audit.

Validation:334 executable/table instruction assertions and390 deliberately
changed inputs rejected (334 ELF anchors plus subtype/health/six tuple words
for seven DAT definitions). Direct struct decoding corroborates the seven
raw tuples. All19 inventories match the pre-change tool exactly; the entire
level4 contract dictionary matches too. Level2/3/4 checks, level4 mutation
checks, response-analyzer self-tests, Python compilation and whitespace
checks pass. DAT+ELF are independent source artifacts establishing data and
code contracts; neither is a new live behavioral observation. No library,
runtime, default or queued-soak change; latest soak verdict remains
20261028-075640, already consumed.

Reproduce:

```sh
python3 tools/g1_dat_inventory.py --level 5 --check-level5 --mutation-check-level5 --output scratch/agent/s6675_lvl5_checked.json
python3 tools/g1_dat_inventory.py --level 4 --check-level4 --mutation-check-level4 --output scratch/agent/s6675_lvl4_regression.json
python3 tools/g1_dat_inventory.py --level 3 --check-level3 --output scratch/agent/s6675_lvl3_regression.json
python3 tools/g1_dat_inventory.py --level 2 --check-level2 --output scratch/agent/s6675_lvl2_regression.json
python3 tools/g1_objective_response_run.py --self-test
```

Artifacts: scratch/agent/s6675_validation.json and s6675_lvl5_checked.json.
DAT SHA2563750527765697056173bea035f5498f8565c13ce97e8e8630163202d5d90b90e;
ELF SHA256f6809909002b407b339ca0331e54faea895ac2730f15152ab5221307442f6cc9.
Next: one same-owned ordinary API10 request on x_wing_wedge, join health
store/return and original counter40 getter, with actual changing-value and
ownership controls. No lethal dose in that unit.


## s6676 — level 5 ordinary wingman health chain

2026-10-31. One bounded opt-in adapter/runner/analyzer extension to level5.
Original ELF/DAT checks preceded instrumentation:334 anchors/390 mutated
negatives pass. Existing level2/3/4 contracts and level4 mutation checks pass.
The original wingman route and array/inline health writers are retained;
new level5 callback hooking persists through apply_s6657_objective_response.py
in the fixup chain. Level5 disables generic TELE forcing and all lethal dosing,
including when the lethal env var is set. One named API request10 only.
The original callback loss/success thresholds supply conservative pre-gate
stops c2>=3 or c4>=8. These are diagnostic stops, not game-logic overrides.

Corrected run: `scratch/agent/m6/g1_lvl5s6676_ordinary_v2/`,167.02s runner
wall, unlocked screen, B40=5 plus lv5 callback, VI4682..10086,0 crash lines.
Off/on/off begins VI4682/6482/8882. Exactly one API request, no TELE forces.
Wedge: DAT8031BCCC=base8031A1D0+1AFC,slot87/gen1,node8021B6DC,
NPC8035421C,handler800D93C0,actor80354898,detail0/mode0,
array health address8031BD38. Mark-all owned health controls fire in arms0/1;
initial observed HP200 later becomes190 before the probe (that earlier damage
is not attributed here). At VI6486 request10 follows this exact same identity:

| Link | run.log line | Observation |
| --- | --- | --- |
| Owned live / lookup / mark-all |210884 /277122 /277123|canonical slot87, original name lookup equals DAT, health190|
| API / message5 entry |277124 /277132|original API800C7390 -> handler800D93C0, message80165E80|
| Damage / actual writer |277134 /277136|D9C54 -> F2148 stores190→180 at8031BD38|
| Damage/API returns |277140 /277141|both180; no death effect|
| Explicit original getter40 |277443|VI6489, returned0=memory0|
| End |417359|VI10086, dv5404, still selected/in flight|

H-wingman selected for health delivery and storage; H-route/H-availability
are not observed for this request. No objective getter changes in the epoch:
`exact_health_chain=true`, `named_identity=true`, `request_count=1`,
`getters_match=true`, but `qualified_ordinary=false` because the changing-value
counter control is absent. This is not a controlled objective null. Dynamic
causality is single-flight/single-source; original ELF/DAT corroborate contracts,
not live behavior. No destruction, named-counter response, player-shot,
game-invoked friendlies-reader, retail-equivalence or VERIFIED claim.

ORIGIN: original dealDamageToNpc800F2120's F2148 legitimately writes selected
array health minus the accepted message damage. No mitigation/health/counter
store was added. No library/default changes or new queued-soak verdicts.

First attempt was SIGKILLed before flight after review caught an accidental
change to the level3-only dose expression. Corrected before the second launch;
level3 tick is now byte-identical to HEAD. The incomplete attempt is retained
separately and not pooled. Corrected build, all6 launch hashes, inline/array
and missing-link/identity/health/return/getter/control/duplicate-request fixtures
pass. Level5 fixtures additionally reject wrong selector, callback/definition,
name, offset, subtype and base. All13 outputs idempotent; hook-free level5
replay byte-exact. Proof: `scratch/agent/s6676_qualification.json`,
`s6676_replay.json`, `s6676_selftest.log`, `s6676_lvl5_contract.json`.
Next: same-owned one-shot Wedge death-counter response, not a repeat ordinary
soak. Reuse the observed ordinary control, revalidate identity/current health,
and stop at actual counter40 store/readback/getter before any gate/progression.


## s6677 — level 5 same-owned Wedge named loss response

2026-10-31. One opt-in adapter/analyzer change and one unlocked flight.
Original ELF/DAT contract checks preceded the change:334 instruction anchors
and390 deliberately mutated inputs rejected. Original subtype27 wingman
message5, array/inline health storage, death-gated effect800D9D28 and
counter writer8006594C establish the static contract independently of the
live witness. No retail gameplay oracle was run.

The existing explicit `ROGUESQ_OBJECTIVE_RESPONSE_LETHAL=1` now admits one
level5 currentHealth+1 request only after an exact same-owned ordinary API10
entry/store/damage-return/API-return control. Before either request the
adapter checks c2/c4/latches8010D080/84/c40 zero and the original effect tuple;
before the dose it revalidates canonical ownership, slot generation, DAT,
relocated name lookup, NPC/actor, detail/mode/health address and current HP.
Changed identity inhibits the request with a field-specific report. Generic
TELE remains disabled. After the actual named write, the callback readback and
explicit original getter must agree; SIGSTOP then runner SIGKILL ends the run.
Level3 helpers remain byte-identical; the level4 saved loss capture produces
identical analyzer output. No guest health/counter stores or default changes.

Run `scratch/agent/m6/g1_lvl5s6677_lvl5_loss/`:107.76s total runner wall,
VI4696..6508,0 crash lines. Off/on atVI4696/6498; off2 intentionally not
reached. Wedge DAT8031BCCC,slot87/gen1,node8021B6DC,NPC8035421C,
actor80354898,handler800D93C0,detail0/mode0,health array8031BD38.
Both API requests use original message80165E80 and the same owned identity.

| Link | run.log line | Actual observation |
| --- | --- | --- |
| Owned mark-all controls |210578 /231039|arms0/1, HP200, same node/actor/storage|
| Ordinary API / entry / actual store / returns |231041 /231047 /231051 /231055 /231057|VI6498, request10, F2148 health200→190, both returns190|
| Original getter40 after ordinary |231169|returned0=memory0 before dose|
| Dose API / entry / actual store / return |231171 /231175 /231179 /231183|VI6503, request191, F2148 health190→−1, damage returns−1|
| Original death effect / counter writer |231216 /231220|D9D28 tuple(40,1,0,0,0,1);6594C id40 0→1, exact NPC/DAT|
| API return |231222|−1, c40=1|
| Callback / original getter / done |231334 /231335 /231336|VI6508, actual readback0→1, getter1=memory1; c2/c4/latches all0|

H-death selected for this victim: the registered same-owned request crosses
zero, invokes the original effect and changes the named friendly-loss count.
H-route/H-identity are not observed for these two requests. The ordinary hit
alone did not change objectives; the dose's actual counter40 getter0→1
supplies the epoch's changing-value sensitivity control. Owned mark-all
controls fire in both reached arms. No silent counter is treated as a null.
Dynamic causality remains single-flight/single-source; original ELF/DAT
corroborate contracts, not live retail behavior. No player-shot, game-invoked
friendlies reader, historical id2 attribution, win/progression, retail-equivalence
or full VERIFIED claim. Named level5 loss-response unit closes.

ORIGIN: original dealDamageToNpc800F2120 legitimately stores accepted message
damage subtracted from the selected health array atF2148. Original wingman
death effectD9D28 consumes Wedge's DAT tuple; original6594C legitimately
increments counter40. No corruption mitigation or compensating store added.

Validation: build and analyzer fixtures pass, including every missing loss
chain link, named definition/selector, ordinary control, storage/identity,
dose HP/count, effect tuple, writer/getter and safety negatives. All13 adapter
outputs are idempotent; level5 hook-free replay is byte-exact. All6 manifest
hashes still match after collection. No lib edit or new queued-soak verdict
(latest20261028-075640 already consumed). Proof:
`scratch/agent/s6677_qualification.json`; original assertions/mutations:
`s6677_lvl5_original.json`; replay:`s6677_replay.json`; prior-level analyzer
regression:`s6677_lvl4_regression.json`; build/self-test logs:`s6677_build.log`
and`s6677_selftest.log`.

Reproduce:

```sh
python3 tools/g1_dat_inventory.py --level 5 --check-level5 --mutation-check-level5 --output scratch/agent/s6677_lvl5_original.json
python3 tools/apply_s6657_objective_response.py ../N64Recomp/RecompiledFuncs
cmake --build build --target RogueSquadron64Recomp -j6
python3 tools/g1_objective_response_run.py --self-test
env ROGUESQ_OBJECTIVE_RESPONSE_LETHAL=1 python3 tools/g1_objective_response_run.py <fresh-tag> --level 5
```

Next: original-backed level6 named objective/target contract, before any live
instrument. The historical silent level6 heartbeat is not a value control.

## Session 6678: level6 original two-counter target contract

ONE bounded offline tool change; no game build/run. Ground truth is original
ELF SHA256 `f6809909002b407b339ca0331e54faea895ac2730f15152ab5221307442f6cc9`
and retail `level/lv_6/dat`, ROM `009662C8`, decoded length78648, SHA256
`a5c2a4a2882a4e3efc5a44844526517e99387cf827536ec7bd2cd224d9188703`.
These establish static code/data contracts, not independent live causality.

Original callback80104210..80104398 reads counters34..39/98/50/99 and
Booleans98/99/40/125/11. Any c34..39==1 sets Bit4, plays voice101 and
returns early. c98==6 with Boolean98==0 sets that Boolean, increments99
and completes objective1. c50==4 with Boolean99==0 sets that Boolean and
increments99. Boolean40/125 complete objectives2/3. c99==2 with Boolean11==0
sets that Boolean and Bit8. Equality thresholds are exact, not >=. Original
reader80104444 and slot8010443C both return0 without counter reads. Do not
borrow the level5 friendlies arithmetic. Counter40 and Boolean40 are distinct;
the callback does not read counter40. The old fifteen-counter heartbeat was
outside this callback's counter set; it remains no changing-value control.

| Retail definition | DAT offset | subtype | nominal detail0 HP | effect (counter,delta,Boolean,value,counter2,delta2) | disposition |
|---|---|---|---|---|---|
| OBJ_ConYard_Barracks | 4A2C | 14 | 500 | (50,1,0,0,90,1) | ordinary-probe candidate; second counter90 unresolved |
| OBJ_Factory_01 | 0AF4 | 14 | 650 | (50,1,125,1,90,1) | direct objective Boolean125 coupling |
| OBJ_Hangar_01 | 17A8 | 14 | 500 | (50,1,121,1,90,1) | Boolean121 coupling |
| OBJ_Hangar_02 | 2274 | 14 | 750 | (50,1,40,1,91,1) | direct objective Boolean40 coupling |

Offsets/subtypes in the table are hexadecimal. All four have DAT+a0=0 and
halfword+8A=1. Wingman_01/02 have zero effect counters/Boolean. Radar_Dish
subtype2A has raw+80=98, but its layout/handler is unqualified; its raw words
must not be interpreted as a subtype14 effect. This is not an exhaustive
proof that no other safely isolated level6 target exists.

Original setup table8003BDD8 selects800653F4 for subtype14, then handler
8006CBB0; setup stores descriptor at payload+34. Message5 table8003CA30
selects8006CF88, with payload=node+4 and health DAT+6C+4*word80137CE4.
Require live detail0: other detail indices alias raw effect words and are not
qualified here. Prehealth<=0 skips at8006CFA4. DAT+a0 nonzero can suppress
subtraction for a player-source message; selected DAT+a0=0 removes that
specific source gate. Actual subtraction/store8006CFE4/E8 uses unsigned
message halfword+6. Posthealth>0 at8006D278 skips death effect. Global
byte80130B39 nonzero at8006D6BC/C0 also skips it. Otherwise call8006D6F0
loads all six DAT effect fields; original6594C increments counter50 and
65974 increments90 for Barracks, with no Boolean store. This names the
writers and the legitimate two-counter effect; it does not prove live execution.
FFFF named-API fallback differs: C74AC subtracts and C74E0 applies subtype14
effect without a death threshold. Never pool that route with registered message5.

H-coupled selected for the Barracks definition; a single-counter interpretation
is rejected. H-layout is statically resolved only for subtype14. Live availability,
source/global gates and counter90 downstream consumers stay open. No lethal
admission, objective-response claim, retail behavioral equivalence or VERIFIED
promotion. No default/runtime/lib change; no new queued-soak verdicts.

Validation: `tools/g1_dat_inventory.py --level 6 --check-level6
--mutation-check-level6 --output scratch/agent/s6678_lvl6_contract.json` passes
294 literal original-ELF anchors and334 mutated negatives: each anchor and
10 fields on each of four DAT definitions, including counter2, detail/setup
word88 and source-gate wordA0. Direct `struct.unpack_from` plus name checks
cross-check all four DAT tuples independently of inventory semantic decoding.
All19 pre/post inventories and complete prior level5 contract are identical;
level2/3/4/5 contract regressions, level4/5 mutation suites and objective-runner
self-tests pass. Proof `scratch/agent/s6678_validation.json`.
Next: one original named API10 on live owned Barracks with HP>10/detail0,
join registered handler/message/actual health store and return, original getters
50/90 and changing-value controls. Keep lethal and generic TELE disabled.

## Session 6679: level6 ordinary admission is unregistered; response untested

Bounded opt-in adapter/analyzer change and one corrected single-flight capture.
`tools/apply_s6657_objective_response.py` admits level6, records original Barracks
lookup/registration/ownership/generation/detail/source/effect gates, and permits
at most one named API10 on an owned subtype14 instance with detail0 and HP>10.
Generic TELE and every lethal branch remain disabled for level6. Registered
message5 entry/store/effect/return and FFFF fallback hooks carry exact identities;
all128 original getters expose50/90 plus actual changing-value controls.
The analyzer keeps exact health-chain qualification separate from owned mark-all
and getter sensitivity. Fixtures reject missing links, wrong identity, route,
detail, generation, source, health address, dose, return, duplicate request,
fallback/effect and missing controls. No direct health/counter stores.

Ground truth preceded instrumentation: original ELF/DAT294 anchors and334
mutations pass. Additional8 literal original instructions, independently decoded
by GNU objdump, establish that message5 returns status1 (D754 delay slot),
whereas original API C7474..C7488 returns detail-indexed remaining health. These
are distinct returns, not interchangeable. Original ELF/DAT establish contracts,
not an independent live witness.

Corrected unlocked run `g1_lvl6s6679_lvl6_ordinary_v2`: 184.02s total runner
wall, first epoch VI5744..11154, done dv5410 selected1 flight1,
0 crash lines, reached arms0/1/2, no generic forces, no API requests, no
registered health/effect chain or fallback. Admission samples: VI5745/arm0, VI7614/arm1, VI9949/arm2.
Every sample has base8031B9B0, desc803203DC, name80320484, lookup==desc,
subtype20(decimal), detail0, HP500, source/effect gates0, valid free-list1;
slot65535/FFFF, generation0, node/NPC/handler0, owned0. Thus the checked
registration field inhibits the request. Do not infer whole-world absence from
these sampled callbacks or assume that an offscreen Barracks is defective.

Original getters match memory and actually change for ids20,21,64,65,66,67,98;
10 callback changing-value readbacks are observed. Shared local selector
fixtures accept the original50/90 tuple and reject the Boolean-mutated tuple,
but those are local fixtures, not a target ownership control. The actual owned
Barracks mark-all control never fires. `qualified_health_chain` and
`qualified_ordinary` are both false. No surviving-health/counter null, hit-driven
objective response, player-shot proof, retail equivalence or VERIFIED promotion.
H-ownership is observed at the admission checks; registered-vs-fallback health
behavior was not exercised. Live evidence remains single-source.

First capture `g1_lvl6s6679_lvl6_ordinary` is retained separately:248.78s wall,
epoch starts5833, same unregistered state in all3 arms,0 requests/0 crashes. Its
shared census continued after lv6 callbacks stopped and later DAT-load reports
were outside flight; doneVI15119/dv9286 is NOT a first-flight duration.
ORIGIN: slotDispatcherIter legitimately keeps invoking rs6663_scan after the
mission callback stops; the scan inherited `started` without checking current
flight. Level6 now calls the flight gate before each census scan. This changes
diagnostic lifetime only; no guest guard or object restoration. Fixed build and
fresh v2 capture above close the epoch at the actual checked boundary. Do not
pool first-run late rows with corrected flight evidence. Exact first-run adapter
snapshot matches its launch hash; v2 all6 current launch hashes match.

Validation: both builds complete, runner fixtures and level3/4/5 original-contract
regressions pass. All13 outputs are idempotent; all3 new hook-free replays are
byte-exact, and qualified level3/4/5 helper bodies are unchanged. The adapter
is already included by the vendored fixup sequence. Additional original-return
assertions and full proof are in `scratch/agent/s6679_qualification.json`;
`original_handler_return.txt`/`original_api_return.txt` use the s6679 prefix.
No library edits, default changes or new queued-soak verdicts.

Next: original counter90 consumer/use graph plus FFFF-route effect safety
contract, recovering known c50->99->Bit8 as the positive control. No fallback
or lethal admission until that contract is qualified. Do not repeat this hold.


## s6680 — level6 counter90 and FFFF-route safety audit (2026-10-31)

ONE bounded original-backed tool change; no runtime build or game run. The
admission boundary from s6679 is retained: named Barracks resolves but is
unregistered, so no ordinary request was issued. The new flags are
`--check-level6-safety` and `--mutation-check-level6-safety` on
`tools/g1_dat_inventory.py`. They preserve the existing level6 contract and
add original instruction assertions, a classified base-site census, typed DAT
conditions, direct getter-call selectors, and bounded execution of the original
integer instructions. Presentation/audio calls in that slice are recorded stubs;
this is a static fixture, not an independent emulator or live-game result.

| Discriminator | Original-backed result | Limit |
| --- | --- | --- |
| Known c50 -> c99 -> Bit8 control | c50=3/c99=1 yields no Bit8; c50=4/c99=1 sets Boolean99, increments c99 to2, sets Boolean11 and Bit8 | Integer slice with mission-state HUD gate initialized0 |
| Latch / other stage / failure controls | Boolean99=1 inhibits repeat increment; c50=4 alone increments c99 to1; c98=6 plus c50=4 reaches2; c34=1 takes Bit4 early return | Synthetic initial states, no live baseline claim |
| FFFF nonlethal request | Original C748C..74E4 and65914..6597C, subtype14, detail0: API10 writes HP500->490 and counters50/90 each0->1 | Effects are eager, independent of death threshold |
| FFFF gate margin | With c50=3/c99=1, same API10 reaches c50=4, then original callback sets Bit8 | Demonstrates a possible terminal coupling, not the captured flight's baseline |
| Counter-base materialization census | All30 ADDIU-immediate8060 candidates in resident text plus mission classified as reads, effects, public helpers or initialization | No complete pointer/alias proof; shifted bases not excluded |
| Direct getter calls | All125 JAL800C761C sites have locally recoverable constant selectors; none90 | Direct calls only; computed readers remain explicit |
| Typed DAT condition census | Original switch8003C140 selects +64/+68 or +38/+3C layouts for167 level6 records:154 disabled,13 use14/16/17/18/19 at threshold1; none90 | Only this audited condition family, not all DAT/script readers |
| Script reader | Original table800A8A20 opcode3 dispatches339C; F33BC reads a counter whose index is trunc.w.s(record+58+16*i), threshold at+5C | Effect-context+24 constructor and retail record ownership unresolved |
| Handle reader | Original FA07C/FA0AC read record+6 counter against signed record+8; mode0 >=, mode1 <, then indirect callback | Level6 initializer supplies20/21/13/0; other producers/reachability unqualified |

**H-unresolved selected.** Neither H-terminal nor H-tally is established for
counter90. The c50 coupling already prevents treating repeated fallback hits as
ordinary health-only probes. No fallback request, lethal dose, direct store,
mission win/progression or VERIFIED promotion is admitted. Original ELF and
retail DAT corroborate static contracts; execution of those ELF bytes is the
same source and does not supply a second independent dynamic witness. The
scoped missing90 results must not become “counter90 unused.”

Evidence: `scratch/agent/s6680_safety.json`, `s6680_validation.json` and
`s6680_validation.log`; original objdump files `s6680_{all,mission}_disasm.txt`.
Run the safety tool with both new flags for reproducibility. Safety checks pass996 original anchors and1048 rejected mutations, including
12 typed selector/threshold substitutions to90. Existing level2..6 contracts,
all19 DAT inventories and analyzer fixtures pass separately; prior level3..6
contract objects compare identical to HEAD.
The first validation harness incorrectly applied the level4+ generic DAT mutation
runner to level3; its malformed subtype raises KeyError rather than ValueError.
The corrected harness tests level3's original instruction mutations directly;
no production behavior changed for that harness error. No new soak verdicts,
lib changes, runtime defaults, or game-run evidence in this unit.

Next single unit: trace the original effect-context+24 constructor through
executeActorType1Effect -> resolveScriptedNameTokenList, prove the record bounds
and typed retail level6 ownership, and classify each opcode3 selector and chosen
DAT target. Keep all other computed edges explicit; no damage run.

## s6681 — level6 type3 script ownership and bounded selector census

ONE bounded extension of `tools/g1_dat_inventory.py`, flags
`--check-level6-scripts --mutation-check-level6-scripts --level 6`.
No game build/run, request, lethal dose, direct stores or win/progression.
No new queued-soak verdicts (latest20261028-075640 already consumed).

H-DAT / H-derived / H-computed discriminator: original constructor source ->
context+24 -> inline slot bounds -> opcode3 -> retail token and DAT target.
**H-DAT selected for kind3/subtype3 sources.** Both original constructors
F94A0/F9698 store unmodified a1 in context+24, context=actor+8. Example original
wingman path D9604..9658 resolves DAT+94 relative name through
getLevelDatItemByName, passes its result as constructor a1. Loader46ABC..6B40
uses header18/1C count/table, table-relative record addresses, relocates
record0C/20/2C only in this loop. Inline scripts and token offsets stay relative.
Resolver sets context28 from named lookup; executorF43F0 moves it to context24.
This is a static ownership contract, not observed activation or a proof that
every constructor argument is subtype3. Arbitrary named API inputs and other
record kinds remain outside the census.

| Measurement | Result | Limit |
| --- | --- | --- |
| Original loop bound | F3494 SLTI v0,s4,8; slots54+16*i throughD3 | NEXT's proposed field50 count was wrong;0/1 values resembled a count, but are not read as one here |
| Every level6 kind3/subtype3 record |21 records,168 slots;0 opcode3 slots | Overapproximates possible scans, not a live reachability proof |
| Active opcodes | ATAT_Spline_01 op5 -> ATAT_Spline_02; Wingman_Spline_01 op5 -> Wingman_Loop; Shuttle_Escape_01 op6 | Both named targets uniquely join kind3/subtype3; no other nonzero opcodes |
| Completion effects | All21 record40 counter and48 Boolean selectors0 | Only this executor's direct completion fields |
| Retail nonzero control | Level1 x_wing_vs_probe_d+4840: op3 counter10>=3 -> x_wing_to_rendezvous+49C4 | Static decoder control, no new runtime control |
| Sensitivity/bounds | Synthetic selector90 detected;10.75 truncates10;-1.75 truncates-1 and skips read;0 skips; counter90 in eighth slot detected | Synthetic bytes test decoder; not independent hardware execution |
| Rejections | Token offset in header/OOB and nonfinite selector rejected; all168 slot opcode mutations rejected | Qualified float domain only |
| Regression |1282 ELF anchors,1502 rejected mutations; direct struct cross-check168 slots; field50=FFFFFFFF leaves slots unchanged | Mutation execution uses the same ELF/data sources |

The pipe-list helperF30AC skips the leading byte before copying the selected
name; raw token searches that include that byte misidentify names. The decoder
retains all slot indices, operand words, typed selectors, relative offsets and
target matches in the report. Original opcode3 ignores nonpositive selectors;
positive selectors read counters and compare against trunc.w.s(threshold).

Original ELF instructions and retail DAT bytes corroborate static format and
content. The decoder/mutation fixtures are same-source; no independent dynamic
causal, retail-equivalence, complete counter90-absence or VERIFIED claim follows.
Other computed NPC/actor/radar/music/handle readers remain unresolved, and FFFF
API10 remains inadmissible because its eager c50/90 coupling is unchanged.

Evidence: `scratch/agent/s6681_scripts.json`, `s6681_validation.json`,
`s6681_baseline.json`, `s6681_level2.json`, original
`s6681_{mission,dat}_disasm.txt`. All19 inventories and prior level3..6/safety
contract objects compare identical to HEAD; level2 assertions and objective
analyzer self-tests pass. Neither already-dirty lib submodule was edited.
Next unit: spline events through F4660..46AC remap into kind7 records consumed
by updateNpcEffectIntensity; classify +2C counter condition and +34 effect.


## s6682 — level6 spline-event remap and common counter prefix

ONE bounded extension of `tools/g1_dat_inventory.py`, flags
`--level 6 --check-level6-events --mutation-check-level6-events`.
No runtime build/run, fallback request, lethal dose, direct stores or win gate.
No new queued-soak verdicts; latest20261028-075640 already consumed.

H-typed / H-derived / H-computed discriminator: original spline source ->
stride8 event -> record-relative remap -> kind7 table entry -> unshifted
updateNpcEffectIntensity input. **H-typed selected for the level6 kind3/subtype3
file inputs.** Original F4660..46AC reads context24, source28 count/source2C
relocated event array, unsigned event+6 index, remap at source+D4+word(D8),
unsigned remap+2 target index, DAT header3C table, then passes the entire target
record as a1. Loader46C24..6C88 relocates the table-relative kind7 records and
names, leaving selectors unchanged. The record's remap kind halfword is7 in
every selected entry; the consumer itself reads only its index halfword.

Original F3CB0..3D80 processes the common prefix BEFORE subtype dispatch at
F3D84: +28 Boolean gate; +2C counter selector with signed +30 threshold;
+34 counter selector incremented by +38; +3C Boolean set from byte+43.
Subtype-specific effects remain outside this closure. Field values in the
report retain raw words. A zero selector disables its common counter access.

| Spline | Event order -> kind7 table indices | Subtypes (decimal) |
| --- | --- | --- |
| Wingman_Spline_01 |46,47 |27,27 |
| Shuttle_Escape_01 |42,39,38,40,41 |34,27,26,27,27 |
| AT_ST_Spline_01 |44 |34 |
| AT_ST_Spline_02 |45 |34 |
| Hangar_ATST_Spline_01 |48 |34 |

All21 type3 records are decoded;5 have events,10 events total,10 distinct
targets. Every selected target has common tuple(0,0,0,0,1,0,1) at28..40:
Boolean/counter gates and common counter/Boolean writes disabled. Thus this
specific static family neither reads nor increments90 through the common
prefix. Every event span lies inside its source record; each event index is
within the remap span; each target is an owned kind7 table entry. The remap
span described by D4/D8 ends exactly at source20's point-array start. These
are offline file bounds, NOT checks enforced by the original consumer, nor
proof that all possible constructor arguments are typed spline records.

Same-command retail positive controls in level3: Madine_TO event0 remap0 ->
kind7[88], subtype34, common condition counter26>=3; CS_New_Wedge event0
remap1 -> kind7[54], subtype26, common effect counter16+=1. Synthetic90 is
observed in both exact fields; zero disables each. Seven malformed fixtures
reject event/remap spans, remap count, event index, kind, target index and
nonfinite time. Direct struct reads independently cross-check all10 original
level6 record joins/7-word tuples without calling the event decoder; these
remain same-data verification, not an independent live witness.

1399 original instruction assertions and1798 rejected mutations pass, including
original/safety/script regressions and active event ownership/prefix fields.
All19 inventories and six prior contract objects(level3/4/5/6/safety/scripts)
compare identical to pre-change HEAD. Existing level2 checks, original script
controls and objective analyzer self-tests pass. Initial mutation run correctly
accepted a changed source2C in a zero-event record: that pointer is unused.
The mutation suite was corrected to require rejection only for active event
pointers, then rerun completely; no decoder/runtime guard was added for it.

Original ELF plus retail DAT establish static format/content. Decoder execution,
struct cross-check and mutations use those same sources; no independent dynamic
activation, full counter90 safety, retail-equivalence or VERIFIED claim follows.
FFFF API10's eager c50/90 coupling stays inadmissible. NPC/actor/radar/music,
other handle producers and arbitrary constructor arguments remain unresolved.
Neither already-dirty lib submodule was edited; retail defaults unchanged.

Evidence: scratch/agent/s6682_events.json, s6682_validation.json,
s6682_baseline.json, s6682_level2.json. Next: original-backed ownership of the
two pending-song counter readers, including descriptor/queue copying and a
nonzero typed retail control; no repeat admission hold.


## s6683 — level6 pending-song counter90 ownership qualified statically

ONE bounded extension of `tools/g1_dat_inventory.py`, no game build/run.
H-typed selected for the qualified original family; H-derived is rejected for
its selector copies. Arbitrary descriptor producers/aliases remain H-computed.

Original loader46B44..6C20 relocates kind6(header30/34) records/names, not
condition fields; loader4723C..7280 sends flag34 bit80 records to setup.
Subtype16 selects table8003BDC8 ->65558 -> ECC28; spawn uses the unmodified
DAT pointer. ConstructorECC84 stores it at payload+4. Action3 ECD30..D90
checks DAT84/88 Boolean and8C/90 counter, then ticks that payload. TickEC6F0
makes enter/exit stack requests; both paths copy DAT bytes97/9B/9F and
wordA0 into request33/34/35/38. EF724..748 copies those into C230+29/2A/2B/2C;
EE064 selects C230 as s0; EE16C..1A0 stores globals8010C2F5/F6/F7/F8.
Selector is an unsigned BYTE (low byte of DAT9C); threshold a signed word.
C170's 0x24-byte song config copies are separate from C230 conditions;
EED7C builds background-song config, not this condition payload. Full alias/
indirect-producer closure is not claimed.

| kind6/subtype16 owner | index / DAT offset | pending counter | signed threshold | original reader switch condition |
| --- | --- | --- | --- | --- |
| MUSICRNG_ATATs |132 / FDDC |90 |−3 |c90 < 3 |
| MUSICRNG_ATSTs |134 / FED8 |91 |−1 |c91 < 1 |
| MUSICRNG_LevelSettings |136 / FFD4 |0 |0 |both selectors disabled: returns0 |

All3 have eager-spawn bit80, handler Boolean0/value1/counter0/threshold0,
pending Boolean0/value1. Their live spatial entry/exit and pending state
remain unobserved. EDC44's signed comparison/branch returns1 BELOW the
magnitude of a negative threshold; a nonnegative threshold returns1 at
count>=threshold. NEXT.md's tentative negative wording described waiting,
not the actual switch return; branches now establish polarity explicitly.
No prior CURRENT-TRUTH conclusion is overturned: counter90 was unresolved,
never proven unused. The original eager Barracks effect's c90 increment can
change this music condition at2→3. Its coupled c50 success-stage effect
remains a separate reason not to admit fallback requests.

New flags `--check-level6-music` / `--mutation-check-level6-music` qualify
1587 total original anchors; all1587 independently compared byte-for-byte
with their retail ROM text/mission offsets,0 mismatches.2013 instruction/DAT
mutations reject, including all27 checked level6 music gate/selector fields.
Original selected transfer slices plus the complete EDBB0 reader execute
15 level6 boundary cases (counts0..4 on each owner). A same-command retail
level1 MUSICRNG_Zone01 control copies selector110/threshold−3 and returns1
at2. Ten additional slice fixtures test synthetic90, both threshold signs,
equality, disabled selectors, pending-state gating, Boolean match/mismatch,
and byte truncation(0x1234005A→90). Synthetic90 also passes the typed DAT
decoder, and a short owner rejects. This is same-source static execution;
it is NOT a dynamic independent witness or a full scheduler/spatial replay.

All19 inventories and seven prior contract objects(level3/4/5/6/safety/scripts/
events) compare identical to pre-change HEAD. Existing level2 assertions,
objective analyzer fixtures, Python compilation and diff whitespace checks
pass. No failed run, new soak verdict, mitigation, default/lib change,
VERIFIED promotion, live fallback/lethal request or mission-win test.

Evidence: scratch/agent/s6683_music.json, s6683_validation.json,
s6683_baseline.json, s6683_level2.json. Counter90 safety remains partial:
other NPC/actor/radar/handle readers, runtime aliases and dynamic activation
are open. Park that boundary without repeat admission holds; move coverage
to the next missing named objective contract, level7 (historical id2 has no
proven level7 meaning). No complete consumer-absence claim follows.


## s6684 — level7 original named counter20 contract (2026-10-31)

One bounded extension of `tools/g1_dat_inventory.py`; no game build/run.
The retail ROM and original ELF, rather than the recompiled runtime, supply
all instructions and target definitions. This is **single-source static
qualification**: ROM, ELF, DAT and decoder checks share original lineage.
No live response, player-shot, retail-equivalence or VERIFIED claim.

Original callback801044E0..80104A08 reads counters20/30/40/99 and
Booleans97/98/99/106. For each stage, a zero Boolean latch permits exactly
one counter99 increment, objective-slot activation, and two Boolean writes:

| Counter threshold | Latch Boolean | Completed slot | Extra Boolean |
|---|---|---|---|
| c20 >= 21 | 97 | 2 | 120 |
| c30 >= 10 | 98 | 1 | 121 |
| c40 >= 6 | 99 | 3 | 122 |

At c99>=3 it calls setHudEnableBit8. There is no Bit4/failure call in this
callback; that is not a global assertion that the mission cannot fail.
Exactly one of Booleans97/98/99 also triggers the corresponding61/64/67
notification behind latch words8010D098/90/94. c40>=6 AND c30>=10 with
Boolean106==0 and word8010D09C==0 sets Boolean41. Near-completion cases
(c20==19 with B98/B99, c30==8 with B97/B99, c40==4 with B97/B98) set
Boolean50 behind shared word8010D0A0. Here the paired Booleans must equal1.
Friendlies reader80104A60..A9C unusually reads counter128 twice and passes
negative sum to setFriendliesSaved. Preserve both calls; do not simplify
an observed runtime value or invent friendly-loss semantics. Neither reader
uses counter2. Historical id2 activity remains unrelated evidence.

| Retail DAT name | Offset | Subtype | Detail0 HP | Effect (counter,delta,Boolean,value,counter2,delta2) | Decision |
|---|---|---|---|---|---|
| 20_Dest_Tanks_01 | 05D0 | 0x14 | 50 | (20,1,0,0,0,1) | selected |
| 20_Dest_Tanks_03 | 0754 | 0x14 | 50 | (20,1,0,0,0,1) | alternate |
| 20_Dest_Tanks_04 | 0818 | 0x14 | 50 | (20,1,0,0,0,1) | alternate |
| 40_Destroy_Imp_Barracks_03 | 0B90 | 0x14 | 100 | (40,1,28,1,0,1) | Boolean coupling |
| 20_Spaceport_02 | 18B8 | 0x14 | 300 | (20,1,106,1,0,1) | callback Boolean coupling |
| 30_Sensor_Array_Main | 1F94 | 0x14 | 100 | (30,1,2,1,0,1) | Boolean coupling |

All six checked definitions have detail word88=1 and source-immunity wordA0=0.
Original setup table8003BDD8 ->653F4 ->handler6CBB0; message5 table8003CA30
->6CF88. Node+4 is payload; payload+34 points at DAT. Selected detail health
is DAT+6C+4*detail. Prehealth<=0 exits at6CFA4. A nonzero DAT+A0 enables
source-player immunity; otherwise actual store6CFE8 subtracts message+6.
Positive posthealth exits at6D278 before effect6D6F0. Global byte80130B39
can suppress the effect. Original writer6594C increments the first counter;
second selector0 disables its unused delta1. The FFFF API fallback atC748C
instead applies the effect after subtraction without a death threshold.
Live registration, ownership, detail, health and gates are unobserved; no
fallback or lethal admission follows from this static contract.

H-named selects a counter20-only candidate whose callback meaning is checked;
H-coupled applies to the excluded Boolean-bearing targets and eager fallback.
H-unresolved remains for live availability/ownership. One future ordinary
API10 request must use the original named lookup, valid registered ownership,
and a surviving target. Do not set counters/health directly, trigger a stage
threshold or attempt a win. No inference that the tank definition is mobile.

Validation: --check-level7/--mutation-check-level7 checks538 original anchors,
all538 byte-match retail ROM at pc-80000000+C00;598 one-field/instruction
mutations reject. Six raw struct tuples agree with typed retail decoder
controls (counter20 and nonzero Booleans28/106/2); this is not a live null
control. All19 inventories and eight earlier contract objects are unchanged.
Level2 checks, level6 music regression, full response-analyzer self-tests,
Python compilation and whitespace checks pass. Initial regression equality
failed because saved JSON stringifies integer keys in slice maps; normalize
both sides through JSON, rerun all eight, identical. No tool/runtime behavior
was changed to accommodate that comparison. No new soak verdicts/defaults/
lib edits. Evidence: scratch/agent/s6684_level7_checked.json,
s6684_validation.json, s6684_baseline.json, s6684_lv7_contract.txt.
