# Next work unit (s4396): locate the selector/decode transform boundary

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4395 qualified retail capture strengthened H-maintenance: matches remained
in before-publication rows and the seven after rows were all nonmatching. The
next unit is one bounded oracle instrument/run that locates the remaining
selector/decode transform between the qualified title caller chain and task
publication.

Competing hypotheses:

- H-direct-prepublication: a named intermediate writer produces the selected
  word before task publication, with source/post scalar equality.
- H-later-transform: no direct semantic writer is found in the caller-to-task
  boundary, while the selected value changes at publication.
- H-maintenance-only: the existing maintenance matches persist, but no
  semantic intermediate writer/value join is observed.

Discriminating measurement: one phase-keyed table joining every candidate
writer in the title caller/decode range to the nearest type-2 task publication,
with source/post scalar comparisons and selected-word snapshots. A named
semantic writer with equality selects H-direct-prepublication; a qualified
absence plus changed publication value selects H-later-transform; only
maintenance-class matches select H-maintenance-only.
Controls are whole-RDRAM threshold >=10,000, title origins `0x00790400` and
`0x00790800`, hangar `0x006AB400`, valid type-2 rows >=1,000, ordinal overflow
0, and supported scalar mismatch 0. A missing control is invalid, not a null.

Exact commands:

    bash tools/oracle/build.sh
    bash scratch/agent/run_s4396_m5_selector_transform_boundary.sh

The script must run one 75-second Rice/oracle capture from the repo root and
write its log below `scratch/agent/s4395_m5_published_word_direction/`.
