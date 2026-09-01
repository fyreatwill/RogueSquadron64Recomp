# M5 session 3561 — image route table was target-valid standalone

The independent retail preflight could not run in this checkout: the oracle
frontend exists, but its documented Mupen64Plus core and retail ROM were both
absent. No retail null is used as evidence here.

The full target rebuilt successfully. A concurrent image/silent launch used
the validated LLE-solo, spin-yield, autopilot, and phase-gate recipe. The
image arm crashed before VI 1024 at guest PC `0x8000834C`, while the silent
arm reached title `0x00790400`/1024 and hangar `0x006AB400`/512. Because this
made the image discriminator route-invalid, the same image recipe was
immediately retried standalone from the same build.

The standalone image arm reached title 1024 at 11.7 seconds and hangar 512
at 19.9 seconds, then was deliberately killed after capture. It had no crash
marker or `0x8000834C` last-PC failure. Its positive controls were 14,358
route-order rows, 7,462 route-handoff rows, 141 route-transition rows, 20
route-state rows, 530 audio-return rows, and 196 PCM boundary rows. The
silent arm independently reached both target VIs with 14,558 route-order
rows, 7,378 route-handoff rows, 20 route-state rows, 529 audio-return rows,
and 196 PCM rows.

The requested deeper image witnesses—caller/input, HMT input, base/index,
task-contract, and selector-route—emitted zero rows in the standalone image
arm. Therefore the target-valid image/silent pair does not split
`H-ImageInputBoundary` from `H-ImageRouteGate`; those rows were absent rather
than negative. The paired crash is nondeterministic route evidence, not a
discriminator result. The target-phase output/slot/MORT contract remains the
next qualified boundary.

No game state, task field, output, gate, slot, PCM, or writeback behavior was
changed.

ORIGIN: diagnostic-only route, task, audio-return, PCM, and phase observations;
no mitigation or value rewrite was added.
