# Session 2975 M5 route oracle capture

The planned retail route-preparation discriminator was not evaluable. The
fixed command used the locally built debugger core, armed a whole-RDRAM write
watch and `0x80019CD8` execution watch in the same run, and passed the positive
control at 10,000 callbacks. The route-PC watch also fired (64 logged rows),
but every observed row was boot-width `320 @ 0x006DD280`; the capture did not
reach title or hangar before the debugger-watch overhead made the 45-second
window unusable.

This does not select any route hypothesis and does not justify changing the
target predicate. The falsifiable blocker is per-execution debugger overhead:
rerun the same route watch with a phase-aware arm that avoids breaking on the
boot loop, while retaining a same-run positive control.
