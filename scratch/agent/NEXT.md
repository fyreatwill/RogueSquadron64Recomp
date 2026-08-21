# NEXT work unit (s2092)

HYPOTHESIS-ID: m5-audio-ground-truth-reconciliation

## Work unit

Run one retail-oracle ground-truth table for the MusyX gate byte and its two
nearby completion-state words before adding or changing any port instrument:
physical `0x000A0F50` (gate), `0x0014998A` (audio-task countdown), and
`0x0014974C` (audio worker flag). Keep the whole-RDRAM positive control, Rice
video plugin, VI trace, and the eleven-Start driver. Use the target-watch
detail and writer-PC histogram to identify every retail storing PC; do not
flip a gate, select the real audio ucode, alter a wait, or change a guard.

## Competing hypotheses and discriminator

- **H-RetailGateWriterMatch** — retail writes the gate byte from the named
  init/display/shutdown paths, and the countdown/flag words have active retail
  producers whose PCs can be reconciled with the generated source/fixup
  anchors.
- **H-PortOnlyGateContract** — the whole-RDRAM control and target phases pass,
  but the requested gate/countdown/flag locations have no retail writes or
  only unrelated PCs; the current port-side gate/wait behavior is not a retail
  contract at this address scope.
- **H-GeneratedAnchorMismatch** — retail target writes occur with meaningful
  PCs, but the generated tree or `fixup_game_funcs.py` lacks the corresponding
  instruction anchor; this selects an anchor/source audit, not a behavior
  change.
- **H-OracleUnevaluable** — the positive control, title phase, or hangar phase
  is absent. A null in that run is not evidence about the audio contract.

The discriminator is one table of whole-RDRAM callback count, target-watch hit
counts, storing PCs, and VI-gated target-phase coverage. Positive control plus
named retail writers matching generated/fixup anchors selects
H-RetailGateWriterMatch. Positive control plus target-phase nulls selects
H-PortOnlyGateContract only if the nearby target watches and their controls
also behave normally. A target hit with no generated anchor selects
H-GeneratedAnchorMismatch. Missing control or phase coverage selects
H-OracleUnevaluable and causes no port conclusion.

## Exact command

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 35 --hit-cap 64 \
  --watch-write 0x0:0x800000 \
  --watch-write 0xA0F50:0xA0F54 \
  --watch-write 0x14998A:0x14998C \
  --watch-write 0x14974C:0x149750 \
  --first-watch 0 --detail-watch 1 --pc-hist-watch 1 --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start
```

Require the whole-RDRAM positive-control threshold, title
`1024 @ 0x00790400`, hangar `512 @ 0x006AB400`, and target-watch summaries
before interpreting any null. If the run is qualified, crosswalk every gate
watch PC to the generated `funcs_*.c` and `fixup_game_funcs.py` anchor in the
same iteration; do not build the port until that ground-truth table is
complete.
