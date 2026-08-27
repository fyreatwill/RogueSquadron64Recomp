# NEXT work unit (s2838) — retail gate-writer route discriminator

HYPOTHESIS-ID: m5-audio-route-gate-writer

## Work unit

Run one new same-build image/silent pair while the independent retail oracle
watches the physical gate span around `0x800A0F50` and reports writer PCs in
the title/hangar phases. Keep the whole-RDRAM oracle positive control and the
existing phase/audio marker set. Do not change a gate store or add a guard.

## Competing hypotheses and discriminator

- H-gate-route: the image/silent route split is associated with a divergent
  guest MusyX gate writer/value, and the oracle identifies a legitimate writer
  transition that can be compared with the port gate trace.
- H-gate-unreached: retail writes the gate only in a phase the port pair never
  reaches, so the gate cannot explain the pre-title split.
- H-route-independent: retail gate writers/value match the existing port gate
  contract or remain active without route divergence; the split is upstream or
  scheduling-sensitive.

The discriminator is the same-run table of oracle gate writer PC/value/phase
rows plus port gate value/phase rows, with dispatch controls and route phases.
A named retail writer/value matching the port divergence selects H-gate-route;
zero target-phase retail rows or no port/retail correspondence leaves the gate
unevaluable; matching values with different port routes rejects H-gate-route.

## Exact commands

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_s2838_m5_gate_writer.sh
grep -a -E 'oracle_gate|gate-writer|gate-value|title=|hangar=|\[phase\] vi_width=|\[audtask-dispatch\]|\[m5-gate\]|\[CRASH\]|\[ABORT\]' scratch/agent/s2838_m5_gate_writer/driver.log
```

The recipe must arm the whole-RDRAM control before the narrow oracle watch,
phase-gate narrow rows, launch both port arms from `build/`, and SIGKILL its
process group. Pre-target port or oracle nulls are unevaluable.
