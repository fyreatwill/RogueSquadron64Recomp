# NEXT work unit (after s710: cap marker and 0x06/EndDL return edges audited)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Perform one bounded static audit of the Factor 5 root-stream lifecycle behind
backlog item 1. Enumerate every write and every consumption of DMEM state
offset `0x54($18)`, which `L_1E80` loads into `r17` before returning to
`L_1090`. Trace its callers and task-root transition paths, then decide
whether cap rows can be a deliberately reloaded root stream or require a
missing termination transition. Do not rerun the recovery recipe: s694--s696
exhausted unchanged unqualified rerolls, and s710 closed the 0x06/EndDL return
edge hypotheses.

## Competing hypotheses

- **H-root-is-deliberately-reloaded:** a documented control path repeatedly
  writes `0x54($18)` and returns through `L_1E80`, making cap continuation an
  expected task-root wait under the unmodelled SP status bit.
- **H-root-stale-or-unwritten:** the cap path reaches `L_1E80` without a
  matching live root-pointer write, so it reuses stale state rather than a
  valid root stream.
- **H-cap-never-enters-root-reload:** `L_1E80` is unrelated to cap rows; the
  repeated stream originates solely in normal `0x06` list dispatch and needs
  a different lifecycle audit.

## Discriminating measurement

Produce one complete table: `0x54($18)` read/write site, value source, caller
or successor, and root-lifecycle verdict. The positive control is exhaustive
enumeration: every generated `0x54($18)` access must have a row. A recurrent
write→`L_1E80`→`L_1090` path supports H-root-is-deliberately-reloaded; a read
without a dominating write supports H-root-stale-or-unwritten; no cap-reachable
`L_1E80` path selects H-cap-never-enters-root-reload.

## Commands

    rg -n -C 12 '0X54, r18|0x54\(\$18\)|L_1E80|L_1090|L_10E8' \
      build/factor5_ucode tools/fixup_factor5_ucode.py factor5_rsp.toml
    rg -n -C 8 'root|display-list|EndDL|F3DSWRS_(DL|ENDDL)' \
      docs/F5-UCODE-REFERENCE.md docs/factor5-ucode-dispatch.md

Record the enumerated table in `docs/F5-UCODE-REFERENCE.md` or
`docs/CURRENT-TRUTH.md`; if a code correction is indicated, put it in
`tools/fixup_factor5_ucode.py`, regenerate, and run the existing phase-gated
controls in the same iteration.
