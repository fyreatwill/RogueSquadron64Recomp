# NEXT work unit — requalify selector-store entry on reachable port route

HYPOTHESIS-ID: m5-selector-store-caller-boundary

Session 3525 landed the regeneration-safe entry witness, but the corrected
real-audio LLE/spin-yield/autopilot arm crashed pre-title at
`last-guest-pc=0x8000834c`; the port comparison was invalid. Re-run one
reachable real-audio arm with the existing entry witness and all prior
positive controls. Do not change guest state or control flow.

Competing hypotheses and discriminator:

- `H-StoreCallerAlternate`: store rows have a distinct immediate caller or
  entry path in hangar, selecting the alternate path.
- `H-StoreCallerGate`: store rows retain the known caller but an enclosing
  route gate differs, selecting the gate edge.
- `H-StoreCallerParity`: immediate store caller context matches retail while
  the AI boundary remains absent, selecting a later internal mismatch.
- `H-CaptureInvalid`: startup controls or title/hangar phase rows are absent;
  predicted no valid comparison. Selected by s3525's port crash.

The discriminating table is phase-gated title 1024/hangar 512 rows for the
entry witness (`pc=0x8008F000`, `$ra`, `a0..a3`), both store contexts,
producer context, mixer entry, known route, and AI boundary. Use the validated
route variables `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_SPIN_YIELD=1`,
`ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, `ROGUESQ_STUB_MISSING_FUNCS=1`,
the documented autopilot, and `ROGUESQ_AUDIO_UCODE=1`. Preserve the retail
oracle result in `scratch/agent/s3525_selector_oracle.log`; capture the retry
under `scratch/agent/s3526_selector_port.log` and SIGKILL the game.
