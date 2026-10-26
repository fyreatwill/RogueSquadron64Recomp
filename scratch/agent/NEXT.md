# G1e/G1 follow-up: pick the next unclosed rung
HYPOTHESIS-ID: m6-endurance-patched-build
The C-patch pipeline is qualified (s6269). Next: take M6 endurance on an untested route (hangar route, or levels 11-18 forced-level hold of 300 s with the patched build) via scratch/agent/g1_level_coverage_common.zsh, log any distinct crash/stall with backtrace; or, if a concrete game bug needs a C patch, add the function to tools/weaken_patched_funcs.py PATCH_WEAKEN and qualify two-arm like s6269.
