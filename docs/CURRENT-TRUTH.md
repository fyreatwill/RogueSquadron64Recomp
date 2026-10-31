# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 6676 (2026-10-31).
`PORTING-STATE.md` is the chronological ledger. Historical detail, the
retired backlog, and the verbatim s6378-s6551 body of this file are in
`docs/PROJECT-OVERVIEW.md` ("Migrated from CURRENT-TRUTH (s6552 maintenance)"
and "Archive: CURRENT-TRUTH body s6378-s6551"). Per-level framebuffer
evidence, duplicate coverage notes and historical backlog/update chains from
s6632–s6666 were migrated in s6667 to the linked maintenance archive below.

## Headline

- The qualified route boots attribution, N64 logo, intro, Factor 5 logo, title,
  hangar, and mission origins; mission input reaches flight code.
- M5 audio de-stubbing, M3 idiom audits, generated-symbol renaming (G5), M6
  first-mission endurance (3x600 s lvl1/5/7, s6442), and G2 audio are closed.
  G4 crash hunting is parked after clean coverage. G1 is mission coverage and
  visual quality, not autopilot work.
- **Active thread closed: G1d 21:9 level-select tear (g1d-levelselect-heap).**
  s6631. The wide gap punch in `buildHeapFreeList` places the `8010FEFC`
  free-tail header exactly on `801163E4`. A walker that stops at `a >= e4`
  never cuts it (first binary, `did=0`, overlap unchanged). The fix, aspect
  > 4:3 only, shortens the previous block and plants the terminator at
  `e4-0x10`. It does not write the image and does not run at 4:3. Second
  binary, both widths, screen unlocked: level-select `did=3`. 21:9
  `e4=0x80B56000` head `0x80961000` cut `0x80A0AFF0` oldsz `0x14B000` newsz
  `0x14AFF0`; heap end becomes `0x80B56000`. 16:9 end becomes `0x80B7BD80`.
  Neither width has a malloc covering `0xBB0020`. The 21:9 zlib `0x8000`
  block ends at `0xB53A20`, below the image. The upload word is
  `0xFFFCFFFC`, not the memset zero. 16:9 45.9 s / 50 frames, fail [];
  21:9 45.2 s / 54, fail [] (edge-px and dy reasons gone; dy180 20.11,
  edges 46.72/31.59). Both floor_frac 1.0, alive, rc -9, 0 crashes.
  Evidence: `scratch/agent/s6631_heapcap_at/`. Pre-fix baseline remains
  s6630. Do not skip `rs_memset` or restore depth. OS window stays 640x480.
- **G3c (owner visual report): engineering closed, owner judgement pending.**
  (a) far-edge stair: no opt-in rougher than retail (s6449, s6544);
  (b) spike wedges: H-hw-draws, angrylion lights the same 16/79 wedges
  (s6454), `ROGUESQ_CULL_SPIKE` stays opt-in; (c) turning shake: retail 30 fps
  judder (s6455, s6458).
- **G1d (aspect): level-select floor tear closed (s6631).** Flight radar
  inset matches retail (s6610). Extra width is real scene and the left HUD
  stays pinned. Heap `8010FEFC` now stops at the depth pointer when aspect
  is wider than 4:3. The OS window stays 640x480, so wider modes letterbox.
  Do not return to the combiner or the pixel pipe.
