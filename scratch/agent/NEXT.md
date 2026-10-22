# NEXT: G1 - s5859: who receives the msg-type-5 hit SENDs?
s5858: npcGroundTroopUpdate sees types 3/4/11 only, never 5 (n=233k, controls populated). 505 SENDs of type 5 exist.
Hypotheses: H16 slotDispatcherIter/queue drops msg 5 before delivery (slot lookup fails or victim id not live); H18 the victims' update fn is another one (not 0x800E7860) which handles/ignores 5; H19 SEND carries a different type value than 5 in a1 (e.g. type is in another register/field) so the ty5 filter is wrong - check type 11 (174k) vs SEND log.
Discriminating measurement (one build): at the SEND site log receiver id, msg type, and the receiver slot's update-fn pointer; in slotDispatcherIter entry histogram (msg type, target fn addr) for type 5; positive control: type 3/4/11 deliveries show up in the same table. Outcomes: target fn != 0x800E7860 -> H18; no dispatch row for the SEND -> H16; SEND type != 5 at dispatch -> H19.
Also: capture lldb backtrace if the Bus error at far 0x37fffd040 recurs (queue the g1_fireall recipe as a soak).
Run: env ROGUESQ_LOG_HITS=1 zsh scratch/agent/g1_fireall.sh s5859 300
HYPOTHESIS-ID: g1-mission-progression
