# Next work unit: validate the active-queue empty-head invariant

HYPOTHESIS-ID: m3-active-queue-empty-head

The current M3 patch validates non-empty active-queue reachability but leaves
the empty-head branch unchecked. Audit the complete insertion idiom in
`patches/heap_guards.c`: when `*heap_other_listhead == NULL`, the published
tail node must have `next == NULL` before the append stores run. Add one guard
for that exact state, preserving the existing valid empty-queue path.

Competing hypotheses:

- H1: the empty-head/tail-successor combination is impossible in legitimate
  allocator state; the new guard is dormant and the patch is behavior-neutral.
- H2: the combination is a corrupt detached queue; the guard prevents the
  append from publishing a second chain and returns before the link stores.
- H3: the tail is a legitimate sentinel with a successor while the published
  head is null; the guard would reject valid state and must be reverted.

Discriminator: inspect the original insertion ordering and, when the MIPS
toolchain is available, run the patch with the valid empty-queue control plus
the malformed empty-head/tail-successor state. This checkout currently lacks
`mips64-elf-gcc`/`mips64-elf-ld`, so this iteration must at least compile the
host target and record that MIPS validation remains unavailable; no runtime
claim is allowed from the host build.
