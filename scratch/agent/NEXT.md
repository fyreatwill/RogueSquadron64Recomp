# NEXT work unit (after s711: root-loader state field excludes cap reload)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Perform one bounded static audit of the Factor 5 fetch-pointer lifecycle behind
backlog item 1. Enumerate every generated-main assignment to `r17` and every
direct/indirect predecessor of `L_1090`, then classify whether it starts a
root stream, advances an ordinary command, loads a 0x06 child, or restores an
EndDL parent. The s711 audit proves the root loader enters `L_1090` only once
per loader return; this unit tests whether a cap row can nevertheless loop by
an erroneous `r17` continuation. Do not rerun the recovery recipe: s694--s696
exhausted unchanged unqualified rerolls.

## Competing hypotheses

- **H-r17-command-advance:** all cap-reachable writes advance a valid command
  or take a documented 0x06/EndDL frame edge; the long stream is a legitimate
  open chain, not a reloaded root.
- **H-r17-stale-reload:** a cap-reachable predecessor assigns `r17` from root
  state or an unmatched saved frame, restarting/reusing a stream incorrectly.
- **H-r17-unmodelled-dispatch:** an indirect handler/return reaches `L_1090`
  without a statically classifiable `r17` update; the missing semantic is in
  that dispatch family rather than the root loader.

## Discriminating measurement

Produce one complete table: `r17` write site, value source, successor, and
whether the edge can reach `L_1090`. The positive control is exhaustive
enumeration: the count of table rows must equal the generated-main `r17 =`
assignment count, with each direct `goto L_1090` and indirect jump-table case
accounted for. Only advance/frame edges support H-r17-command-advance; a
root/saved-frame reload without its matching lifecycle edge supports
H-r17-stale-reload; an unclassifiable dispatch edge selects
H-r17-unmodelled-dispatch.

## Commands

    rg -n -C 6 'r17 =|L_1090:|goto L_1090|case 0x1090|L_1088:|L_10D8:|L_12A0:|L_12DC:' \
      build/factor5_ucode/factor5_ucode_recompiled.c
    rg -n -C 8 'F3DSWRS_(DL|ENDDL)|pointer advance|inline data|root' \
      docs/F5-UCODE-REFERENCE.md

Record the enumerated table in `docs/F5-UCODE-REFERENCE.md`; if a code
correction is indicated, put it in `tools/fixup_factor5_ucode.py`, regenerate,
and run the existing phase-gated controls in the same iteration.
