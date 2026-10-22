# NEXT (s5908): where does the caller discard a returned-1 findSegmentObjectSphereHit?

HYPOTHESIS-ID: g1-mission-progression

s5907: RET attribution correct (176/176). Fine hit returns 1 for every hit (80323f58: 627 hits, only 6 become RET).

Hypotheses:
- H-caller: the loop calling 0x8006AB4C's function (in intersectSegmentWithObject / 0x8006A944 area) rejects hits by team/owner/id/range compare or nearest-t.
- H-late: hit accepted (RET) but later damage handler ignores non-NPC class (RET=6 would then just be real).
- H-shooter: the 627 hits mostly come from shooters (rs5834_who) that are not the player bolt, so RET (player-only?) is correct.

Discriminator (one build, run scratch/agent/s5902_life.sh): in the caller after the jal, tally (class, rs5834_who, return v0, whether the loop took the accept branch). Positive control: sum of accepted == RET count (176).
Read first: static caller code around 0x8006A944..0x8006AB38 in funcs_16.c.
