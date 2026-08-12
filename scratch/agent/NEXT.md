# NEXT work unit (after s709: recovery cell is retail-target-specific absent)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Perform one bounded static audit of the Factor 5 LLE synthetic-cap return path
behind backlog item 1. Enumerate every `src_kind=2` assignment and every
call/return edge that can produce it in the generated ucode plus its fixup
script. Map each edge to the real Factor 5 command semantics in
`docs/F5-UCODE-REFERENCE.md`, especially `0x06` and EndDL. Do not rerun the
recovery recipe: s694--s696 exhausted unchanged unqualified rerolls, and s709
shows the recovery cell itself is not written by retail in the driven hangar.

## Competing hypotheses

- **H-cap-is-expected-root-wait:** every `src_kind=2` edge is an intentional
  bounded wait/continuation after a valid root list; no missing guest return
  exists.
- **H-cap-misses-06-return:** a valid `0x06` child-list edge can return to the
  repeated dispatcher rather than its parent/root continuation.
- **H-cap-misses-enddl-exit:** EndDL at depth zero fails to take the root-exit
  edge on a reachable generated-code path.
- **H-probe-misattribution:** `src_kind=2` can be assigned without a cap-path
  return, so the prior dynamic classifier is not measuring the claimed edge.

## Discriminating measurement

Produce one complete table: assignment site, guarding condition, immediate
caller/callee or jump target, command kind, and reference-semantic verdict.
H-cap-is-expected-root-wait requires all reachable sites to agree with the
reference. Any reachable `0x06` or root-EndDL mismatch selects its respective
hypothesis. An assignment reachable outside the cap return selects
H-probe-misattribution. The table itself is the positive control: every
`src_kind=2` assignment found by grep must have a row.

## Commands

    rg -n -C 12 'src_kind[[:space:]]*=[[:space:]]*2|src_kind.*2' \
      build/factor5_ucode tools/fixup_factor5_ucode.py
    rg -n -C 12 '0x06|L_10E8|EndDL|endDl|L_1090|L_1088' \
      build/factor5_ucode tools/fixup_factor5_ucode.py
    rg -n -C 8 '0x06|EndDL|F3DSWRS_DL' docs/F5-UCODE-REFERENCE.md

Record the enumerated table in a new bounded section of
`docs/F5-UCODE-REFERENCE.md` or `docs/CURRENT-TRUTH.md`; if a code correction
is indicated, put it in `tools/fixup_factor5_ucode.py`, regenerate, and run
the existing phase-gated controls in the same iteration.
