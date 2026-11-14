# NEXT (s7350): idiom-class audit - class AA, memcpy between ranges that may overlap
HYPOTHESIS-ID: host-memcpy-overlap
Context: s7349 closed class Z (tools/s7349_shift_census.py: 1727 shifts, 158 sites, 0 open; librecomp __ull_rshift/__ll_lshift & 63).
Idiom: `memcpy(dst, src, n)` (also std::copy over raw pointers, which is memmove-safe only for a forward overlap) where dst and src can
both point into the same object: guest RDRAM (rdram + a, rdram + b), one host ring, or one RT64 buffer. If the ranges overlap, the
result is UB (arm64 libc memcpy copies backward in some size classes, so the bytes really come out wrong).
Hypotheses: H-safe (every same-object copy uses memmove, or the ranges are disjoint by construction: separate buffers, a checked
`a + n <= b`), H-diag (only gated probes / dumps), H-ub (a default-on memcpy whose guest-chosen src/dst can overlap: real defect, fix
with memmove).
Method: new tools/s7350_overlap_census.py on the s7343 scope. Reuse s7343 args_of() and the s7338 sites() classes (C/P/G/D). Site = memcpy /
std::memcpy / __builtin_memcpy / std::copy. Classify by the base object of dst and src (s7344 base()): DISJ (different named objects,
one a local/stack array or a std::vector/.data() of a different object), MM (already memmove), CHK (overlap ruled out before the call),
H hand, B (same base, e.g. both `rdram + ...` / `RDRAM + ...` with guest offsets, no check). Controls: planted
`memcpy(rdram + task->dst, rdram + task->src, task->len)` ('?'), memmove twin (MM, not a site), disjoint twin (local buf -> DISJ),
checked twin (`if (d + n <= s || s + n <= d)` -> CHK), gated twin (G).
Runtime only if a B site exists: fix + standalone control, then `env SECS=260 zsh scratch/s7326/run.zsh s7350_dd8 ''`.
Exit: PORTING-STATE s7350, CURRENT-TRUTH item 27o -> closed/fixed, commit.
