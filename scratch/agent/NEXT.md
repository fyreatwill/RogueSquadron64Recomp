# NEXT (s5895): can real stick input steer the ship toward a survivor, and which descriptor ids are the unaimed slots?
Context (s5894): ~10 survivor slots never get bolt-line within ~2 u; H-aim selected, single run, slot ids not joined to descriptor ids.
Competing: (a) stick steers when not paused -> aim autopilot feasible; (b) stick does not steer even unpaused (input path defect); (c) slots unaimed because player is parked far in xz, not heading.
Discriminator: run s5894 recipe with AP_HOLD=600 and stick table su/sr/sd (see s5868/s5869 scripts), log [plpos] heading-sensitive fields (tilt matrices +0x74/+0xC0) and bolt dir at spawn; also print descriptor id (slot node +0x34 -> +0x78) in the [s5855] line. Control: fire counts and tilt matrix change under stick. Stick moves bolt dir => (a); not => (b).
HYPOTHESIS-ID: g1-mission-progression
