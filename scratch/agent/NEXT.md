# Next work unit: why does the flown mission end at ~10 min?
HYPOTHESIS-ID: m6-mission-endurance

s5420: flown hold leaves the mission (origin 0x690400 -> 0x790400 title) at 634 s; clean otherwise. Hypotheses: (H1) player dies; (H2) objective completes -> debrief -> title; (H3) autopilot 'r'/start mash selects quit.
Discriminator: fix the dump to use the VI width as stride so frames decode; rerun scratch/agent/m6_flown_hold.sh (tag s5421_b, 1200 s, background) and view frames just before the transition (dump every 200 swaps), plus a variant with no 'r'/start keys after t=100 (H3 control). H3 -> disappears without 'r'; H1/H2 -> persists and the frame shows death/debrief.
