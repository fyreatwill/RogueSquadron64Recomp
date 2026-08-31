# NEXT work unit — port skip-allow source into 0x800A6274

HYPOTHESIS-ID: m5-osvimode-postviewer-continuation

Session 3313 selected `H-RetailB1CWrite`: retail
`cinematicLoopBody` never takes time-pred `0x800A626C`
(`$v1=1` on 1189 printed rows). Skip-allow `$a0` stays 0 until a late
physical `0x000B0B1C` write from `0x800A9360`; then `0x800A6248` loads 1,
`0x800A6274` falls through, and `0x800A62B4` fires. Port Session 3311
keeps `$a0=0`. Ask the port which operand/writer relation is missing.

## Resume context

Skip-allow `$a0` at 6274 is computed just above:

- `0x800A6208` `andi $v0, $v0, 0x9000` after
  `getControllerNewButtonsPressed` (Start `0x1000` / A
  `0x8000`). Result copied to `$a0` at `0x800A6220`.
- `0x800A6238` `bne $v0, $zero → 6250`: incoming `$a0!=0`
  forces skip-allow=1 and skips the byte load.
- `0x800A6244` `lbu $v0, 0xB1C($t1)` from `0x800B0B1C`
  (physical `0x000B0B1C`).
- `0x800A6248` `beq $v0, $zero → 6254`: byte 0 leaves
  skip-allow 0.
- Prologue `0x800A5EE8` `sb $zero, 0xB1C` zeros the byte
  at cinematic entry.

This run is undriven (no `--press`).

## Competing hypotheses

- `H-PortIncomingA0`: port 6238 is taken with nonzero `$a0` in the
  transition window.
- `H-PortB1CWriter`: port 6238 is not taken and a named port writer makes
  `0x800B0B1C` nonzero before 6248.
- `H-PortBoth`: both operands become active in the same transition.
- `H-PortInputUnavailable`: required phase/positive controls are absent.

## Discriminator

One port build and one phase-gated run. Watch `0x800A6208`, `0x800A6238`,
`0x800A6248`, `0x800A6274`, and `0x800A62B4`, plus every writer to
`0x800B0B1C`. Whole-RDRAM writes and `[gpr-ctl]` are positive controls.

62B4 n>=1 with 6238 taken/nonzero selects `H-PortIncomingA0`; 6238
not-taken plus a named nonzero B1C writer before 6248 selects
`H-PortB1CWriter`; both selects `H-PortBoth`. Missing positive controls
selects `H-PortInputUnavailable`.

## Exact commands

Create the self-contained recipe at
`scratch/agent/s3314_port_skip_source/run.sh`, following the Session 3311
port census recipe and adding the five source watches:

```
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LOG_ALL=1 zsh scratch/agent/s3314_port_skip_source/run.sh
```

No `--press`. No M5 Step 3. No audio/output change. Require completion-
wins/SP-complete, whole-RDRAM positive control, `[gpr-ctl]`, VI
`640 @ 0x0066A500`, cinematic entry, and 62B4.
