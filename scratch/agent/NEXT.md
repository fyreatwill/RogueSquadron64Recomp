# Next work unit (s4354): bounded selector/decode writer witness

HYPOTHESIS-ID: m5-step9-selector-decode-boundary

Session 4352 passed the retail controls and recorded 989 rows at each C904
boundary. The retained family was present at C904 itself (`584` rows of
`0x3108`, `405` of `0x0010`), but the configured post-value watch was only
`0x8009C0E8..0x8009C0EC` and fired zero times. That is an instrument-boundary
result. The same rows bound selected addresses to physical
`0x1535C4..0x1545BC`; decoded object fields are around physical `0x1535AC`.
The next unit is one qualified retail writer watch over those bounded ranges.

Competing hypotheses:

- H-post-C904-selector: a writer in the selected-address range publishes the
  family after C904.
- H-decoder-state: a writer in the decoded object fields publishes the family.
- H-earlier-stream: neither bounded range writes the family; it enters before
  C904 from an unjoined stream.

Discriminating measurement: in one run, retain the whole-RDRAM, title, hangar,
and C904 controls while watching physical `0x1535AC..0x1545C0` with writer-PC
and source-register attribution. A family-valued write in the selected-address
subrange selects H-post-C904-selector; a family-valued write to decoded
`+0x18A/+0x18C` selects H-decoder-state; zero family-valued writes in both
bounded ranges selects H-earlier-stream. A zero result is valid only if the
watch itself has positive-control hits and the C904 rows remain qualified.

Exact command:

```
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom build/rogue_squadron.z64 --secs 120 --hit-cap 10000 --watch-write 0x0:0x800000 --watch-write 0x1535ac:0x1545c0 --c904-witness --pc-field-dump 0x8009C904,0x8009C950 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 --store-field-dump-all 1 --pc-hist-watch 1 --post-value-watch 1 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --vi-trace > scratch/agent/s4354_retail_selector_writer.log 2>&1
```

Retain whole-RDRAM, title, hangar, and C904 controls. A positive-control watch
and qualified C904 rows are required before interpreting a zero. Do not change
decoder, RSP, AI, or runtime behavior.

Static context:

`rg -n -C 100 '0x8009C0D8|0x8009C0E4|0x11C8|0x198\\(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c`

`rg -n -C 20 '0x8009C0D8|0x8009C0E4|0x11C8|0x198|decodeAndFillVoiceBlock' docs tools scratch`

The selector/state ranges are bounded by s4352 field rows; do not widen them
without a positive reason.
