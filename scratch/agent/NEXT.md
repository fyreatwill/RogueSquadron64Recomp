# NEXT work unit (s959)

Audit the oracle source for input-plugin attachment and PIF-trace read timing,
then run one bounded 30-second positive-control arm with `--press 6:start`
using `--verbose --vi-poll --pif-trace`. The s958 pair confirmed config/help
wiring and press delivery but both stayed at VI 320 with no PIF reads. No build
or generated-code edit is needed.

HYPOTHESIS-ID: m3-slotdispatcheriter-stacksp-class

Competing hypotheses:

- H-oracle-config-path: the selected input plugin or config is not the one
  assumed by the documented recipe.
- H-oracle-core-phase: the configured core/RSP/setup remains at VI 320 and the
  game never reaches its PIF-read loop.
- H-oracle-pif-instrument: the game reads PIF, but this oracle build's trace
  hook is not attached to that read path.

Discriminating measurement: source/config wiring plus verbose runtime evidence
of input-plugin attachment and PIF reads in the same driven run. Attachment
failure selects setup; attachment with no PIF reads selects core/setup; PIF
reads without trace lines selects an oracle trace-hook defect. The whole-RDRAM
positive control must visibly fire.

Exact starting commands (create the result directory first):

`mkdir -p scratch/agent/oracle_results/s959_oracle_phase`

`rg -n "Input-SDL-Control1|Start|plugin|pif|PIF|press" /Users/williambuckley/Documents/Tools/rs64-oracle/src /Users/williambuckley/Documents/Tools/rs64-oracle/cfg`

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 30 --watch-write 0x0:0x800000 --hit-cap 200 --vi-poll --pif-trace --verbose --press 6:start > scratch/agent/oracle_results/s959_oracle_phase/driven.log 2>&1`
