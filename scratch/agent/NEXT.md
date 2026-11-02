# NEXT: G3 classify the persistent thin lines in lvl1 flight
HYPOTHESIS-ID: g3-flight-thinline

State: s6798 closed g3-wide-menus (21:9 menus/hangar = content only). Side datum: in lvl1 flight (menus route, after
continue from pause) thin straight terrain-coloured lines persist ~1.5 s, dotted when thin, thicker as the craft nears.
Seen at 4:3 (scratch/s6797/tog w275, w286, faint diagonals behind the pause emblem w078-w122) and 21:9
(scratch/s6798/tog21 w283-w285, scratch/s6798/seq.png). Not wide-only.

Hypotheses:
- H-object: real thin game geometry (e.g. long cable/beam/bolt trail model) -> present in retail at the same place.
- H-wedge: a terrain/ object triangle with a vertex near/behind the eye plane, a knife wedge too small to exceed the
  rs64_spike_scan guard (640 FB px past the viewport) -> its RDP tri has one huge edge slope and near-degenerate height.
- H-rt64: the RDP tri is sane, RT64 rasterises a sliver hardware would not (exact-edge/fan related -> check tog arms).
Discriminator, ONE run: menus route (scratch/s6798/menus.sh tag none "ROGUESQ_LIVES_CAP=1 ROGUESQ_LOG_SPIKE=1
ROGUESQ_SPIKE_CTL=64 RS64_RDP_BIN_PORT=<file>") so every tri past a 64 px guard is logged with its swap number; match
the swaps of capture frames showing the line to the logged tris (slope/height/texture). Positive control: SPIKE_CTL=64
must log ordinary near-edge tris. Then render the matching tri set offline. Also check the RDP dump of that swap with
angrylion (tools used in s6785) for the retail-rasteriser answer.
Outcomes: line tri is long-thin with sane vertices in the game DL -> H-object (check retail oracle); vertex far
off-screen with tiny height -> H-wedge (tighten cull or fix clip); tri absent/sane but RT64 draws line -> H-rt64.
