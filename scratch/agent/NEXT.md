# M5 audio plan: all rows qualified/closed on title+hangar; choose the mission-phase audio checkpoint

HYPOTHESIS-ID: m5-audio-destub-mission-route

s4805 qualified Step 8 A9 (0 bad / ~2.4M checks, 10/13 sites reached, writer in range). Every M5 plan row is now qualified or closed on title/hangar.
Work unit: extend the A9 + A10 instruments (ROGUESQ_LOG_M5_A9=1, ROGUESQ_LOG_M5_A10=1) to a mission-reaching route ONLY IF a driver reaches origin 0x00690400 (none has since s4759; VI-640 stall s4797 is nondeterministic). If no driver reaches it in one attempt, go to strategic item 4 REVISIT (retail-entry boundary, CURRENT-TRUTH Next steps) with a genuinely new angle, or declare BLOCKED asking for a retail mission capture (needed to evaluate the 0x2C splice, s4804).
Hypotheses: H-A9-mission-valid (guards inert at mission, 3 unreached sites finally hit), H-A9-mission-bad (a guard fires -> name writer before any change), H-route-absent (unevaluable).
Discriminator: a9rows with bad>0 or the 3 unreached sites' first row, with forced-arm control in the same build (scratch/agent/run_s4805_m5_a9.sh as template).
