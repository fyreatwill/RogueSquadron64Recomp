# Next: m6-mission-stall — what blocks the game thread ~75 s into the mission?
HYPOTHESIS-ID: m6-mission-stall
Fact (s5084, n=1): after mission onset + ~75 s the game thread stops (no osContGetReadData, [watch #] frozen at 7803), VI thread alive, no CRASH.
Hypotheses: (A) time-based mission stall independent of input; (B) input-triggered (Z/A press or stick extremes); (C) host-load/flake (s5047 route_flake_hostload precedent).
Discriminator, ONE iteration, two arms run concurrently-safe sequentially (one game at a time): arm1 = s5084 route with NO pad input after onset, 150 s; arm2 = repeat s5084 as-is. In both, once [watch #] stops growing for 10 s, run `sample <pid> 3` (macOS) and save thread stacks to the out dir to name the blocked wait (osRecvMesg? audio slot wait?). Positive control: padlog transitions in arm2 until stall.
Outcomes: A -> arm1 stalls at similar watch#; B -> arm1 survives; stack names the blocking primitive either way.
