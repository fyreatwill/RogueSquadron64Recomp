# Session 3242 — free-list guard ordering audit

The patch-owned `func_80007D74` path validated `head` before reading
`head->next`, but its second `popped` validation occurred after inserting
`popped` into the active queue. An invalid free-list head could therefore be
published before the guard returned.

The change moves the `popped` KSEG0 check before active-queue publication and
changes the shared predicate from a top-bit test to the actual KSEG0/RDRAM
window `[0x80000000, 0x80800000)`. The writer is the guest allocator/free-list
publication; an out-of-window pointer is not legitimate. This is a guard
ordering and range-class change, not an explanation for the VI-640 route stop.

Verification: `git diff --check` passed. The documented `PatchesLib` target is
not present in the configured build because the MIPS toolchain path is absent;
host Clang cannot parse the MIPS-only `.recomp_patch` section attribute, so a
cross-target compile remains pending on the Windows toolchain.
