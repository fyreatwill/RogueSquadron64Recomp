# NEXT (s5921): poke ship within 0.3 u of an unkilled class-1 centre

HYPOTHESIS-ID: g1-mission-progression

Context (s5920): ship has no yaw; track never within 1.8 u of any class-1 centre (r<=0.59). H-range holds.
Work unit: use ROGUESQ_PLPOS_POKE (s5891, scratch/agent/s5891_poke.sh as template) with waypoints = centres of unkilled ids (from m6/s5920b_steer/run.log [s5901] c1f=1 ctr=), PLE=2 logging; check whether [npcmsg] tmsg5 / kill fires when range < r.
Positive control: poke onto a centre of an already-killed id vs unkilled; kills must rise for >=1 poked id. Null (no msg5 at range<r) => collision uses bolt pos, not ship pos; then log bolt spawn pos.
