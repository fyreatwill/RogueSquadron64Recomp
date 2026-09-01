# M5 session 3560 — image route contention qualification

The s3559 image/PCM join failed before target-phase rows. This run tested
whether the image route only fails when paired with the silent arm.

The retail control passed its whole-RDRAM positive control with 10,000 writes,
reached title VI 1024 and hangar VI 512, and had zero hits at guest PC
`0x8000834C`. That retail PC null is not evidence about the port boundary.

| arm | task handoffs | audio returns | PCM source | PCM consumer | target VIs |
|---|---:|---:|---:|---:|---|
| image, paired | 512 | 527 | 96 | 96 | 1024, 512 |
| silent, paired | 512 | 527 | 96 | 96 | 1024, 512 |
| image, alone | 512 | 528 | 97 | 97 | 1024, 512 |

All arms used one existing build, the validated LLE-solo/spin-yield/autopilot
route, and the same VI phase gate. The paired image arm reached title at
14.8s and hangar at 24.0s; the standalone image arm reached them at 14.4s
and 23.6s. No `[CRASH]` marker or `0x8000834C` last-PC failure appeared.

`H-SharedContention` is refuted by the paired-versus-standalone port arms.
This is two independent port lines of evidence, with the retail run
confirming that the phase-driving route was live. `H-ImageInputBoundary`
versus `H-ImageRouteGate` remains unevaluable: the run flags emitted
task/return/PCM witnesses but not the deeper caller, pointer/scalar, HMT,
texture, or route-edge table. No input, writer, task field, output, or gate
was changed.

Next, enable that deeper table in one same-build image/silent pair and
attribute the first missing or divergent route edge before `0x8000834C`.
Do not repeat the output join until that edge is qualified.
