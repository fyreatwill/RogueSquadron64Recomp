# NEXT work unit (s2222) — broaden the retail key-on PC witness

HYPOTHESIS-ID: m5-audio-keyon-contract

## Work unit

Run one independent retail oracle census with a PC watch for every instruction
in `musyxKeyOnVoice` (`0x80090A3C` inclusive through `0x80090E00`), retaining
the whole-RDRAM positive control, both 640 target origins, and the 512 hangar
phase. Compare its range histogram and register fields with the already
captured s2221 port table; do not build or remove a key-on return in this unit.

Competing hypotheses and the single discriminator:

- H-RetailSkipsInterior: after positive coverage, retail executes only the
  entry/tail boundary PCs and no interior divide/return address at target or
  hangar; the s2221 port divides are a port-route difference.
- H-RetailExecutesAlternateInterior: retail executes interior PCs in the
  function range, but not the eight watched addresses; the range identifies
  the real arithmetic path and its `$v0/$s1/$a0/$a2` values.
- H-PCWatchCoverage: the range watch does not produce a usable per-PC table
  despite the positive control or fails to reach target/hangar; no site
  conclusion is allowed.
- H-PortOnlyInterior: retail has boundary-only execution while the s2221 port
  has four divisor witnesses at `0x80090CEC`, `0x80090D30`, `0x80090D74`, and
  `0x80090DB8`; this separates a real port/retail route difference from a
  narrow-watch artifact.

The discriminator is the same-run range-PC matrix keyed by target origin and
hangar phase, with the whole-RDRAM callback count and VI phase controls. A
range row inside the function proves the narrow eight-site null was a watch
selection issue or alternate path; boundary-only rows with the existing port
divide table select the port/retail difference; missing controls select
coverage failure. Do not infer operand validity from a PC count alone.

## Ground-truth command — run before any port build or new instrumentation

~~~sh
pc_list=""
for ((pc=0x80090A3C; pc<0x80090E04; pc+=4)); do
  [[ -n "$pc_list" ]] && pc_list+=","
  pc_list+=$(printf '0x%08X' "$pc")
done

tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 60 --vi-trace --status-poll \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --watch-write 0x0:0x800000 \
  --watch-pc "$pc_list" \
  --pc-phase-log 0x00696100 --pc-phase-log 0x00696600 \
  --hit-cap 25 \
  > scratch/agent/s2222_retail_keyon_range.log 2>&1
~~~

Required controls: `positive-control threshold reached`, whole-RDRAM writes
at least 10,000 with removal `rc=0`, repeated 640 rows at both target origins,
and a 512 row at `0x006AB400`. Use `rg '^\\[oracle\\] watch pc'` for the
per-PC matrix and `rg '^\\[vi'` for phase coverage. Compare against
`scratch/s73_post_a_scene/m5-audio-keyon-census/run.log`. No default, gate,
task-field, safety-guard, or early-return change is authorized by this unit.
