# NEXT (s5911): read the msg-5 post site in audioCueDispatcherNpcHandler

HYPOTHESIS-ID: g1-mission-progression

s5910: msg 5 has exactly two posters (audioCueDispatcherNpcHandler+53528: 763; dealDamagetoDatItem: 1) in 420 s fire-held lv0. Controls fired.
Hypotheses: H-site-gate (the 763 posts are real bolt hits but selector list excludes the 12 ids); H-not-damage (site is a proximity/AI cue, unrelated to bolts); H-predicate (needs a state the player-bolt never sets).
Discriminator: static read of the call site (find guest addr: grep slotDispatcherIter(rdram in audioCueDispatcherNpcHandler in funcs with a1=5), name the predicate and selector source; then one run logging sel/a2 at that site joined with player bolt positions (apply_s5910_postra.py already prints [postra5] sel/a2 -- ra column now host-bt, fix print).
