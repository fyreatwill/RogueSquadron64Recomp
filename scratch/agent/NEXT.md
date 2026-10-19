Work unit: fold s5520_b40w_{f7,base} (SOAK-RESULTS.md; logs in scratch/agent/m6/s5520_b40w_*/run.log; grep '\[b40w\]|\[saveslot\]|\[initMission\]').
Hypotheses: H1 f7 shows DC2C val=0x07 then a later reset writer (pc named) -> that site's source is the real selector; H2 DC2C never logs (store path bypassed/different B40 base) -> positive control fails, redesign; H3 B40 only written 0 by init (E974) before DC2C ordering is wrong.
Discriminator: order and pc of [b40w] lines relative to [saveslot] and [initMission] lines.
HYPOTHESIS-ID: second-distinct-mission-coverage
