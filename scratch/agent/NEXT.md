# Next: owner feedback on opt-ins; otherwise a real C patch with a purpose
HYPOTHESIS-ID: cpatch-pipeline-qualification
Pipeline now qualified for no-arg (s6269) and arg+store (s6277) patches. Reserved libc names (rand) are unpatchable (N64Recomp strict mode). Do not qualify more trivial leaves: next C patch should fix or enable something real (e.g. a dd>=3 display-list pool exhaustion writer, G1c phase 2 residual, or a widescreen HUD x-position patch for G1d). Pick one, two-arm it (patched vs unpatched, positive control that the patch fires), then a 300 s hold.
