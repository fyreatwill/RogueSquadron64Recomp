# NEXT work unit (s2667) — make the Step 0 pair control independent

HYPOTHESIS-ID: m5-audio-step0-contract-reconciliation

## Work unit

Repair `run_s2288_m5_audio_default_step2.sh`, which the Step 0 entry point
now invokes, so the oracle still gates qualification but the silent and image
port arms launch independently (concurrently or image launch is otherwise
not gated on silent-hangar success). Preserve SIGKILL cleanup, the existing
`PROBE_PHASE_WIDTH=1024` / `PROBE_KEYS_FROM_PHASE=1` settings, and all current
marker categories. Then run the repaired Step 0 entry point once. Do not
change runtime behavior or add a new runtime instrument.

## Competing hypotheses and discriminator

- `H-Step0-closes-contract`: with both arms actually observed, the phase-keyed
  table names a legitimate writer/value/order edge sufficient to select one
  M5 behavior change.
- `H-Step0-still-unmapped`: both arms reach the target phases and controls,
  but no same-event retail writer/value plus port ordering join closes; retain
  the current image/stub policy.
- `H-Step0-port-control-invalid`: the independent oracle control passes but
  one or both port arms still fail title/hangar or their positive controls;
  repair only the driver/control next.

The discriminator is one table per arm and phase: oracle whole-RDRAM/title/
hangar controls; port dispatch, task fields/source, DMEM/DMA, image exit/SP
completion, service, slot/status/voice/reap, MORT, PCM source/consumer, and
route phase. A complete legitimate writer/value/order join selects the first
hypothesis; complete controls without that join select the second; any
missing port phase/control selects the third. A `Broke` or branch count alone
does not close the row.

## Exact commands

1. Edit `scratch/agent/run_s2288_m5_audio_default_step2.sh` with
   `apply_patch` to remove the sequential `stub_hangar` gate and launch both
   arms under the existing oracle gate, retaining bounded watchdogs and
   SIGKILL cleanup.
2. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`
3. `zsh scratch/agent/run_s2277_m5_step0_ground_truth.sh`
4. Inspect only `scratch/agent/s2277_m5_step0_ground_truth/driver.log` and
   bounded `grep -c`/`tail -50` slices of its logs.

Expected outcomes: both arm phase controls plus the oracle positive control
and a complete join select `H-Step0-closes-contract` only if the writer,
legitimacy, and ordering evidence is present; otherwise select
`H-Step0-still-unmapped` when all controls pass, or
`H-Step0-port-control-invalid` when a port control remains absent. No
writeback, remap, gate bypass, wait relaxation, or guard change is allowed
from destination overlap or a null row.
