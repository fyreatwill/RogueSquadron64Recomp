# NEXT work unit (s1035)

HYPOTHESIS-ID: retail-oracle-phase-environment-audit

Run one bounded retail-oracle environment/phase-path audit. Do not build or
change the recomp runtime, and do not arm the freelist watch. s1034 proved the
whole-RDRAM callback control, verified `Start = key(40)`, and showed both Start
and A pad words, yet the retail path stayed at width 320.

## Competing hypotheses and discriminator

* `H-rom-or-core-mismatch`: the oracle is not running the expected retail
  image/core configuration, so its stable width-320 path is not comparable to
  the documented timeline.
* `H-phase-marker-misread`: width 320/origin `0x006dd280` is a legitimate
  early phase in this setup, but the assumed 512 transition marker or timing
  belongs to a different configuration.
* `H-controller-protocol`: the pad words are visible at the input layer, but
  the selected input plugin/core does not expose them to the title's expected
  controller path.

Discriminating measurement: before the run, record the ROM hash, selected core,
RSP plugin, generated input mapping, and emulator mode from the oracle's own
startup/config output. In one bounded run, require the existing 10,000-callback
positive-control/removal marker, the early-boot VI/origin marker, and the
controller/PIF marker. A mismatch in ROM/core/config selects
`H-rom-or-core-mismatch`; matching identity plus a documented early-phase
marker but no 512 transition selects `H-phase-marker-misread`; matching
identity with pad activity but no PIF/controller activity selects
`H-controller-protocol`. Missing positive control invalidates the run.

## Exact command

```sh
mkdir -p /tmp/rs64-oracle-s1035
xxhsum rogue_squadron.z64 > scratch/agent/oracle_s1035_rom_hash.txt
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/rogue_squadron.z64 \
  --rsp /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-rsp-hle.dylib \
  --datadir /opt/homebrew/share/mupen64plus \
  --configdir /tmp/rs64-oracle-s1035 \
  --secs 45 \
  --watch-write 0x0:0x800000 \
  --press 6:start,11:start,16:start,21:start,21.2:a \
  --hold-ms 150 --vi-trace --pif-trace \
  > scratch/agent/oracle_s1035_capture.log 2>&1
```

Verify the generated config maps `Start = "key(40)"` before interpreting
input. The whole-RDRAM watch must be removed at the validated threshold and is
not a target; do not interpret a freelist null until a 512 hangar-origin phase
is reached.
