# M5 Session 3528 — selector allocation-edge boundary

The new regeneration-safe table covered pre/post stages of all three
`rs_malloc` calls inside `allocateSongChannelArray` at `0x8008F0D0`,
`0x8008F210`, and `0x8008F23C`. The Debug build completed successfully.

The fixed real-audio/LLE/spin-yield/autopilot port run passed its controls and
reached title VI 1024 and hangar VI 512. In hangar, the effective allocator
inputs and returns were stable across all three edges; the post-delay-slot
sizes were `0x990`, `0x1E30`, and `0x1E30`, with returns
`0x801714D0`, `0x80171E70`, and `0x80173CB0`.

The independent retail oracle had a whole-RDRAM positive control, reached the
target route, and observed matching allocation returns and effective inputs
at the same PCs. Its pre-delay-slot snapshots show `$s1/a1=0x561F`, while the
port's function entry and store context show `0x5622`; this is an
entry-argument difference, not an allocator-return difference. The initial
port capture was invalid for hangar because its probe key list was
comma-delimited; the corrected space-delimited run is the qualified result.

This selects `H-AllocParity` and moves the active discriminator upstream to
the producer of `allocateSongChannelArray`'s `a1`/`s1` argument. It rules out
the three allocator edges as the source of the selector pointer difference.
No audio, selector, task, or output state was rewritten.

ORIGIN: diagnostic-only pre/post allocator, entry, store, phase, and oracle
execution observations. The allocator and selector state were untouched.

Evidence: `scratch/agent/s3528_selector_alloc_fixed/port/run.log`,
`scratch/agent/s3528_selector_alloc/oracle_phase.log`, and the successful
Debug build.
