# Next work unit: recover the Step 7 generated-tree/fixup boundary

HYPOTHESIS-ID: m5-step7-generated-boundary

Competing hypotheses and discriminator:

- H-generated-present: the external generated tree and regeneration fixup are
  available under a discoverable path; the status-03 store probe can be
  rebuilt and a phase-gated worker-entry -> `0x8009B7EC` store -> return chain
  can be run.
- H-generated-absent: the implementation/fixup inputs are not present on this
  host, so the prior runtime artifact cannot be reproduced from this checkout.
- H-wrong-fixup: the inputs exist, but the fixup's function-slice or marker
  anchor is stale and cannot produce the exact store witness.

The single discriminating measurement is a bounded filesystem/toolchain
inventory followed, only if the inputs are found, by one ordinary Debug build
and the existing retail-gated status-03 capture. A discoverable generated
tree plus rebuilt exact-store marker selects H-generated-present; no matching
tree/fixup selects H-generated-absent; a tree with a fixup/build mismatch
selects H-wrong-fixup. Do not alter the wait or force-clear status.

Exact first command:

`find /Users/williambuckley/Documents/Tools -maxdepth 4 -type f \( -name 'funcs_*.c' -o -name 'fixup_game_funcs.py' -o -name '*status*03*' \) -print`

If the inputs are found, inspect only the matching files, then use the
existing `scratch/agent/run_s4106_m5_contract_rebaseline.sh` recipe as the
phase-gated route after rebuilding. If absent, record the path/toolchain
request as the blocker rather than adding another runtime probe.
