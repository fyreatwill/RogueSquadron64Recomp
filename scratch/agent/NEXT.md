# NEXT (s7443)
HYPOTHESIS-ID: guest-hook-trim

Class CZ (CURRENT-TRUTH Next steps item 1). s7442 closed CY (guest rsNNNN probe helpers): every one is gated except
renamed-body wrappers. Left on the [Game] threads by tools/s7441_rs64_census.py scratch/s7442 (--min 0.002):
rs64_s6287 0.010 ms/f self (src/main/upstream_compat.cpp:3707, ROGUESQ_PPLOG test inside, but called per ?),
rs64_s6285_en 0.004, rs64_s6963_pre 0.023 incl / 0.006 self (cell-index memo, s6963; S.calls++ + s6963_tick every call),
rs64_s5660_ustore 0.002 (main.cpp).
Step 1 (offline): read each, find its generated call sites (grep the name in N64Recomp/RecompiledFuncs), classify
UNGATED-DIAG vs UNGATED-NEEDED (behaviour/memo). Sum the UNGATED-DIAG self cost.
Outcomes: H-trivial (sum < 0.05 ms/f: close the guest-hook trim campaign, no build, take CURRENT-TRUTH item 20 / the next
ITERATION.md 3c rung), H-hidden (a site does work or prints with no env: latch it at the call site via its apply/fixup
script, ROGUESQ_G1E_TRIM=0 restores; rebuild; env S7431_ARM=CZ zsh tools/s7433_probe_cost.sh; s7438_rt64_terms.py CONTROL
PASS; python3 tools/s7442_probe_gate_census.py --samples scratch/s7443 and s7441_rs64_census.py vs scratch/s7442; consumer
control: one 150 s tools/s7431_stderr_volume.sh arm with that hook's env armed must print).
