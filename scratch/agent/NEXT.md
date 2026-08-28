# NEXT work unit (s2878) — m5-route-qualification-autopilot

HYPOTHESIS-ID: m5-route-qualification-autopilot

## Work unit

The s2877 port pair again failed the title gate while the probe was otherwise
valid, so its zero rows are not evidence. First run the documented reliable
in-process `ROGUESQ_AUTOPILOT` route with the existing build and the same
image/silent arms, phase-gating at title and continuing through hangar. Do not
add another probe or interpret consumer rows until this route qualification
passes.

## Competing hypotheses and discriminator

- H-autopilot-repairs-route: both arms reach title and hangar with the
  documented autopilot route, making the existing consumer probe interpretable.
- H-autopilot-does-not-repair-route: both arms still fail before title, so the
  current blocker is not the probe or phase-relative key driver.
- H-arm-divergence: image and silent arms differ in title/hangar reachability,
  selecting an audio-arm route effect for the next discriminator.

The discriminator is one same-build image/silent table containing phase-gate
status, title/hangar reachability, crash/abort markers, and the last VI origin.
Each possible arm outcome selects one hypothesis above.

## Exact command

    # Run image/silent arms concurrently from build/ with the documented
    # in-process driver; gate at title and continue through hangar.
    env ROGUESQ_AUTOPILOT=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 \
      ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=0 PROBE_PHASE_WIDTH=1024 \
      PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
      zsh tools/probe.sh scratch/agent/s2878_route_autopilot/silent 60 1
    # Repeat concurrently with ROGUESQ_AUDIO_UCODE=1; no build is needed.

Record the phase table under `scratch/agent/s2878_route_autopilot/`; use SIGKILL,
run from `build/`, and run `git diff --check` before committing.
