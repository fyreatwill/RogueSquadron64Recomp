# NEXT: audit the selected DC0 writer's address and value
HYPOTHESIS-ID: g1c-dd8-limit

Run exactly one bounded experiment. Extend the existing keyed probe so each
live 0x80042DC0 store records target address, byte value, table index or
out-of-table classification, and the existing span-bound decision. Retain the
per-site interval masks and post-table diff. Use one Debug build and the pinned
dd1/dd4 arms in `scratch/agent/s6492_forface.sh`; do not change game behavior
or add a mitigation.

Competing hypotheses and discriminator:

- H-DC0-legitimate: every changed-byte overlap is a target in
  `0x80130DB0..0x80130DC7` with an ordinary signed span value; this proves DC0
  is a legitimate stream refresh and moves the defect upstream.
- H-DC0-corrupt: a matching DC0 store targets outside the table or carries a
  value outside the signed span domain; this identifies the corrupt writer
  input path before any guard is considered.
- H-uninstrumented: the post-table diff is nonzero but no keyed DC0 target
  accounts for it; this reopens a host/uninstrumented writer path.

Positive controls required: keyed rows, dd1 nonempty rows, dd4 EMPTY rows, and
zero crash/VI-stall markers. Expected split is determined by the target/value
classification above; a null is not evidence unless all controls pass.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/s6492_forface.sh
