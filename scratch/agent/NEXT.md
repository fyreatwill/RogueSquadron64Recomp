# NEXT work unit — trace immediate selector-store callers

HYPOTHESIS-ID: m5-selector-store-caller-boundary

Session 3524 selected a route-path difference: all four generated direct
`runVideoFrameTick` callers and its three guards were live in title but absent
in hangar, while both selector stores and mixer entry were live in hangar. Do
one bounded diagnostic change: instrument the immediate generated
callers/entry boundary of stores `0x8008F228` and `0x8008F264`, regeneration-
safe through the fixer, then build once and run one real-audio canonical arm.
Include the retail oracle's whole-RDRAM and `0x80029E78` controls, plus the
port phase, producer-context, store-context, mixer-entry, route, and AI
controls. No guest state or control flow may change.

Competing hypotheses and discriminator:

- `H-StoreCallerAlternate`: store rows have a distinct immediate caller or
  entry path in hangar, selecting the alternate path.
- `H-StoreCallerGate`: store rows retain the known caller but an enclosing
  route gate differs, selecting the gate edge.
- `H-StoreCallerParity`: immediate store caller context matches retail while
  the AI boundary remains absent, selecting a later internal mismatch.
- `H-CaptureInvalid`: startup controls or title/hangar phase rows are absent;
  predicted no valid comparison.

The discriminating table is phase-gated title 1024/hangar 512 rows for each
store's immediate caller/entry, both store contexts, producer context, mixer
entry, known route, and AI boundary. First run the retail oracle with
whole-RDRAM positive control and the existing `0x80029E78` watch. Use SIGKILL
for the port and capture logs under `scratch/agent/s3525_*`.
