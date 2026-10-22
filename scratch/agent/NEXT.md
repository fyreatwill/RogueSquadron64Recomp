# NEXT: G1 - s5876: fold s5875_hold600_mtm soak; identify the object whose 0x184 timer expires at 0x800B1140
Hypotheses: (a) legit mission timer (objective time limit) - mission is meant to end/fail; (b) our dt (a1) is wrong/huge or timer init (obj+0x184) is uninitialised/zero from an unimplemented spawn path; (c) object is an NPC/ally despawn timer that should not drive mission end (phase gate wrong).
Measure: read [bit1] lines in scratch/agent/m6/s5875_hold600_mtm/run.log (slot, lives, s1 vs [m47] vi). Then add a one-build logger (apply_s5876) at 0x800B1024 entry printing s1, [s1+0xB8], [s1+0xBB], dt(f6), [s1+0x184] for the first 3 calls per object, to see initial timer and per-frame dt. dt ~1/60 sane => (a)/(c); dt wild => (b).
HYPOTHESIS-ID: g1-mission-progression
