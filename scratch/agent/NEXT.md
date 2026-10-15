# Next work unit

HYPOTHESIS-ID: m5-retrace-pacing-vs-retail

s4901: port = 2 retrace returns (and ~2 synth entries) per TRUE fb-origin change (4642/4644 hangar); retail = 1 per origin change (s4900). Aliasing explained 0/2; the real gap is 2:1.

Hypotheses: H-slow-frame (port game frame takes >1 retrace, e.g. CPU/RSP/RDP wait stalls so it misses every other retrace); H-divider (game's frame-limiter counter/min-retrace-per-frame variable differs, set from a stubbed/uninitialised value); H-vi-rate (port retrace rate itself is 2x retail per wall second so 1 swap per 2 retraces is the same game rate).
Discriminator: in one port run log wall-time per retrace return and per swap (rate in Hz) plus the game's frame-limiter variable; retail oracle: same variable via watch. Rates: port swap Hz ~ retail swap Hz => H-vi-rate; port swap Hz ~ half => H-slow-frame/H-divider (check variable value vs retail). Find the variable by grepping decompiled code around the swap caller for a retrace-count compare.
