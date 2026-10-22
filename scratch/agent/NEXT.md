# NEXT (s5882): what does get(1) (0x80138060) count, and why does the fire arm reach b14=2 at get(1)=5?
Context (s5881): under NO_CRASH, held fire moves get(1) 2->5; get(10) (win, needs >=6) stays 0; fire arm hits lose arm b14=2 (gate 4 subphase 1) with get(2)=0.
Work: (1) static: find the writers of 0x80138060 (setObjectiveCount/increment, 0x800C7xxx neighbours of 7738/776C) and the lv0_checkComplexObjectives readers of get(1); name what increments it. (2) Raise the [mission-win] get cap (main.cpp s_dn<300 -> log on change only, 2000) and rerun fire x2 + nofire to see get(1) at the lose-arm onset. Positive control: pokectl shows get(10)=6 poke.
Hypotheses: (a) get(1)=enemy kills, lose arm is a timer/ally-loss rule unrelated; (b) get(1)=5 trips the lose arm (objective cap exceeded = mis-modelled threshold); (c) b14=2 comes from player death by another path.
HYPOTHESIS-ID: g1-mission-progression
