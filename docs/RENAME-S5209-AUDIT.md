# Session 5209 symbol audit: `strlen`

Candidate: `strlen = 0x8003471C`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. Independent generated-tree searches found the
`strlen_recomp` body at the companion address. Its body runs from
`0x8003471C` through `0x80034740`, and the overlay record gives an exact
`0x28` span ending at `0x80034744`, matching the next companion symbol
`strchr`. There are 34 independent generated call sites in addition to the
definition.

Classification: already correctly named; preserve the existing semantic name
and do not rename. No build or soak was warranted for this naming-only result.
