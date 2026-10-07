# Next work unit: isolate the M5 image-arm route failure

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

Competing hypotheses and discriminator (written before the build):

- H-declared-staging: default declared-size image staging is the route fault;
  the legacy `0xF80` image arm reaches both target phases.
- H-staging-independent: both image staging arms remain at VI 640 despite
  task/audio-stage rows; the fault is elsewhere in the image route.
- H-silent-residue: silent no longer reaches both phases in the paired run;
  the prior image-versus-silent split was schedule residue.

The discriminating measurement is one same-build matrix with the retail
whole-RDRAM positive control and retail title/hangar gates, followed by
sequential silent, default-image, and legacy-staging-image port arms from
`build/`. Each arm records phase gates plus task dispatch/exit, SP completion,
service entry/return, status/slot, and PCM source/consumer joins. A qualified
legacy image arm selects H-declared-staging; two image arms stuck at VI 640
select H-staging-independent; silent failure invalidates the comparison.

Use the existing Step-1 phase-gated environment, set
`ROGUESQ_AUDIO_LEGACY_UCODE_DMA=1` only on the legacy image arm, and run all
arms sequentially after the retail positive-control marker. Keep silent and
default image in the same build/run, launch from `build/`, and kill each
process with SIGKILL. Do not force-clear status 03 or change the wait. Record
the full arm comparison and route verdict in the ledger and CURRENT-TRUTH.
