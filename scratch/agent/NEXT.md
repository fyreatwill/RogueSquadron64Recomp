# NEXT work unit (s2478) — validate the host-local continuation bridge in target phase

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Single work unit

Run the existing driven target-phase port recipe against the s2477 bridge. Use
one build/run capture; do not add another bridge, runtime API, NULL guard, or
audio/output remap before this discriminator.

## Competing hypotheses

- H-BridgeGenerated: returning from `convertMat3x4ToN64Mtx` resumes the sole
  generated caller's `after_4` path and the target phase advances.
- H-BridgeRuntime: the host return is insufficient and a reusable runtime
  continuation mechanism is required.
- H-TailContractStillWrong: the converter's `jr $t9` contract is not the
  caller-local `after_4` continuation.

## Discriminator

The pass arm must reach the target 640/512 route and show no
`Failed to find function at 0x800155EC` or `get_function(0)`. Reaching the
existing work after `after_4` selects H-BridgeGenerated. A different immediate
converter failure selects H-TailContractStillWrong. An unchanged lookup
failure selects H-BridgeRuntime or proves the bridge was not applied; inspect
the generated marker before choosing between them. The same capture must keep
the existing indirect-resolver positive control and phase-gate any M5 result.

## Exact command

First verify the existing driver is available:

```sh
test -x tools/winctl/winctl || test -x "$HOME/bin/winctl"
```

Then run the already-established single image-arm driven recipe from the repo
root (its eleven-start schedule reaches the target route):

```sh
zsh scratch/agent/run_s2327_m5_task_ordinal_prepost_join.sh
```

Capture under `scratch/agent/s2478_m5_continuation_bridge_validation/`, kill
the game with SIGKILL, and do not interpret a run that fails its route-control
gate. If the driver is unavailable, record that concrete setup failure and
use `SUBSTITUTED` only with a falsifiable replacement experiment.

Ground truth: no new runtime instrument is planned. If a new one becomes
necessary, first run the retail oracle whole-RDRAM and driven-VI controls.
