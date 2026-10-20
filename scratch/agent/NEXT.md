Single next work unit (s5616): fold s5615_nopoke_a/b from SOAK-RESULTS.md (data in scratch/agent/m6/s5615_nopoke_{a,b}/run.log). Compare `grep 'seq gate' run.log | sed -E 's/.*gate=([0-9]+) subphase=([0-9]+).*b14=([0-9]+).*/g\1 s\2 b\3/' | uniq -c` with the p100/p300 sequence g5(11-14) g0(~146) g4(11) g4s1b2 g6s1b2(9) g0b2.
Hypotheses: H2 gate-5 phase window swallows the poked event; H4 the g4/b14=2 tail is a natural/godmode-independent end (poke irrelevant); H5 poke drives it but only after a delay.
Outcomes: NOPOKE same sequence -> H4: find what ends the mission naturally (b14=2 writer caller, 800FB190 a0 via lldb break) ; NOPOKE all g0 -> poke causes gate 4: poke get(10) again whenever gate returns to 0 and phase==0.
HYPOTHESIS-ID: m6-mission-endurance
