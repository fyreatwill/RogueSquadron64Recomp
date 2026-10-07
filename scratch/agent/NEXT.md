# Next work unit: qualify the M5 A11 terminal transition on a valid route

HYPOTHESIS-ID: m5-a11-terminal-transition

Use one rebuilt canonical real-audio/LLE/ungated/solo/spin-yield port and the
independent retail oracle. The route is now valid: the s4144 port reached title
and hangar without the known pre-hangar crash. Capture the A11 wait, slot-state,
terminal, and post-wait rows in both target phases without changing behavior.

Competing hypotheses and discriminator:

- H-A11-terminal-reaches: both arms pass whole-RDRAM/title/hangar controls and
  the port emits a complete terminal transition after `waitForAnyAudioSlot`.
- H-A11-terminal-missing: the route is valid but the terminal transition or
  post-wait row is absent in the port while retail reaches the corresponding
  phase-keyed boundary.
- H-route-invalid: either positive control or target phase is absent, or the
  port again hits the known pre-hangar `musyxSynthFrame+3828` boundary.

Before building, verify the existing A11 probe and its positive-control env vars
in the tracked debug catalog. Build once. Run the retail oracle first with the
whole-RDRAM control and title/hangar phase gates, then run the canonical port
from `build/` with the same gates. Do not change guest behavior, audio waits,
caps, predicates, slot state, or host writeback.

Expected outcome: qualified paired terminal rows select reaches or missing;
any missing gate or known pre-hangar crash selects H-route-invalid.
