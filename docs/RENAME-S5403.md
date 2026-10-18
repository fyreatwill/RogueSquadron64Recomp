# Generated-symbol audit: `fake_func_800AE3E4`

The bounded six-surface check was rerun for the candidate named by the prior
handoff. The generated body is exactly 0xC bytes (`0x800AE3E4..0x800AE3F0`):
two frame loads followed by a floating multiply, with no callable epilogue.
The next generated and overlay entry begins at `initPlayerCraftTrailBuffers`
(`0x800AE3F0`, size `0x1D4`).

The companion mission-overlay map retains `fake_func_800AE3E4` at the same
address, and the checked-in syms table independently gives that fragment size
0xC. `recomp_overlays.inl`, `funcs.h`, and the generated definition all use
the same placeholder. No semantic name or caller evidence was found.

Decision: H3. The candidate is already synchronized and has no supported
semantic identity. No rename or generated output changed. This confirms the
earlier range audit in `docs/RENAME-S4795-AUDIT.md`.

## Next candidate

Continue with `func_800E9AE0`, applying the same exact-span and independent
semantic-evidence test.
