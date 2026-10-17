# Next: generated-symbol renaming sweep — next companion-mapped candidate
HYPOTHESIS-ID: generated-symbol-renaming-sweep

Bounded work unit: select the next not-yet-renamed generated function with a
companion semantic mapping. Competing hypotheses are H-name-correct (the
companion symbol covers the exact generated function span and its live callers
support the semantic name), H-span-mismatch (the mapping crosses a split or
stale span), and H-unproven (the function has no usable live-caller evidence).

Discriminating measurement: one candidate's companion address/span comparison
plus live-caller census. Exact-span mismatch rejects the rename; a matching
span with at least one live caller selects the semantic mapping; no caller
leaves it unrenamed and selects the next candidate in a later sweep unit.

Before changing the mapping, inspect the recent sweep titles:

    grep -n '^## Session ' PORTING-STATE.md | tail -15

If this is not a sweep-only revisit, identify the next candidate and apply the
existing gates with the bounded helper/tooling. Do not build or soak unless a
mapping is actually changed.
