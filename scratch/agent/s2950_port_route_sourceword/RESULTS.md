# s2950 port route source-word qualification

The initial unguarded run was invalid: the new `MEM_HU(s1+0x22)` sample
bus-crashed during boot before `[f5-fetch-control]` fired. The corrected run
used KSEG0 guards and the documented LLE qualification flags.

The final run passed the same-run `[f5-fetch-control]` positive control 8
times and emitted 1,018 `[route-prep]` rows. It reached pre-title VI 640 at
origin `0x0066A500`, but never reached title 1024 or hangar 512, so there
were no target-phase rows. All pre-title rows had `accepted=0`; invalid
`s0`/`s1` route pointers caused the guarded samples to be
`source_word=0x00000000`, `source_byte=0x00`, and `branch_state=0x0000`.

Conclusion: the instrument is live and the positive control passed, but the
port has no retail-qualified target tuple. H-PrepareFieldBad,
H-PrepareTimingBad, and H-PrepareLogicBad remain unevaluable. The exact route
discriminator is paused pending a new route repair.
