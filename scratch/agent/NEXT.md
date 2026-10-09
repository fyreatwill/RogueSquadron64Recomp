# Next work unit (s4355): independent pre-C904 stream boundary

HYPOTHESIS-ID: m5-step9-selector-decode-boundary

Session 4354 passed the whole-RDRAM positive control and retained 3,107
executions at each C904 boundary. The physical watch recorded 150 stores, all
at `0x1535AC..0x1535BC`, and zero stores in `0x1535C4..0x1545C0`, while C904
still retained the family. That selects H-earlier-stream, but is single-source.
The next unit adds an independent source-level audit and a read/write witness.

Competing hypotheses:

- H-earlier-stream-confirmed: the static call chain shows no post-C904 store
  path to the selected range, and retail read/write attribution agrees.
- H-post-C904-residual: static code identifies a store path missed by the
  s4354 physical watch or the read/write witness observes it.
- H-instrument-boundary: the independent watch fails its positive control or
  cannot qualify the C904 phase, so s4354 remains unresolved.

Discriminating measurement: first run the bounded static audit; then run one
qualified retail oracle arm with both `--watch-write 0x1535ac:0x1545c0` and
`--watch-read 0x1535ac:0x1545c0`, plus the whole-RDRAM, C904, phase, and field
controls. The static audit must enumerate every store in the C904 caller and
callee window. A complete audit with no selected-range store and no retail
selected-range write selects H-earlier-stream-confirmed; any store path or
qualified selected-range write selects H-post-C904-residual. Failed controls
select H-instrument-boundary.

Static audit:

```
rg -n -C 100 '0x8009C0D8|0x8009C0E4|0x8009C904|0x8009C950|0x11C8|0x198\\(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c
```

Exact retail command:

```
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom build/rogue_squadron.z64 --secs 120 --hit-cap 10000 --watch-write 0x0:0x800000 --watch-write 0x1535ac:0x1545c0 --watch-read 0x1535ac:0x1545c0 --c904-witness --pc-field-dump 0x8009C904,0x8009C950 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 --store-field-dump-all 1 --pc-hist-watch 1 --post-value-watch 1 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --vi-trace > scratch/agent/s4355_retail_pre_c904.log 2>&1
```

Retain the positive-control threshold and qualified C904 rows before
interpreting a zero. Do not change decoder, RSP, AI, or runtime behavior.
