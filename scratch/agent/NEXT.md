# NEXT work unit (s2666) — execute M5 Step 0 ground-truth reconciliation

HYPOTHESIS-ID: m5-audio-step0-contract-reconciliation

## Work unit

Run one same-build, phase-gated reconciliation of the independent retail
oracle and the port's current image/silent audio arms. Do not change behavior.
The row must cover the whole-RDRAM oracle control, retail gate/task/voice/status
writer observations, port task fields/DMEM/DMA/exit/SP completion, service,
slot/voice, MORT, PCM source/consumer, and title/hangar phase identity. Do not
repeat the already-closed output-field census or named texture-writer audit.

## Competing hypotheses and discriminator

- `H-Step0-closes-contract`: the existing controls and oracle watches produce a
  complete row naming the next legitimate de-stub edge.
- `H-Step0-still-unmapped`: controls pass but no writer, destination/value, or
  ordering join closes; behavior must remain unchanged and the next probe must
  target the missing boundary.
- `H-Step0-control-invalid`: whole-RDRAM or phase controls fail, making all
  narrow nulls unevaluable and requiring recipe repair before M5 changes.

The discriminator is the single phase-keyed table described in
`docs/M5-AUDIO-PLAN.md`: whole-RDRAM positive control; retail writer/value;
port dispatch/task fields/DMEM/DMA/exit/SP; service/status/slot/voice; MORT;
PCM source/consumer; and route phase. A complete writer-plus-legitimacy-plus-
ordering join selects the first hypothesis; a complete control with no join
selects the second; any missing positive control selects the third.

## Exact commands

1. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`
2. `zsh scratch/agent/run_s2277_m5_step0_ground_truth.sh`
3. Inspect only bounded outputs under its result directory with `grep -c`,
   `grep -n`, and `tail -50`; do not read a full run log.

Use the recipe's existing oracle and port controls, phase-gate with
`PROBE_PHASE_WIDTH=1024` and `PROBE_KEYS_FROM_PHASE=1`, and terminate game
processes with SIGKILL. If the recipe's positive control or phase setup is
stale, repair that recipe in this iteration and report `H-Step0-control-invalid`
instead of interpreting narrow nulls.

## Expected outcomes

- Complete named writer/value/order join: select `H-Step0-closes-contract`
  and write the next one-edge behavior change into a new NEXT file.
- Controls pass but join remains absent: select `H-Step0-still-unmapped`; no
  writeback, remap, gate bypass, or guard relaxation is allowed.
- Any missing whole-RDRAM or phase control: select
  `H-Step0-control-invalid`; repair only the recipe/control next.
