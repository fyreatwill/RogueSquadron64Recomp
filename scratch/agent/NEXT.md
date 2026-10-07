# Next work unit: re-baseline the complete M5 image/silent contract on a qualified route

HYPOTHESIS-ID: m5-audio-contract-rebaseline

Before any build, write the competing hypotheses and discriminator into this
file: H-contract-live predicts both image and silent arms reach the target
phases with dispatch/SP/task controls; H-route-only predicts only a route
change while task/service/slot controls remain absent; H-audio-degeneracy
predicts the image arm adds service/slot/PCM progress beyond the silent arm.
The discriminator is one same-build, phase-gated matrix containing the oracle
whole-RDRAM control, retail title/hangar, port title/hangar, both arm identities,
task dispatch/exit, SP completion, service entry/return, status/slot rows, and
PCM source/consumer joins. Any missing route control makes downstream nulls
unevaluable.

Use the existing Step-1 phase-gated recipe/configuration, but repair any
startup/path defect before running it; launch from `build/`, keep
`ROGUESQ_AUDIO_UCODE=0` and the default image arm in the same build/run, and
kill the process group with SIGKILL. Do not force-clear status 03 or change
the wait. Record the full arm comparison and route verdict in the ledger and
CURRENT-TRUTH.
