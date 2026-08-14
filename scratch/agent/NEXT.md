# NEXT work unit (s1155)

HYPOTHESIS-ID: post640-state-writer

Perform one bounded static census of the state that selects the VI descriptor
after the final committed width-640 record. Enumerate every generated store to
the selector bytes at `0x8011A865..67`, the copied descriptor records at
`0x80128D50..0x80128E8F`, and the active mode/record pointers used by
`selectAndApplyViMode`; classify each writer by its caller and whether its
known phase ordering is before or after the final 640 commit. Include the
companion symbol/decomp inventory so the generated graph is not its only
 witness. Do not add a mitigation or repeat the closed submitGfxFrame owner
capture.

Competing hypotheses and discriminator:

- H1/post640-writer: a generated store is reachable after the final 640
  commit and can change the selected descriptor or active mode pointer.
- H2/prephase-only: all generated stores are boot/pre-640 or ordinary copied
  initialization, so no generated post-640 state writer exists.
- H3/non-generated-owner: the generated census is complete but the active
  post-640 state is written by host/runtime or another non-generated path.

The discriminating measurement is one complete address-and-caller table,
cross-checked against companion symbols: a post-640 generated writer selects
H1; no post-640 generated writer with a complete generated/companion inventory
selects H3 as the next runtime-owner audit; an incomplete or conflicting
inventory is inconclusive and must be repaired before any conclusion.

Commands (from the repository root):

    rg -n "8011A865|80128D50|80128DA0|80128DF0|80128E40|selectAndApplyViMode|osViSetMode" src lib docs scratch
    rg -n "8011A865|80128D50|80128DA0|80128DF0|80128E40|selectAndApplyViMode|osViSetMode" /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp /Users/williambuckley/Documents/Tools/rogue_squadron64 2>/dev/null
    git diff --check

Record the full bounded inventory and its classification in the ledger and
CURRENT-TRUTH. If a runtime arm is required to resolve ordering, batch all
markers in one build, retain an independent positive control, and gate on VI
transitions rather than elapsed time.
