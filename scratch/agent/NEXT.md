# NEXT (s7556)
HYPOTHESIS-ID: class-gp-guest-time-consumers

GO CLOSED s7555 (tools/s7555_go_census.py rc 0, controls 7/7): no stale device status anywhere; the only time-valued getter the game
imports is osGetTime (14 guest call sites, s7555 table). GP asks whether every TIME value the guest consumes uses the same unit and
clock as the host provides, in default config and under ROGUESQ_FPS60=1 (where the frame/VI ratio changes).
Static census, tools/s7556_gp_census.py (reuse s7555 call_sites/ret_use):
- every osGetTime call site (14): enclosing function, what the 64-bit $v0:$v1 feeds (delta-time, timer deadline, RNG seed, profiler,
  audio pacing), and the conversion constant the guest applies (e.g. 0x800026AC loads 0x3B9ACA00 = 1e9: OS_CYCLES_TO_NSEC needs
  osClockRate 62.5 MHz count = 46875 ticks/ms, s7514 FK / s7402 BL);
- every guest read of osClockRate / osViClock / any VI-count global used as time, and every osSetTimer deadline the guest computes;
- under FPS60: sites that combine a time delta with a frame count (time per frame assumed 1/30 s or 1/20 s).
Hypotheses:
- H-unit-ok: every consumer's constant matches the host clock and nothing mixes osGetTime with frame counts (0 open rows).
- H-unit-mismatch: a site assumes a different rate (e.g. 46.875 MHz vs 62.5 MHz, or a hardcoded ticks/frame) -> name it, measure the
  value with a counter in one run (default vs FPS60, L1), fix.
- H-mixed: a site divides a time delta by frames or the reverse, so FPS60 changes game speed -> same-run FPS60 alt measure.
Controls (--controls): planted call site with a wrong constant -> open; a site whose value is killed -> H-ret-unused; coverage
control: the 14 sites from s7555 all appear.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
