# Next work unit (s4352): retail witness for the selector/decode boundary

HYPOTHESIS-ID: m5-step9-selector-decode-boundary

Session 4351 passed the retail controls and fully covered the stable base ring:
all observed C904 inputs were within `0x801B2C60..0x801B4CE0`, while the
watched span contained no exact retained family word. The next unit is one
qualified retail witness for the post-base selector/decode boundary.

Competing hypotheses:

- H-post-C904-selector: the family is published by the immediate C904
  output/selector path.
- H-decoder-state: it is formed from decoded `+0x18A/+0x18C` or stack fields.
- H-earlier-stream: the family enters before C904 from an unjoined stream.

Discriminating measurement: phase-gated retail field and writer watches must
join C904 input/base/cursor, C904 output/selector values, decoded state, and
writer PCs/source values. A family-valued post-C904 writer selects
H-post-C904-selector; a matching decoded-state value selects H-decoder-state;
neither moves the boundary to the earlier stream.

Static context:

`rg -n -C 100 '0x8009C0D8|0x8009C0E4|0x11C8|0x198\\(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c`

`rg -n -C 20 '0x8009C0D8|0x8009C0E4|0x11C8|0x198|decodeAndFillVoiceBlock' docs tools scratch`

Ground-truth command (no port build or runtime change):

```
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom build/rogue_squadron.z64 --secs 120 --hit-cap 10000 \
  --watch-write 0x0:0x800000 \
  --c904-witness --pc-field-dump 0x8009C904,0x8009C950 \
  --pc-phase-log-width 0x00790400:1024 \
  --pc-phase-log-width 0x006AB400:512 \
  --store-field-dump-all 1 --pc-hist-watch 1 --post-value-watch 1 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --vi-trace > scratch/agent/s4352_retail_selector_decode.log 2>&1
```

Retain whole-RDRAM, title, hangar, and C904 controls. Before building or
arming a targeted writer watch, bound the dynamic selector/state addresses
from the existing C904 field census; if they cannot be bounded, redesign the
witness rather than treating a null as evidence. Do not change decoder, RSP,
AI, or runtime behavior.
