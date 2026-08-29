# Session 3232 — retail VI-origin attribution

## Work unit and discriminator

The competing hypotheses were `H-RetailRouteWriter` (the `0x00790A00`
transition is the watched route's legitimate publication),
`H-RetailOtherWriter` (another writer or commit path owns it), and
`H-PortOriginSelection` (retail and port share the writer/order but select
different legitimate buffers). The discriminator was a Rice retail run with
a whole-RDRAM write control, the four established route-PC watches, and
`osViSwapBuffer` (`0x80035500`) watched in the same run.

The initial 50-second run reached title VI 1024 and hangar VI 512. Its
whole-RDRAM control reached 10,000 callbacks and was removed; all four route
PCs fired once, and the VI trace included `0x00790A00` immediately before
title. The swap watch fired 1,208 times. Its phase join reported
`latched=0, joined=0`.

A 30-second retry took a different direct `0x0066A500 -> 0x00790400`
transition and did not reach `0x00790A00`; its zero route counts are
unevaluable. A second 50-second full-schedule capture again passed the
positive control, reached title and hangar, included `0x00790A00`, and fired
all four route watches once. The swap phase join again reported
`latched=0, joined=0`.

The positive control and title/hangar gates validate the oracle runs, and the
four route PCs are live at the retail transition. The requested writer-to-swap
discriminator did not produce a joined row, so none of the three hypotheses is
selected. Route-watch counts do not prove that `osViSwapBuffer` published
`0x00790A00`; no port counter or guest change is authorized.

Evidence: `oracle.log`, `oracle_fixed.log`, and `oracle_route.log` in this
directory.

ORIGIN: no mitigation or guest value was changed; the result is limited to
positive-controlled independent retail execution and VI observations.
