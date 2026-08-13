# NEXT work unit (identify the parser-side E9 count filter)

HYPOTHESIS-ID: m3-e9-parser-filter-join

Perform one bounded source audit; do not change runtime behavior and do not
rerun the game unless the source audit is ambiguous. Compare the bridge's
`g_rdram_for_submit[p ^ 3] == 0xE9` test with RT64's `dl->w0 >> 24` raw-op test
at both the direct display-list walk and pending-command completion path.
Enumerate every guard between raw-op recognition and `++s_rdp_advance_task_e9`,
then reconcile the result with s833 tasks 570, 580, 632, and 649.

Competing hypotheses and discriminator:

- H-byte-order: the two paths inspect different physical bytes. Prove or
  refute by deriving the byte address and endian conversion on both paths.
- H-pending-path: only pending-command completion changes the count. Prove or
  refute by classifying each increment site and its command-buffer conditions.
- H-other-filter: a guard/callback gate suppresses increments after raw E9 is
  recognized. Prove or refute by enumerating the complete predicate.

The result must identify one branch or explicitly show why a single
phase-gated probe is required. If a probe is required, design one build with a
positive control that records both bridge-tested byte and parser raw opcode;
do not build a partial instrument.

Expected commands: `rg -n` the bridge byte test, both parser increment sites,
`MEM_B`, `DisplayList`, pending-command setup, and all `return`/guard
conditions in bounded source windows. Use the existing s833 log only for the
four reconciliation rows; no mitigation is authorized.
