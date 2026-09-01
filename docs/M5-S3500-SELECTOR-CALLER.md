# M5 Session 3500 — selector caller comparison

The independent retail oracle ran first with a whole-RDRAM write control,
Rice video, title-driving Start presses, and execution watches at
`0x80091330` and `0x80091034`. The control fired 10,000 times; both execution
watches fired 765 times in the title phase, and the predecessor relationship
was `0x80091330 -> 0x80091034`.

The port caller witness was built into the regenerated-function application
script and ran on the qualified real-image/LLE/spin-yield/autopilot route.
Title and hangar phases appeared; caller, producer, and selector-load controls
fired, with 1,024 rows at each port boundary and no crash or abort marker.

Retail caller rows were dominated by `a0=0x801772F0`, `a1=0x2`, `a2=0x1`.
Port caller rows instead included 432 `a0=0x80175960`, `a1=0`, `a2=1` rows,
plus the existing mixed `a0=0x801772F0`/`0x80175960` and `a1=0/1/...` classes.
The caller and producer rows were adjacent in the same port invocation, so
the producer-input difference is already present at the caller boundary.

This selects `H-CallerDivergence` and rules out an absent caller witness and a
producer-only transformation below `0x80091330`. It does not identify the
writer or selector state feeding the caller's `a0`/`a1` values.

ORIGIN: diagnostic-only caller-register observation; no audio state, selector,
task field, or output was rewritten, skipped, or validated.
