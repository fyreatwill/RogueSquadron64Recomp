# NEXT work unit (s2116) — M5 image-arm C88 coverage contrast

HYPOTHESIS-ID: m5-image-arm-target-coverage

## Work unit

Run one fresh, same-build four-arm coverage experiment: default stub and
`ROGUESQ_AUDIO_UCODE=1` image arm at both explicit `C88=0` and `C88=1`.
The s2115 image arm passed positive dispatch controls but crashed before the
target phase in `waitForAnyAudioSlot+1060`; the stub arm reached title and
hangar. This unit tests whether C88 is the route-admission split before
attempting another image-task contract comparison. Do not change task fields,
DMA, exit mapping, output routing, canary, slots, PCM, waits, guards, queues,
or default behavior.

## Competing hypotheses and single discriminator

- H-C88-RouteDivergence: C88 changes image-arm pre-target admission; one image
  C88 arm reaches a target phase while the other reproduces the pre-target
  wait crash.
- H-RecipeVariance: image C88=0 is route-variable; the C88=0 image arm reaches
  a target phase in this paired window, with its C88=0 stub control also
  reaching that phase.
- H-ImagePreTargetInvariant: both image C88 arms crash pre-target at the same
  wait path while both stub controls reach target, making C88 non-discriminating
  for this coverage failure.
- H-RouteRecipeFailure: at least one stub control also misses target coverage,
  so the pair is not an image-arm-specific discriminator and the recipe needs
  a new route treatment.

The discriminator is one four-arm table keyed by arm, C88, target phase,
positive LLE/audio dispatch, crash symbol/guest PC, and target contract-row
count. Image C88=0 reaching target with its stub selects
H-RecipeVariance and reopens the contract A/B; only C88=1 reaching target
selects H-C88-RouteDivergence; both image arms failing at the same wait path
with both stubs reaching target selects H-ImagePreTargetInvariant; a stub
coverage miss selects H-RouteRecipeFailure. No empty target row is a contract
result.

## Exact commands

Use the already-built Debug binary. Launch all four arms concurrently from the
repository root:

    env GAME_EXTRA_ENV='ROGUESQ_M5_B40_VALUE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_WAIT_CONTRACT=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2116_m5_cov_stub_c0 30 12 > scratch/agent/s2116_m5_cov_stub_c0_driver.log 2>&1
    env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_B40_VALUE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_WAIT_CONTRACT=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2116_m5_cov_image_c0 30 12 > scratch/agent/s2116_m5_cov_image_c0_driver.log 2>&1
    env GAME_EXTRA_ENV='ROGUESQ_M5_B40_VALUE=0 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_WAIT_CONTRACT=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2116_m5_cov_stub_c1 30 12 > scratch/agent/s2116_m5_cov_stub_c1_driver.log 2>&1
    env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_B40_VALUE=0 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_WAIT_CONTRACT=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2116_m5_cov_image_c1 30 12 > scratch/agent/s2116_m5_cov_image_c1_driver.log 2>&1

If a process remains after its driver exits, terminate its process group with
SIGKILL. Inspect only phase lines, positive-control counts, crash tails, and
target-row counts; never read a complete run log. If an image arm reaches a
target phase, the following iteration returns to the phase-keyed stub/image
contract table with the matching C88 value.