- **G1e (frame rate): closed** (retail ~30 fps vs FPS60 ~59, s6452).
- **G1(c) framebuffer presence covered for levels 0..18.** Level 1 has a
  retail flight match; the remaining evidence establishes content presence,
  not retail equivalence. Saved level-0 port images are duplicate pixels
  from one crop; its retail level identity is unresolved. Numeric rules,
  near-misses and inspected sheets are retained in
  [G1-FRAMEBUFFER-COVERAGE](G1-FRAMEBUFFER-COVERAGE.md) and
  [the s6667 migration](PROJECT-OVERVIEW.md#maintenance-s6667-retained-evidence).
  Classifier controls reject title/craft-select; phase ordinals alone do not
  identify flight (levels 16–18 can remain phase 5). Objective(d) stays partial.

- **G1(d) saved evidence reconciled (s6656), still partial.** New tool
  `tools/g1_objective_evidence.py --check` streams 18 ctl/TELE gzip logs
  plus legacy s5843–s5845, using only the first explicit flight-width epoch.
  All 18 pair selectors match. Actual lvl7 id2 and lvl8 id6 changes are
  positive controls; lvl9 baseline ids match in both arms. Lvl7 id2 goes
  0>2>3>0; lvl8 id6 goes 0>1>2>3>4 (its reset is after the first epoch).
  Shared end requests do not prove a hit-driven end gate. Lvl6 heartbeat
  proves execution only, so its silent value monitor is NOT a controlled
  null. Single-source static read: lvl7 itself tests ids 20/30/40/99,
  outside the old monitor's 1–15 slots; id2 meaning is not established for
  lvl7. Saved lvl1 ctl contains objsnap while tele does not: paths were
  reused across builds, so historical arm identity cannot be assumed.
  Legacy lvl0 logs name lv0_checkComplexObjectives and show counter1
  pre-states 0..3 ctl versus 0..12/0..16 TELE; cross-run, single-source.
  Forced-selector lvl0 ctl/tele and lvl10–18 pairs are absent in this set,
  not negative results. No level promoted to fully VERIFIED. Full table,
  semantics and line provenance: `docs/G1-OBJECTIVE-RESPONSE.md`.
  That was the s6656 handoff; s6657 below now supplies the forced-route
  lvl0 counter1 witness. No new soak
  verdicts; no runtime/default change in s6656.

- **G1(d) level 0 forced-route counter1 response observed (s6657).**
  One corrected flight, B40=0/cursor0 plus lv0 callback, first flight epoch
  VI4672..10074. Off/on/off c1 0→2→13→13; 77 forced segments in on only,
  13 actual changing-value readbacks, 0 crash lines, 167.87 s wall. Eight
  exact force→accepted SEND→store triads match node, NPC payload and
  descriptor; actual writer is datItemSetObjectiveBooleanCount at
  0x8006594C, each +1. Example seq24: node8021B22C, payload80356230,
  descriptor8031AA94, c1 4→5 after 4 VI. Original ELF independently shows
  node+4→payload, payload+0x34→descriptor and descriptor+0x70/+0x74→
  counter/delta. First binary's node+0x34 join was wrong; rerun corrected
  it before interpretation. Dynamic chain remains single-source, not
  retail equivalence or player-shot proof (example SEND is N). c1 stops
  at13, below lv0's21 gate; c2/c3 stay0. No win/progression tested or full
  VERIFIED promotion. Durable adapter: tools/apply_s6657_objective_response.py;
  runner/analyzer: tools/g1_objective_response_run.py. Table and limits:
  docs/G1-OBJECTIVE-RESPONSE.md. Next missing named response is level1.

- **G1(d) level 1: generic forced victims hit id10, not the named loss counters (s6659).**
  Corrected single-flight off/on/off, B40=1 plus lv1 callback, VI5271..10674,
  176.59 s, 25 forces, 0 crashes. Two exact force→N SEND→pc8006594c→readback
  chains increment id10 6→7 and7→8. Eight actual id10 readback changes are
  the live value-detection control. ids13/40/41 and Boolean6 remain0.
  Original ELF: friendlies saved=19-(c40+c13+c41), c13>=5 fails;
  Boolean6 completes. Thus H-incidental under the direct-callback-counter
  discriminator; no named loss response or VERIFIED promotion. Whether id10
  feeds another mission script is untested. Dynamic response is single-source.
  First attempt crashed in the s5857 host health diagnostic before TELE-on:
  unsigned C promotion made a valid guest address read4GiB too high.
  Persistent address calculation corrected to match MIPS32 SLL/ADDU;
  same-input old expression SIGSEGV, fixed expression passes. Corrected
  flight passes the fault point. No guest guard, lib edit or default change.
  Details: docs/G1-OBJECTIVE-RESPONSE.md; scratch/agent/m6/g1_lvl1s6659_response_v2/.
  Next: one descriptor-targeted lv1 loss-counter response below its gate.

- **G1(d) level1 targeted hits: nonlethal dose, no named response (s6660).**
  One build/flight, VI5234..10634, 175.61s, 0 crashes; forces0/46/0.
  Twenty-three exact projectile/sequence/node/NPC/descriptor SEND joins:
  14 counter40,9 counter13. Mark-all id10 eligibility fires in every arm;
  six changing id10 readbacks control value detection. ids13/40/41 and
  Boolean6 remain0. Health actors stay positive:999→859 and400→322.
  Original ELF independently proves transport800DF840 bgtz skips the
  descriptor effect call800DF8C8 while remaining health is positive.
  Thus this flight does not test the destruction threshold. Per-hit health
  parent attribution remains single-source: the legacy damage join logs
  force_seq0 for actor subobjects. Eight unique named live/candidate
  identities per arm; c1f0 shows the old lever excluded relevant targets.
  Census is sampled;4096 candidate rows/arm cap means unseen later targets
  are unknown. No VERIFIED promotion or retail-equivalence claim.
  Next: a single controlled lethal hit on one named loss victim, then stop
  at actual counter readback below failure/completion. Evidence/table:
  docs/G1-OBJECTIVE-RESPONSE.md; scratch/agent/s6660_targeted/chains.tsv.

- **G1(d) level1 named loss response observed (s6661).** One opt-in build
  and flight, 128.32s wall, VI5265..7748, six forces, 0 crashes. Ordinary
  exact accepted hit seq4 reduces health390→386; same node8021B628,
  NPC8035B35C, descriptor80319AF4, actor8035D3A0. Subsequent exact seq6
  requests387 instead of raw10 once: actual damage returns−1, death-effect
  call800DF8C8 runs, actual writer8006594C changes id13 0→1 at VI7744,
  callback reads1 at VI7748. All further forcing stops at the dose;
  named readback ends the run, below c13>=5 failure. Boolean6 stays0.
  Same-run id10 changes five times in natural arm; mark-all controls fire
  in arms0/1. Off/on observed; arm2 intentionally not reached. Original
  ELF independently proves actorNPC+38, subtraction and death/effect gate
  (re-disassembly/hash agrees with s6660). H-dose selected for this victim;
  no routing mismatch or bypassed death effect observed. Dynamic causality
  remains single-source, not retail equivalence, success or full VERIFIED.
  No direct health/counter stores, lib edit or default change. Evidence:
  scratch/agent/m6/g1_lvl1s6661_dose/ and scratch/agent/s6661_dose/chain.json.
  Level1 named response unit closes; next is level2 objective response.

- **G1(d) level2 adapter exercised; target boundary remains open (s6662).**
  Original ELF: counter40 is loss (friendlies=1−c40); positive c40 sets
  Boolean109 and failure; success requires Booleans31/32/33/99. One fresh
  ordinary-only off/on/off flight, VI5080..10483,169.97s,0 crashes.
  Zero forces: no sampled descriptor passes the counter40 predicate.
  Mark-all eligible controls5/13/10; eight natural counter changes and
  seven Boolean changes control readback sensitivity. No damage survival
  or hit-driven objective response tested. Census is untyped (some fields
  out of objective range), sampled every300 VI; candidate4096/arm budgets
  all saturate. Thus target availability remains unknown, not a controlled
  objective null or proof of a broken route. Dynamic evidence single-source;
  independent ELF establishes semantics only. Lethal env is hard-disabled
  for level2; success setters excluded, one ordinary force/victim maximum.
  Build, replay, level1/level2 helper controls and manifest hashes pass.
  Evidence: scratch/agent/m6/g1_lvl2s6662_lvl2_final/ and
  scratch/agent/s6662_lvl2/population.json. Earlier incomplete arm0 capture
  has different hashes and is not pooled. No library/default change or
  new queued-soak verdict. Next: original-backed typed ownership audit.

- **G1(d) level2 population ownership corrected (s6663).** Original
  slot-free8003E88C..E8C8 leaves word0 intact: free slots carry legitimate
  stale pointers. The adapter now excludes the original BB4 free list,
  validates BB8 context ownership, records handler/primary-slot/generation
  and observed birth/retirement, and removes candidate4096 caps. One
  unlocked flight171.84s, VI4939..10339,0 crashes/forces. All20 census
  lists valid; active slots33..516, stale free pointers0..235;23 handlers,
  22 descriptor kinds unresolved. Only original-backed CABD4/DE80C paths
  can select level2 forcing; unknown kinds remain explicit. Mark-all
  controls15/17/11 and local selector40/success31 fixtures fire all arms;
  six natural counter changes. No absence, hit-response or VERIFIED claim.
  Original instructions plus live free-list membership select H-stale-free
  for inflated counts; actual target ownership remains open. Full report
  G1-OBJECTIVE-RESPONSE.md; artifacts scratch/agent/s6663_lvl2_owner/ and
  scratch/agent/m6/g1_lvl2s6663_owner/. All6 manifest hashes match; helper
  controls/build/replay pass. No library/default change or new soak verdict.

- **G1(d) level2 rescue activation and ordinary hit controlled (s6666).**
  One retail-settings flight, VI5020..17021,281.27s wall,0 crash lines.
  Reset800FA618 writes timer1=0; tick800FA924 and35 actual getter returns
  prove changing values. At the old dv5401 cutoff timer1 is55.5496902,
  below100. At dv9839 it reaches100.033333; writer800C7564 sets21/59=1.
  Four VIs later rescue01 is live at canonical slot254, handlerD3894,
  desc8031D2A0=DAT8031BD90+1510. Seq1 force14873 -> exact SEND14881 ->
  ordinary damage10, health2000->1990, return1990. One forced segment;
  off/on/off VI5020/14864/16665; no lethal dose. Counter40 stays0 as the
  shuttle survives; objective(d) remains open, no VERIFIED claim. Retail
  DAT/ELF independently corroborate definition, timer/gate and damage
  contracts; timing generalization is single-flight. Grid rescue spawn
  caller was not dynamically observed; do not infer it from the live join.
  Full table/limits: docs/G1-OBJECTIVE-RESPONSE.md s6666. Evidence:
  scratch/agent/s6666_lvl2_activation/summary.json. No new soak verdicts.

- **G1(d) level2 named loss response observed (s6668).** Original ELF/DAT
  audit precedes an opt-in one-shot dose. Same node802191D4/NPC8037680C/
  desc8031D2A0/actor80372398: seq1 ordinary2000→1990, seq2 requested1991
  returns−1, death effect then writer8006594C counter40 0→1 atVI14690.
  Callback memory and original getter return1 atVI14694, failure flags
  109/101 still0; host SIGSTOP then SIGKILL before failure branch. Epoch
  VI4941..14694, forces0/2/0, 0 crash lines,8 actual counter changes,
  getter0→1 and mark-all17/8 controls. Off2 intentionally not reached.
  First rescue01-only attempt instead spawned rescue02 and forced nothing;
  inconclusive, retained separately. Corrected opt-in admits only original
  rescue01/02/03 definitions and requires same-owned ordinary control.
  All6 launch hashes, analyzer fixtures, original assertions, replay and
  build pass. Dynamic causality single-flight; no retail equivalence/full
  VERIFIED. Wrapper's3 stalls follow intentional SIGSTOP, not flight stalls;
  active-flight wall duration unavailable. No default/lib change or new soak
  verdict. Details: G1-OBJECTIVE-RESPONSE s6668; compact proof
  scratch/agent/s6668_lvl2_loss/qualification.json. Next: level3 named response.

- **G1(d) level3 original contract checked (s6669); response still open.**
  Bounded DAT-tool change selects City_1(+048C), subtype0x14, c28+1 with no
  Boolean/second counter. Original friendlies reader80103530 computes
  100-(c27+c28); complex callback loss flags are Booleans4/18/21 and success
  counter22. GVT main adds c28 AND failure Boolean4; Tech main sets18;
  Madine shuttle sets21 but has no counter. All excluded by the static choice.
  Original C7390 FFFF-slot branch subtracts health then calls the effect at
  C74E0 with NO death threshold. Registered-slot message5 handler remains
  unqualified; live eligibility is unknown. Thus do not assume a lethal dose
  or shuttle ownership layout. --check-level3 verifies62 original anchors;
  11 mutation fixtures reject; all19 inventories preserve prior fields;
  level2 checks pass. Source+DAT support static contracts only, no live
  response/retail-equivalence/VERIFIED claim. No game run/build, defaults or
  lib edits. Full limits: G1-OBJECTIVE-RESPONSE s6669. No new soak verdicts.

- **G1(d) level3 registered ordinary script damage qualified (s6670).**
  Original subtype20 setup table selects handler8006CBB0, payload+34=DAT.
  Its message5 store8006CFE8 subtracts damage, and positive-health branch
  8006D278 skips the death effect; C7390's FFFF fallback differs. Corrected
  flight178.00s, VI5291..10692,0 crashes: one original named API request10
  on City_1 (DAT80325EEC, slot429/gen1, node8021A728, payload8038770C)
  reaches exact message80165E80 and health2000→1990; API returns1990.
  Counter28 remains0; explicit original probe getter28 returns0 after hit
  atVI9493. Getter3 actually changes0→1, matching memory. H-registered for
  this ordinary request; no destruction/counter response or VERIFIED claim.
  Original DAT/ELF support contracts; dynamic causality single-flight.
  No player-shot or game-invoked friendlies-reader proof. First full flight
  forced nothing (no projectile-context control); second issued no API
  request (extra adapter eligibility filters, exact reason unmeasured). Both
  had0 crashes and are retained as failed hit controls, not damage nulls.
  Third build uses original lookup equality and lets the API select the route;
  one request only, no lethal/default/lib change. All6 launch hashes,97 ELF
  mutation checks, analyzer fixtures and replay pass. Proof: scratch/agent/
  s6670_qualification.json; details G1-OBJECTIVE-RESPONSE s6670. No new soaks.

- **G1(d) level3 named loss response observed (s6671).** One unlocked
  flight VI5384..7211,120.13s total runner wall,0 crashes. Same City_1
  slot429/gen1,node8021A728,payload8038770C,DAT80325EEC,detail0: original
  named API seq1 request10 writes2000→1990; seq2 request1991 writes1990→−1.
  Death effect8006D6F0 passes original tuple(28,1,0,0,0,1); writer8006594C
  increments28 0→1 atVI7203; callback and explicit original getter read1
  atVI7211, flags4/18/21 and successcounter22 still0. SIGSTOP then SIGKILL;
  off2 intentionally not reached. Actual getter3 0→1 controls value detection.
  Original DAT/ELF corroborate contracts; dynamic causality remains single-flight,
  no player-shot/game-invoked friendlies proof or VERIFIED promotion. Analyzer
  initially demanded unused delta2=0; original counter2=0/delta2=1 disables
  that effect. Corrected to original tuple, stricter chain fixtures pass,
  saved capture qualifies. Binary/adapter unchanged;5/6 current launch hashes
  match, analyzer correction documented. No direct stores/default/lib edits
  or new soaks. Proof scratch/agent/s6671_qualification.json; full evidence
  G1-OBJECTIVE-RESPONSE s6671. Next: original-backed level4 target contract.

- **G1(d) level4 original wingman contract checked (s6672); live response open.**
  Original reader80103CC4 computes6−(c40+c15); callback fails on c16>=3,
  c15>=3 or Boolean26, succeeds on c28>0 with word8010D060==1. Counter5
  is absent from these readers; Boolean5 is a distinct Y-wing effect.
  Retail DAT x_wing_hobbie(+6A7C), subtype0x27, nominal detail0 HP400,
  effect(40,1,0,0,0,1), selects named loss without direct Boolean effects.
  Original table/setup selects wingman handler800D93C0, message5 atD9BB0;
  payload+34=DAT,+38=actor. Damage800F2120 writes array or inline health
  atF2148/F2158; positive return skips effectD9D28. Do not reuse City hooks.
  Tool adds --check-level4/--mutation-check-level4:332 anchors and380
  mutations pass; all19 inventories unchanged, lvl2/3 regressions pass.
  DAT+ELF establish static contracts only, no live ownership/hit/response,
  player-shot/retail-equivalence or VERIFIED claim. No runtime/default/lib
  change or new soaks. Full table/limits G1-OBJECTIVE-RESPONSE s6672;
  scratch/agent/s6672_validation.json. Next: one owned ordinary Hobbie API hit.

- **G1(d) level4 ordinary health chain observed (s6673); counter control absent.**
  One corrected unlocked flight172.03s, VI4971..10371,0 crashes. Hobbie
  slot187/gen1,node8021B268,NPC8035F68C,DAT803239CC,actor80361D58 is owned
  and original lookup-equal. One API request10 atVI6777 -> exact message5
  80165E80 -> original array storeF2148 at80323A38, health370→360; damage
  and API return360. Mode0/detail0; mark-all health controls fire off/on.
  Getter40 returns0 after hit; all128 counter getters match memory, but0
  actual counter changes. Thus exact_health_chain=true, qualified_ordinary=false:
  no controlled counter null or named response/VERIFIED claim. Original
  ELF/DAT independently support contracts; dynamic causality single-flight.
  First attempt stopped73.03s/0 crashes/no API: decimal27 predicate was wrong;
  original subtype is0x27=39. Corrected and rerun. Both health branches hooked;
  all6 hashes,13-file idempotence, hook-free replay and fixtures pass.
  No lethal/direct store/default/lib change or new soaks. Proof:
  scratch/agent/s6673_qualification.json; G1-OBJECTIVE-RESPONSE s6673.
  Next: same-owned ordinary-then-lethal pair to test named counter40 effect.


- **G1(d) level4 named loss response observed (s6674).** One unlocked flight,
  113.56s runner wall,VI4966..6784,0 crashes. Same Hobbie slot187/gen1,
  node8021B268,NPC8035F68C,DAT803239CC,actor80361D58,mode0/detail0,
  health80323A38: seq1 API10 actual F2148 store380→370/returns370;
  seq2 request371 actual370→−1/returns−1. Death effectD9D28 passes original
  tuple(40,1,0,0,0,1); writer8006594C counter40 0→1 atVI6777; callback
  and original getter read1 atVI6784. c15/c16/c28 and Boolean26 stay0.
  SIGSTOP then SIGKILL; off2 intentionally not reached. Actual getter40
  0→1 supplies the counter control missing in s6673; both analyzers qualify.
  Original ELF/DAT332 anchors/380 mutations independently support contracts;
  dynamic causality single-flight, no player-shot/retail-equivalence/full
  VERIFIED claim. All6 launch hashes, build, fixtures, original lvl2/3
  regressions,13-file idempotence and3 hook-free replays pass. No direct
  stores/default/lib edits or new soak verdicts. Evidence:
  scratch/agent/s6674_qualification.json; G1-OBJECTIVE-RESPONSE s6674.
  Level4 response unit closes; next: level5 original objective/target contract.

## Superseded conclusions — do not act on these

- s6673 first adapter treated wingman subtype “27” as decimal27. Believable
  because the prior prose omitted its base; original checker uses0x27 and
  loaded mission DAT reads39. Fixed before the interpreted flight.

- s6664's missing counter40 target is not evidence of a broken spawn/hit
  route. Its5400VI window looked sufficient when VI time was treated as
  mission timer time. s6666 measures55.55 at that cutoff, then naturally
  opens the gate at9839VI and joins an ordinary hit. This establishes a
  duration boundary for the recipe, not a universal timer rate.
- s6662 pointer-like census counts are not live-object counts (s6663 original free-slot writer retains pointers; live free-list walk finds up to235 such entries). Believable because the old census checked pointer shape without free-list membership. Its zero target result was already labelled inconclusive and remains so.
- s6656/s6657 "level1 counter13 meaning unresolved" (s6659 original ELF identifies it in friendlies-saved subtraction and the >=5 Bit4 gate). Believable because historical activity logs supplied indices but no per-level semantics. Hit causality for counter13 remains unresolved; the corrected live flight changes only id10.
- s5962 "lvl6 null is valid because hb ticks fires" (s6656: heartbeat controls execution, not detection of value changes; the monitor covers only ids 1–15 and has a run-lifetime budget). Believable because TELE and hook execution both fired, but no same-run changing-value control established sensitivity to every relevant objective slot.
- s5995 "lvl7 id2 peak3 matches the objective threshold" (s6656: that threshold belongs to lv0; the lvl7 callback's inspected reads include ids 20/30/40/99, outside the monitor). Believable because all levels reuse the counter array; index meaning and thresholds are level-specific. Lvl7 end remains the lives-loss chain observed in both arms, not id2 causality.
- s5994–s5995 "lvl8 counter6 resets during the measured response" (s6656: first explicit flight epoch contains only 0>1>2>3>4; 4>0 is later). Believable because the old parser pooled run-lifetime events including re-entry. The reset remains real, but is not part of the first-epoch response.
- s6653 "level 18 has visual evidence but no numeric terrain acceptance" (s6654: the bounded bright low-chroma snow arm accepts both flight views while every control holds). Believable because their rel 0.046/0.068 is below the original 0.08 floor; that band remains unchanged.
- s6651 "level 17 does not pass the frozen rule, and the grey trench box is not a sky arm" (s6652: neutral8 ≥ 0.80 inside luma [38, 55] with |channel means| ≤ 8 accepts n=2300, 1/10; canon_bad 0; mission 11/13; both title skies stay false; m3150 stays a sky miss at neutral8 0.613). Believable because dark ≥ 0.60, the blue arm, the orange arm and the tan-cloud arm all miss luma 42.5 with R−G 1.4, and the top 4% of that frame is the same grey, so lowering dark does not accept the chase.
- s6649 method "the flight set is the phase-7 dumps" (s6650: level 16's flight dumps stay phase 5). Believable because levels 11-15 insert a 640-wide crawl that bumps `rs64_phase_ord` through 6 into 7. The ordinal bumps only on a VI-width change, so a 512-wide flight after a 512-wide hangar does not.
- s6643 "level 10 is a flight and the frozen rule rejects the sky 0/12" (s6644: tan-cloud arm accepts 11/12; n=2900 stays a craft miss at edge 0.013; title sky stays false because G−B is ~5 while the clouds are ≥22; canon_bad 0; mission 11/13). Believable because dark≥0.60, the blue arm (R−G≤15) and the orange arm (R−G≥40) all miss a luma 73..104 sky with R−G 23..28.
- s6640 "level 8 is a flight and no craft clause accepts it without breaking canon, so the rule stays 0/7" (s6641: lower-centre metal against a coloured neighbour, edge≥0.05, plus luma≥80 orange sky, accepts 6/7; n=2600 stays a side-view near-miss at edge 0.041; canon_bad 0; mission 11/13; title and craft-select still fail). Believable because the engine, bright-metal, reticle and median≥120 dark-hull arms all missed, and a raw grey fraction in the same box also matched the title.
- s6636 "the orange flight sky is the luma≥140 sunset arm" (s6640: level 8's orange sky is luma 84.4..97.0, R−G 86.8..94.3, and that arm misses 7/7; s6641 lowered the floor to 80). Believable because the only orange flight measured before that capture was the level-4 sunset, which cleared 140. Level 4's own acceptance is unchanged.
- s6635 "level 4 is a picture only; the class rule rejects it 0/7, and no sunset arm was shown to keep canon_bad at 0" (s6636: luma≥140 with R≥G+40 and R≥B+20, plus a dark hull against a bright chase band, accepts 6/7; n=2300 stays a terrain near-miss at rel 0.065; canon_bad 0; same-run title and hangar still fail). Believable because the s6634 sky clause had no orange arm and the center-box pink cap treated that sunset as an oversized engine.
- s6634 "a flight sky is either dark (dark≥0.60) or bright with R≤G+15" (s6635: the level-4 sunset is bright, R−G about 48..67, and sky fails 7/7). Believable because the only flight skies measured before this capture were level 1's blue sky and level 3's night. The level-3 acceptance itself still holds.
- s6633 "the level-3 night flight has no numeric acceptance that still rejects the floor and the title" (s6634: relative edge energy in [0.08, 0.33], plus a metal hull or green reticle, accepts 11/13 night dumps; floor rel 0.709 and title rel 0.410 fail). Believable because the only rule that had been run, luma stddev and engine colour, scored 0/13.
- s6632 class rule "those four numeric cuts accept a frame that shows sky, terrain, craft and HUD" (s6633: the level-3 night flight shows all four and scores 0/13). Believable because level 1 and level 2 are bright scenes and both passed the same cuts.
- s6632 "only a dump whose own origin field is 0x690400 is the mission picture" (same run: that origin is in the VI log, and every dump in the window is the other buffer 0x620400, which is the flight picture). Believable because the route key is 0x690400 and EVERY=50 phase-locked onto one of the two buffers.
- s6631 first cut "any block with next > e4 is the tail, so walking until then caps the arena" (same session, did=3 at a header exactly equal to e4). Believable because s6630 described the free block as covering [e4, top) and the header as e4-0x10. The punch's reserved size ends on e4, so the free header is e4 and the old walker returned before cutting.
- s6630's first classifier label "H-stale-target, because inflateEnd frees the zlib window before the depth upload" (same session, H-live-overlap). Believable because that free is real and precedes the read. It does not move `801163E4`, which still names `0x80B56000` at malloc, free, SETZIMG and the upload.
- s6629 "why the zlib window overlaps the depth image is open" (s6630: the image was still reserved when `rs_malloc` returned inside it; s6631 then stopped that heap at the depth pointer). Believable because s6629 named only the store. At s6630 heap `8010FEFC` still ran through to RAM top; heap `8010FF18` already stopped at the depth pointer.
- s6628 "writer between A/B unknown" is resolved at the watched word by s6629 exact pre/post stores and caller context: rs_zcalloc clears a zlib window there. The earlier witness lacked store hooks. s6630 resolves the ownership class; it does not make the whole stripe one 32 KB zero.
- s6628 closes H-swap/H-alias for the measured upload (single-source): believable because the earlier native witness preceded byteswapping and did not record the live mapping. Post-swap and exit preserve `0x9EC4`, and both sites use the identical host address; the zero appears between them.
- s6627 closes "the 1024x447 `copyToRAM` at `0x00B20000` writes the `0x0000` stripe" (it covers `0x00BB0020`). Believable because that span contains every stripe address and the same write's own image y=180 is rawBe 0. Refuted: the absolute sample is rawBe `0x9F4C` on all 935 covering writebacks, the call count does not move, and the upload still reads `0x0000`. The image-y zero is phys `0x00B7A020`.
- s6626 closes "fbChangesDrawDepth, its boolean mask, or its viewport manufactures the 21:9 depth stripe from a clear or smooth guest field" (H-upload). Believable because the GPU image goes from a read-back clear of 1.0 to the stripe inside copyFromChanges, and a discard mask cannot paint 0 by itself. Refuted: the guest words already are the stripe and match the GPU on 142/142 samples (mae 0), shader endian, site state.cpp:2604.
- s6625 "after the zero head, x=16 is a smooth 0.964..0.961 ramp and x=1007 stays 1.0". Believable because x=16 does contain 0.96408 and x=1007 has more exact-1 samples (31 vs 13). Both columns actually interleave ~0.96 and 1.0. The stable part is the exact-0 head.
- s6625 closes "the 21:9 zeros are unwritten depth tiles (create-clear never applied, so a readback of 0)". Believable because Metal does not clear a D32 texture at creation, and a different 1024x480 target's first sample in the same run was exact 0. Refuted on the floor texture: clearDepthTarget read back 1.0 on both columns, and the following copyFromChanges replaced those pixels.
- s6623 "shader-to-attachment MAE 37 at 21:9 means the first wrong stage is an attachment write after a sane shader" (s6624: the same shader color is stored at 16:9, where depth is 1.0 and LESS passes, and rejected at 21:9, where a nearer striped depth already occupies the columns). Believable because the UAV record is written before the depth test and matched the 16:9 attachment exactly.
- s6614 lead "dtdx*x at the outer third diverges on 21:9" (s6615: dtdx shrinks by about 796/1024 and the texel matches to about 0.05). Believable because the sample x grows with the framebuffer and s6613 only cancelled that product at x=0.
- s6612 "21:9 S at the left edge walks off the 64-wide mask while 16:9 stays inside" (s6613: 0/16 pairs do that; S at x=0 matches). Believable because the x span and dsdx scale with width. x_major moves the other way and the product cancels.
- s6610 ring-only "second=fbw-512 fixes the 16:9 radar" (the ring reached the retail inset, but the wedge stayed at 769..792 with 0 pixels inside the ring). Believable because s6609's red-ring edge equalled retail+second. The disc is a separate pre-shift `ROGUESQ_SHIFT_REGION` writer; shift must be A, not RA.
- s6602 "wide-only bottom garbage selects a stale/stride renderer family"
  (s6607-s6608: diagnostic height exceeded the VI source; corrected bounded
  dumps and OS window captures lack the tail). Believable because raw guest
  PPMs looked like window captures. This does not close native geometry issues.
- s6606 "the wide hangar band is already in source pixels" (s6607: source
  fingerprint checks columns 269..335 in 336 rows; visible bottom garbage is
  in a raw 448-row dump beyond that copy). Believable because the raw PPM
  looked like window output and nonzero/transition counts appeared to confirm
  it. The PPM header explicitly says rdram-readback-not-window; its fixed
  height is not the actual VI source height. Actual window fidelity remains
  open; the source-versus-presentation split was not closed.
- (s6579) "dd4 bundle-only / dd4 holds without ROGUESQ_DD_UNSAFE ran at dd4" (superseded: they ran dd3). Believable because the knob was set to 4 and nothing warned except a "multiplier 3" log line, which looked like a display quirk; the s6446 cap in apply_s6036_dd.py:7 clamps silently otherwise.
- s6576 "lvl1 ddclamp area saturates at level extent by dd6, not an engine table" (s6577: at dd6 the cell cap trims the window below the extent in ~55% of samples on lvl1/5/10; the earlier 4096 maximum was a single sample).
- s6574 "dd12 holds clean": believable because the env var was 12 and the run was clean; overturned s6575 - the multiplier is clamped to 8, so it was dd8. Raising the clamp is not the next step; the 64-wide terrain table saturates first (single-source, one run's log).
- (s6559, superseded s6560) "The ~600 chunk/frame loss comes from a head write the store hook cannot see (MEM_W grow hooks, fixup force-zero)." Believable because the hook showed no far/mid/null stores yet the list shrank. Refuted: tracked==actual head 199/199 with a firing positive control; the off-chain stores are in the hooked path, mislabelled 'splice'.

One line each: claim (superseded by; why it was believable).

- s6555/s6554 "chunks consumed by a runaway consumer / free path leaks" (s6556: pops==pushes per frame; chunks vanish without a pop).
- s6554 "runaway consumer in traverseSceneGraphRecursive" (s6555: sibling loop visits 8-17 nodes/frame, 0 revisits at the fault frames; the fault stack merely passes through it).

- s6553 "dd>1 NULL node = DL-chunk supply shortfall" (s6554: a 12x larger arena is consumed in ~24 frames; chunk-empty is the symptom of a runaway scene-graph walk).
- s6550 "split POOLX=3 vs 4 for a threshold" (s6551: px2-4 all fault; the cap scaled with POOLX).
- s6545 "cap0 vs inf undecided" / s6544 "pinned pose" sheet (s6546; s6544 pinned only the stair-metric window, not the camera).
- s6539 cap ordering 0<40<120<inf for terrain (s6541 retracted as run-to-run scatter; 4-10 frames/arm looked monotonic).
- s6542 cap0 dearer than cap120 (s6543: post-inf hysteresis; rotation order confounded it).
- s6540 "default path differs from explicit cap120" (s6541 H-noise; single runs differed).
- s6537 "a cell cap keeps most of the gain cheaply" (s6543: gain is all-or-nothing; cap arms were cross-run).
- s6525 dd4-rejected cells have sentinel recs -2 (s6526 raw dump: normal recs; the joined log read unpopulated bytes).
- s6520 span bytes 0x80 "never written" (s6521: clamp/clear values; 0x80 resembled an init fill).
- s6516 dd4 EMPTY reads another table (s6517: sampling-phase confound; dump rows covered different key ranges).
- s6509 DC0 writes outside a 24-byte span table (s6510/s6511: it is a 64x64 grid; only 24 bytes were dumped).
- s6502 thread-local / s6500-s6505 cumulative writer joins (s6505/s6506: cross-function shared counter; guest IDs matched).
- s6495 all-127 table = rasterizer produced no rows (s6514; snapshot is taken after the filter's own 0x7F stamp).
- s6491 cell list never empty (s6492: read stale r16; head is v0).
- s6488/s6489 low-vs-high-ground tri split (suspect: tool hardcodes non-flight fbs).
- s6472 fixed 64x64 grid tables limit dd3 (s6473 offline: window is post-clamp, kept<cap).
- s6470/s6471 "game submits shorter DL at dd3" break point (explained by the span-filter chain; pinned vs unpinned recipes disagreed).
- s6466 dd8 att1 "route failure" (real SIGBUS; soak summary alone mislabelled it).
- s6446: s6420 "dd3+fix lvl1/5/10 clean" holds were dd2 (run.log said `capped to 2`).
- s6414 durable constraint "dd>2 exhausts the DL chunk supply" ([dlpool] identical across arms; H-chunk refuted).
- s6407 ~5% HUD-absent at dd3/dd4 (s6409: scorer counted menu frames).
- s6399 aspect side-edge lean (s6401 withdrawn: outer-column scalars are noise).
- s6393/s6391 fixed wide-flight origin gate (origin is allocator-dependent).
- s6380 zero-FD57 interpretation (s6380long route audit: retry arm took a different route).
- s6292 FPS60 owns the turning shake (s6455: VI wall-stamp artifact).
- s6426 menu garble = wide-FB stride defect (s6427: 640-wide cam scaling).
- s6434 hangar only ~340/448 rows (s6438: 436-448 lit; dumps misread).

## Run recipes and hard config

- Run from `build/` with the ROM beside it; SIGKILL to stop; one game run at a time.
- Current pinned dd4 lvl1 run: `zsh scratch/agent/s6549_run.sh <dd> <poolx>`.
- dd4 was enabled without `ROGUESQ_DD_UNSAFE` in s6582; higher exploratory
  settings use DD_UNSAFE (clamp 8). Confirm run.log echoes `multiplier N`.
- lvl10/15 need `ROGUESQ_FORCE_PLANET_UNLOCK=0xFF`. Wide soaks need
  `MISSION_WIDTH=796|1024` + `WIDE_ROUTE=1`; ASPECT implies `OSMEM_MB=12`.
- Pose control: `ROGUESQ_POSE_LOCK=1` + `ROGUESQ_POSE_PIN_POSITION=1`; dump
  ordinal is not a phase key, join dumps to `[vi]`/origin
  (`tools/g1c_fbdump_join.py`).
- Soak verdicts: `scratch/agent/SOAK-RESULTS.md`; read `alive_at_end` /
  `crashlines`, never rc. A queued repeat soak is not a work unit.
- Per-frame cost meter: `[g1b]` lines in run.log (sd_wall, tasks/s).
- Full dd knob/instrument table: PROJECT-OVERVIEW "G1c draw-distance knob and
  recipe reference"; owner guide `docs/DRAW-DISTANCE.md`.

## G1 mission coverage

Playable levels are 0..18 (`NUM_LEVELS=0x13`); 19/20 are sentinels. Route/hold
coverage and framebuffer presence are distinct from objective response.
Level 1 has a retail flight match. Level 0/1/2/3/4 named counter responses are
observed; remaining objective response coverage is partial. No level is promoted
here to fully VERIFIED. See [framebuffer coverage](G1-FRAMEBUFFER-COVERAGE.md)
and [objective contracts, evidence and limits](G1-OBJECTIVE-RESPONSE.md).
Mission wins, aim/steer and mission-to-mission progression remain owner playtest.

## Durable constraints

- Retail defaults remain unchanged. Opt-ins include draw distance, aspect,
  FPS60, spike culling, and audio control. Do not make an opt-in default from
  a single-source result.
- `ROGUESQ_DRAW_DISTANCE`: dd2 qualified lvl1/5/10; dd3/dd4/dd6 300 s holds
  clean lvl1/5/10 under DD_UNSAFE; dd8 lvl1/5 clean. Crash-free holds do not
  mean "renders correctly" (s6468: dd>=4 ground missing before the bypass).
  No mitigation is acceptable without naming the writer and establishing value
  legitimacy; dd>1 fixes live in `tools/apply_s6*.py` and fixup scripts.
- Wide rendering uses runtime RAM-top handling and a larger reported memory
  arm; default remains 4:3/retail. Native hangar artifacts remain parked.
- The title plume is parked after clean boots. Reopen only on new evidence.
- Read `docs/F5-UCODE-REFERENCE.md` before interpreting Factor 5 streams.
  Ground truth must precede new instrumentation; every null needs a positive
  control and two independent lines of evidence before changing this file.
- Generated diagnostics must survive regeneration through fixup tooling.
  Never reset, clean, checkout, or update submodules. If editing `lib/`, run
  `./submodule-patches/export.sh` and commit the refreshed patches.

## s6675 update — level5 original contract qualified

Original ELF reader80104118 computes7−(c40+c2); callback8010415C sets Bit4
at c2>=4 and Bit8 at c4>=9 (with latches). Retail x_wing_wedge(+1AFC),
subtype0x27, detail0HP200, effect(40,1,0,0,0,1), selects a named loss response
through the original wingman route800D93C0/message5D9BB0. Health writers
F2148/F2158 and death-gated effectD9D28 are asserted. Historical id2 writer
remains unknown; Reb_combat1..4 raw counter2 tuples also carry Booleans21..24,
and their subtype0x2E route is unqualified. Tool adds level5 checks:334
ELF assertions/390 rejected mutations, direct DAT struct cross-check, all19
inventories and full level4 contract unchanged; lvl2/3/4/analyzer checks pass.
ELF+DAT establish static contracts only; no live availability/response or
VERIFIED promotion. No runtime/default/lib change or new soak verdict.
Full contracts: G1-OBJECTIVE-RESPONSE s6675; scratch/agent/s6675_validation.json.

## s6676 update — level5 ordinary health route observed

One corrected unlocked flight167.02s, VI4682..10086,0 crashes. Wedge
DAT8031BCCC,slot87/gen1,node8021B6DC,NPC8035421C,actor80354898,
handlerD93C0,detail0/mode0. API10 atVI6486 -> exact message80165E80 ->
actual writerF2148 health190→180 -> damage/API returns180; original getter40
returns0=memory0 atVI6489. Owned mark-all controls fire arms0/1. No objective
getter changes: exact named health chain passes, full ordinary qualification
remains false for absent counter sensitivity control. Silent counter40 is not
a controlled null. Original ELF/DAT independently support contracts only;
dynamic chain single-flight. No named response/VERIFIED promotion. Adapter
persists through fixup; level5 lethal/generic TELE disabled. First pre-flight
attempt stopped to undo an accidental level3-only edit; corrected build/run,
6/6 hashes, fixtures,13-file idempotence and new hook replay pass. Level3 tick
unchanged. No lib/default changes or new soak verdicts. Proof/table:
G1-OBJECTIVE-RESPONSE s6676; scratch/agent/s6676_qualification.json.

## Next steps (single monotonic backlog)
1. **G1(d) level5 same-owned Wedge loss-counter response (next unit).**
   Ordinary health delivery is observed (s6676), but no getter changed.
   Add one opt-in currentHP+1 request after same-owned ordinary API10
   entry/store/return qualify; revalidate slot/generation/DAT/NPC/actor,
   detail/mode/storage/name/current health and original effect tuple.
   Require actual death effect, counter40 writer/readback/original getter;
   stop immediately with c2/c4 and latches unchanged, below their gates.
   No direct stores, wins/progression or repeat ordinary soak.
2. **Continue G1(d) named response coverage for remaining levels.** Reconcile
   the existing evidence table before choosing the next level; scope counters
   to that level's original callback and require actual changing-value controls.
   Saved level7 id2 activity does not establish that level's objective semantics.
3. **Owner visual judgement and parked boundaries.** G3c sheets and optional
   spike cull await owner judgement; keep retail defaults. Native hangar
   geometry, rare dd4/dd8 gfx SIGBUS and dd8 hangar garbage remain parked,
   single-source where unresolved. Reopen on a new owner report or relevant
   side-effect failure, not repeat crash-hunt holds. Historical proposed probes
   are archived in PROJECT-OVERVIEW, not an alternate live backlog.
4. **Then G3 render fidelity.** Follow the standing ladder for hangar artifacts
   and flight comparison against retail. G2/G5 are closed; G4 and aim/steer stay
   parked. No backlog-exhausted block.

## Evidence index

- Active objective source contracts, exact commands and result limits:
  [G1-OBJECTIVE-RESPONSE](G1-OBJECTIVE-RESPONSE.md), especially s6661, s6666 and s6668.
- Per-level images: [G1-FRAMEBUFFER-COVERAGE](G1-FRAMEBUFFER-COVERAGE.md).
- [Maintenance s6667 retained evidence](PROJECT-OVERVIEW.md#maintenance-s6667-retained-evidence):
  verbatim per-level paragraphs, duplicate coverage, historical backlog and updates.
- `PORTING-STATE.md` sessions 6656–6676 contain recent chronology; search bounded
  windows only. Earlier durable context remains in PROJECT-OVERVIEW.
- Queued-soak verdicts: `scratch/agent/SOAK-RESULTS.md`; latest remains
  20261028-075640 (already consumed). No new verdicts in s6676.
- s6596/s6597 and s6599 were checkpoint close-outs, not reruns. The saved
  s6595/s6598 HUD artifacts retain their original evidence limits.
