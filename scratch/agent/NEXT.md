# NEXT work unit (s1175)

HYPOTHESIS-ID: musyx-downstream-ground-truth-pointer-origin

Audit the retail writer neighborhood around physical `0x001496F8`, then run one
batched oracle watch over the bounded neighboring range with PC attribution and
the whole-RDRAM positive control. The post-step calibration has already shown
that this field remains `0xFFFFFFFF`, so no voice-array range may be inferred
from it.

Competing hypotheses and discriminator:

- H1: an adjacent field in the writer's object/global neighborhood receives a
  valid KSEG0 allocation; that field is the next ground-truth pointer lead.
- H2: the bounded neighborhood contains only sentinel/initialization traffic
  and no candidate pointer; the voice-array origin is outside this object or
  not reached by the retail path.
- H3: the whole-RDRAM control or per-watch read/write accounting regresses;
  the neighborhood result is unevaluable.

The discriminating measurement is the complete PC-attributed write table for
the bounded neighborhood, together with the whole-RDRAM threshold/removal and
separate per-watch read/write totals.

Exact commands:

    rg -n "8008F0EC|1496F8|voice.*base|musyx" /Users/williambuckley/Documents/Tools/rogue_squadron64 tools/oracle
    ./tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 10 --watch-write 0x0:0x800000 --hit-cap 10000 --watch-write 0x1496D0:0x149730 --detail-watch 1 --watch-read 0x1496D0:0x149730 --detail-watch 2 --press 6:start --hold-ms 150 --vi-trace

Require the whole-RDRAM threshold/removal and separate per-watch read/write
totals before using any neighboring pointer value.
