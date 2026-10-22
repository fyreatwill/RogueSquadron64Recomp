# NEXT: G1 - s5860: do bolts ever have a class-1 troop in range?
s5859: msg-5 SENDs are delivered (468/505) to updateDestructionDebrisNpc (455), not to troops; no dispatch defect. Open: are class-1 troops ever within bolt range/aim, and is the hit-test target set excluding them?
Hypotheses: H20 troops are simply never near the line of fire in this scripted position (scenario/aim, not a bug); H21 hit-test target set/predicate excludes class-1 troops (defect); H22 troops are hit via a different path (the ~14 dealDamageToNpc calls) at a low natural rate.
Discriminating measurement (one build, one run): at each closest-hit SEND log victim id, victim update fn, class (+0x70), and min distance player->any class-1 troop (ROGUESQ_LOG_PLPOS positions); also min troop distance sampled every 60 frames. Positive control: distance column populated and varying; victim fn column shows 8006cbb0 as in s5859.
Outcomes: min distance always >> bolt range -> H20; <range yet never victim -> H21; dd calls track close-range events -> H22.
Run: env ROGUESQ_LOG_HITS=1 zsh scratch/agent/g1_fireall.sh s5860 300
HYPOTHESIS-ID: g1-mission-progression
