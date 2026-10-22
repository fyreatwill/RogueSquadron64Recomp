# NEXT (s5891): does a class-1 desc receive hits once the player is within range? (b) reachability vs (c) other
Context (s5890): s5889 INVULN log: hitsum cls=1 all zero (0 msgs) while cls=2/3 nonzero; player pos static. Single-source.
Competing: (b) player never near class-1 => zero hits (predict: after relocating player within ~100u of a surviving class-1, cls=1 m5>0); (c) class-1 shielded/unhittable even in range (predict: still cls=1 m=0 when in range, with c2 hits still counting as control).
Discriminator: one run, fire-all + ROGUESQ_LOG_PLPOS, ROGUESQ_NPC_INVULN=1; poke player pos (or drive sx/sy) to a surviving class-1 position (from [ctr1]/trig logs) at a phase-gated VI; compare cls=1 hitsum before/after in the SAME run. Positive control: cls=2 m5 keeps rising.
HYPOTHESIS-ID: g1-mission-progression
