# NEXT work unit (s952)

Pre-run decision: source-only first pass; do not build, run the game, land a
guard/mitigation, or enqueue a soak until the writer/object set is classified.

HYPOTHESIS-ID: m3-slotdispatcheriter-872-class

`slotDispatcherIter+872` is the single most recurring terminal SIGBUS across
the `s790_postsec2_reachability` soak queue (s765, s820, s821, s832, s837,
s840, s844 — 7+ hits, always after VI 1024 and all positive controls pass;
see scratch/agent/SOAK-RESULTS.md). No prior session has idiom-class audited
it. This is the s938–s951 audio channel-context class's replacement as the
active M3 thread (that class CLOSED at s951 — see docs/CURRENT-TRUTH.md).

Follow the `-0x25A4` idiom-class model: grep-enumerate the whole class,
classify every site, guard or prove dead, close the class.

Step 1 (not yet done): find `slotDispatcherIter`'s guest address —
`rg -n "slotDispatcherIter" ../rogue_squadron64/symbol_files/main_overlay.txt`
— then locate its generated body in `../N64Recomp/RecompiledFuncs/funcs_*.c`
by guest address and grep for the offset(s) near `+872` (`0x368`) from
whatever base register it uses. Enumerate every writer of that
object/field across the generated source, and cross-check with companion
symbols for an independent second line of evidence per iron rule 4.

Competing hypotheses:

- H-slotdispatcheriter-872-legitimate-oob: the dereferenced object/offset is
  legitimate but the crash is a real out-of-bounds index reaching it (a real
  bug to fix, not a stub artifact).
- H-slotdispatcheriter-872-stale-pointer: the object was freed/reused and the
  `+872` dereference reads a stale or wild pointer (freelist-adjacent, per
  the s640–s659 precedent — do NOT mitigate without naming the writer; that
  precedent burned four iterations on mitigation-without-explanation).
- H-slotdispatcheriter-872-stub-artifact: the crash is downstream of an
  audio- or another degenerate-path stub rather than a genuine game-state bug.
- H-slotdispatcheriter-872-unclassified: the writer/object-origin set is not
  yet fully enumerated.

Discriminating measurement: complete generated-source inventory of
`slotDispatcherIter`'s `+872`-offset access(es) and every writer of the
object/field it reads, cross-checked against companion symbols. A reachable
writer with a provably invalid/stale value selects stale-pointer; a
consistently legitimate writer set with the crash still reachable via normal
control flow selects legitimate-oob; provenance rooted in a known stub path
selects stub-artifact; anything unresolved selects unclassified.

This is a large, multi-file source audit — consider delegating the grep
sweep itself to a subagent (as s951 did) and keeping only the classified
result in the main session, rather than reading full grep dumps directly.
