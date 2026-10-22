# NEXT: G1 - s5866: name the writer of player-record speed words (+0xEC/+0xF0, +0x2C/+0x34) and the gate that makes the stick a no-op
Context: s5865 - record byte-frozen over 228 rows across all stick windows; only A (0x8000) changes it (pos, +0x2C/+0x34, +0xEC/+0xF0 2.625->3.75).
Hypotheses: H28a speed words decay to 0 and the stick steering is multiplied by speed (stick*speed=0) -> no throttle = no steer (grounded/landed ship); H28b a state flag (landed/crashed/cutscene) skips the whole player update, A is a take-off/respawn trigger; H28c stick is read by a different code path (e.g. analog read gated on a mode word) not the injected axes.
Discriminator: grep RecompiledFuncs/ for stores to 0xEC(reg)/0xF0(reg) in player-craft update functions (the record base is 0x80137DC0 per CURRENT-TRUTH); then in one soak with pdump+LOG_PLPOS add a pre-spawn dump of the record words and a call counter on the writer func in the frozen vs A windows (control: counter fires in A window).
Outcome map: writer runs in frozen window but outputs 0 -> H28a (find throttle source); writer never runs -> H28b (find its caller's gate); neither -> H28c.
HYPOTHESIS-ID: g1-mission-progression
Also: backtrace Bus error far=0x3c2d5b616 / 0x37fffd040 (M6) when a run recurs it.
