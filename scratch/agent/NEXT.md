# NEXT: G1 - s5857: what does a SEND to a hit victim do? (hits are real: s5856)
s5856: hit fn returns nonzero for ~12 ids; closest-hit then one SEND per bolt (s3 hit=304, s4 SEND=493). H10/H11 dropped.
Hypotheses: H13 the victim handler receives the damage msg but ignores it (class/state gate) -> hp unchanged; H14 hp drops but kill/explosion path never fires (death routine stub/guard); H15 enemies die fine and the mission win condition is what's missing.
Discriminating measurement (one build, one run): at SEND (0x8005D35C) log victim id, class (desc+0x70), victim hp field before; re-read hp ~2 frames later and log a dead/flag-change; count kills per class. Positive control: ROGUESQ_MISSION_WIN-independent: id 52 SEND must appear. Outcomes: hp flat -> H13; hp drops, no death -> H14; deaths occur -> H15 (check win counter).
Also: take lldb backtrace of the SIGBUS (si_addr=0x37fffd040) if it recurs.
Run: env ROGUESQ_LOG_HITS=1 zsh scratch/agent/g1_fireall.sh s5857 300
HYPOTHESIS-ID: g1-mission-progression
