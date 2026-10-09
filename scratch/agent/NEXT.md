# Next work unit (s4344): value-aware retail C904 witness

HYPOTHESIS-ID: m5-step9-retail-branch-boundary

s4343 qualified the retail route and rejected a phase-local writer to the
backing table, but the range watch did not expose values. The next unit is one
bounded oracle instrumentation change plus one run, all arms in that build.

Competing hypotheses:

- H-retail-table-value: the selected object-backed word carries the retained
  `0x0010/0x3108` family.
- H-retail-selector-value: the table word does not carry the family, but the
  decoded halfwords/state at C904 do.
- H-retail-earlier-boundary: neither value family matches at C904; the
  producer/semantic boundary is earlier.

Discriminating measurement: at retail `0x8009C904`, phase-gated to
`0x006AB400`, print `$s1`, `object+0x11C8`, the selected word at
`object+0x1A0+((cursor>>3)&0xFFC)`, and the decoded halfwords/state used by the
helper. A table-word family selects H-retail-table-value; a non-table decoded
family selects H-retail-selector-value; neither selects H-retail-earlier-boundary.

Before building, re-read `tools/oracle/README.md`. Add the witness to
`tools/oracle/rs64_oracle.c`, rebuild with `env CORE_SRC="$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-core" bash tools/oracle/build.sh`, then run one 180-second oracle from the repo root with:

`--watch-write 0x0:0x800000 --watch-pc 0x8009c904 --pc-phase-log-width 0x6ab400:512 --pc-field-dump 0x8009c904 --vi-trace --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start`

Require visible whole-RDRAM, title `0x00790400`, hangar `0x006AB400`, and C904
controls. Do not alter decoder/RSP/AI behavior or add a mitigation.
