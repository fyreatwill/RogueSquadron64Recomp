# Session 5278 entry-tuple revisit

The port and retail arms were run concurrently with mission-origin phase
gates. Both whole-RDRAM positive controls fired. Retail reached both target
origins with 512-wide VI rows; the port reached both origins and its join
counter showed `c3f0=0`, with `0x800902CC` the dominant caller.

The bounded port samples and retail execution rows agree on the entry PC,
caller (`0x800902CC`), `s0`/`s1`, `a0`, `a2`, `a3`, and `v0` shape. For example,
the first `0x00690400` stride uses `s0=0x80195190`, `s1=0x8018C720`,
`a0=0x801951B8`, `a2=0x50`, `a3` equal to the audio buffer base, and `v0=2`
on both sides. `a1` is a live audio-buffer pointer and differs between runs;
it was not treated as a constant identity field. The port's `r31` is not a
valid caller witness at this host hook, so the oracle's previous-PC field is
the caller evidence.

This is two-source evidence for the caller/phase population, but not a proof
that every argument or return value matches: only three bounded port samples
per target origin were retained, and the host-side `a1` allocation is dynamic.
It rules out a distinct dominant caller path as the explanation for the
observed entry difference, but leaves H1 versus H3 unresolved. No mitigation
is authorized.
