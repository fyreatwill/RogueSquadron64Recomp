# Next work unit (s4345): earlier retail producer boundary

HYPOTHESIS-ID: m5-step9-retail-earlier-boundary

s4344 qualified the retail route and showed that C904's selected table words
are varied compressed-data words, while object decode-state halfwords vary
without the retained 0x0010/0x3108 family. The next unit is one bounded
producer/selector-boundary measurement plus one run.

Competing hypotheses:

- H-retail-writer: an earlier writer produces the semantic branch values before
  C904 and can be attributed by PC.
- H-retail-selector: an earlier selector/transformation derives the values
  from the compressed table stream without a direct family-valued store.
- H-retail-unresolved: the existing C904 fields are not the retained branch
  state, so the next boundary must be located from the caller/data-flow path.

Discriminating measurement: phase-gated at retail C904, watch the earlier
candidate stores/loads or the immediate caller transformation identified from
the C904 body, recording PC, source register/value, destination/selected
field, and the retained 0x0010/0x3108 comparison. A writer with the family
selects H-retail-writer; a value-producing transformation without such a
store selects H-retail-selector; neither selects H-retail-unresolved.

Before building, re-read `tools/oracle/README.md`. Add the witness to
`tools/oracle/rs64_oracle.c`, rebuild with `env CORE_SRC="$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-core" bash tools/oracle/build.sh`, then run one 180-second oracle from the repo root with:

`--watch-write 0x0:0x800000 --watch-pc 0x8009c904 --pc-phase-log-width 0x6ab400:512 --pc-field-dump 0x8009c904 --vi-trace --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start`

Require visible whole-RDRAM, title `0x00790400`, hangar `0x006AB400`, and C904
controls. Do not alter decoder/RSP/AI behavior or add a mitigation.
