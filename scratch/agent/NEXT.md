# Join level-2 rescue timer, gate, shuttle spawn and ordinary damage
HYPOTHESIS-ID: g1-coverage-cd

s6665 identified the original count40 producer. Do not repeat a handler-map
census. tools/g1_dat_inventory.py --check-level2 decodes all401 structural
DAT definitions and positively finds known id71 SHIP_01..03. Three subtype24
rescue shuttles at DAT offsets1510/1628/1740 have HP2000, death40/+1 and
activation Booleans21/22/23. Complete evidence in
G1-OBJECTIVE-RESPONSE.md s6665 and scratch/agent/s6665_lvl2_producer/.
Unknown DAT layouts remain raw; no claim of an all-subtype semantic decoder.

Original ELF paths:
- Grid range80047554 -> condition80047570 -> setup80047640.
- 8003C140[0x24-12]=80065854 reads descriptor+60 Boolean and+64/+68 counter.
- 8003BDB8[0x24-12]=800654C8 -> D3894 shuttle handler; alternative
  structure spawn8003BED8[0x24-12]=80065708 chooses the same handler.
- D3920 descriptor -> payload+34; wrapped spawn D3948 uses incoming+0C.
- Message5 table800A74C8[4]=D49FC -> D4B0C dealDamageToNpc -> death
  D4BA8 datItemSetObjectiveBooleanCount -> actual store8006594C.
- Callback80102174..226C: Boolean59=0 AND objective timer1>=100.0;
  then bool1=1/7=0 ->21=1, bool2=1/8=0 ->22=1, bool3=1/9=0 ->23=1.
  Chosen branch also sets59. Original getObjectiveTimer800C76E0 reads
  timer1 at8010C9FC. Constant800A95F4=100.0, GNU confirms c.le.s.

Saved s6664 first flight VI4955..10356 has bool21/22/23/59 always0 in
callback samples; bool1 rises1 at5881;2/3/7/8/9 stay0. Five actual Boolean
changes control readback sensitivity. NO timer captured. Do not call the
90VI-second hold the explanation: timer initialization/rate are unmeasured.
No shuttle hit, objective response, VERIFIED, runtime/default change.

ONE next unit: one instrument/build/flight carrying the complete
initialization -> timer threshold -> activation predicate -> spawn ->
owned descriptor -> ordinary projectile SEND/health join. Use original
sources first; no field-per-iteration work. No direct timer/Boolean/counter/
health writes, no lethal level2 dose, arbitrary victim, win or progression.

Competing hypotheses:
- H-duration: actual timer1 never reaches100 within the old5400VI window.
  Measure its initial value and growth against VI at every phase-local
  checkpoint, actual getObjectiveTimer return, and threshold crossing.
- H-state: timer crosses100 but another original predicate differs (59,
  ship1/2/3 or7/8/9); capture all at the exact callback decision, including
  setter arguments and actual written byte. Do not infer from timestamps.
- H-spawn: gate really opens but grid/range/ownership prevents a live shuttle;
  join DAT base+offset, range/condition return, setup result and primary slot/
  generation. This selects an activation/spawn boundary, not a broken hit.
- H-hit: live owned shuttle exists but candidate/SEND/health path excludes it;
  add audited D3894 descriptor and message5 health/effect hooks in this same
  build. One ordinary hit per named shuttle, no lethal override. Exact
  force->accepted SEND->health reduction is the discriminator.

Positive controls in SAME flight: dump all three resolved named definitions
including the known id71 live SHIP descriptor match; mark-all candidates
must visibly include a known live object; natural Boolean/counter changes
control monitors; local shuttle selector fixtures test id40 and success
exclusions. A timer null without observed return values is worthless.

Before building, edit the existing persistent adapter/runner to add the
whole table and an opt-in timer-aware level2 duration (old runner hardcodes
HOLD_S=150, watchdog360; adapter stops5401VI). Use up to12000VI after flight,
phase-scoped budgets and a watchdog/hold that covers it (<=600s). Start
force off, switch on only after named live shuttle activation, then off
again; no cross-run scene comparison. Stop before failure/end gates.
Retain level0/1 and disabled behavior; no lib edit is required.

Commands (bounded windows; never read full ledger or logs):
    mkdir -p scratch/agent/s6666_lvl2_activation
    python3 tools/g1_dat_inventory.py --check-level2 --log scratch/agent/m6/g1_lvl2s6664_kinds/run.log --output scratch/agent/s6666_lvl2_activation/original.json
    rg -n '5400|1800|HOLD_S|360|800D3894|rs6663_descriptor' tools/apply_s6657_objective_response.py tools/g1_objective_response_run.py
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x800C76B0 0x800C7718
    sed -n '163,222p' scratch/agent/s6665_lvl2_producer/level2_objectives.txt
After implementing every join and fixtures in one build:
    python3 tools/apply_s6657_objective_response.py
    cmake --build build --target RogueSquadron64Recomp -j5
    /usr/sbin/ioreg -n Root -d1 | rg 'CGSSessionScreenIsLocked'
    python3 tools/g1_objective_response_run.py s6666_activation --level 2
Use the new opt-in duration argument/env you implement. Fresh paths;
SIGKILL watchdog; game cwd build/ with ROM. If no gate within12000VI,
report measured timer and exact predicates; never extend blindly.
