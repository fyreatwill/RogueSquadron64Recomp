# NEXT: G1 - s5864: why stick input does not steer the ship (real-input aiming prerequisite)
Context: s5863 closed the aim/altitude question (TELE_BOLT already is the forced arm; natural hit rate 9/2049, collider r~0.2u). Real input needs pitch/yaw aiming, but s5821 measured the ship frozen under stick-up/right/down holds and moving only with A.
Hypotheses: H25 port delivers stick axes to the game in the wrong field/sign/scale (SDL->OSContPad mapping, or the key-driven harness only synthesises buttons, not axes); H26 flight code ignores the stick in the mission phase tested (state/gate, e.g. autopilot/intro lock); H27 stick works but deadzone eats the injected magnitude.
Discriminator: in ONE run log the axis bytes at the controller read (osContGetReadData result) and the flight code's consumed axis value while the harness holds each direction, with a positive control (button bit visible in the same struct). Axis nonzero in struct but flight unchanged -> H26; axis zero in struct -> H25/H27 (check harness key->axis mapping first, boring-first).
HYPOTHESIS-ID: g1-mission-progression
Also: backtrace Bus error far=0x3c2d5b616 / 0x37fffd040 (M6) when a run recurs it.
