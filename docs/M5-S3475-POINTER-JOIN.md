# M5 Session 3475 — joined candidate stores to the state-pointer consumer

The independent retail preflight used the whole-RDRAM positive control and
the physical candidate span `0x00110000:0x00112000`. The control and span
watch were active; consumer execution watches produced 20,950 hits and title
phase rows. Retail consumer data included live `s1` values in both the
`0x80110xxx` and `0x801Bxxxx` families.

The port build passed the pointer-writer, ordered pointer-checkpoint, and
four-PC output/state controls. It emitted 1,024 candidate store rows and 512
title-gated consumer rows. The consumer witness recorded incoming `$s1` and
the latest candidate tuple for each of `0x800027C4`, `0x800027D0`,
`0x800027DC`, and `0x80003C28`.

None of the 512 consumer rows had a nonzero latest candidate value equal to
its incoming `s1`. The recurring `0x80003C28` value was a different
`0x80111xxx` link, for example `0x80111100` while `$s1` was `0x80110D70`.
This selects `H-AlternateDispatch` for the four measured latest-store links
and rules out `H-InterveningPointerWriter` at that scope. An uninstrumented
writer or route difference remains possible.

ORIGIN: the witness only observes generated store arguments and incoming
`$s1`; it does not rewrite, skip, or validate pointer values as legitimate.
