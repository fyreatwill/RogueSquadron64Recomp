# NEXT: G1e — DPC bridge per-call cost with line-level attribution (dense lvl5 dd4 FPS60 ~8.6 ms / 57 tasks/s after s6715)
HYPOTHESIS-ID: g1e-rsp-segment

First fold SOAK-RESULTS lines s6715_pg_lvl1_dd1 / s6715_pg_lvl10_dd4 (probe gate OFF forced, 300 s). A failure there is
the work unit: A/B with ROGUESQ_G1E_PROBES=1 on the same recipe; suspect a gated probe with a hidden side effect
(rs64_m4_y8000_step counter, inline_probe_dispatch state).

## Hypotheses
- H-bridge-diag: rsp_dpc_submit_impl's ~1300-line per-submit path (dpc-fwd atomics, op histograms, ==8 block op6 cases,
  log_* gates, shadow vector insert) costs ~100 self samples of ~1100 (~9%); a no-diag fast path or trimmed blocks give >=5%.
- H-bridge-essential: the cost is the defer emplace + s4272 shadow insert + stream flush (needed); <3% removable.
- H-floor: interp at its floor; dense dd4 ceiling ~57/s.
## Discriminator (one run)
Run `zsh scratch/agent/s6715_probes.zsh 5 4 prof` (edit: drop PROBES_TOGGLE, add ROGUESQ_G1E_PROBES=0). In flight
(dense phase 7 rows, ~95 s in) attach:
  DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcrun xctrace record --template 'Time Profiler' --attach <pid> --time-limit 15s --output /tmp/s6716.trace
(s6715: plain `xctrace` failed with "requires Xcode" — use the DEVELOPER_DIR form.) Export time-profile table, aggregate
leaf PCs inside rsp_dpc_submit_impl, symbolize with atos -o build/RogueSquadron64Recomp -l <load addr> to source lines.
Then one build with ROGUESQ_G1E_BRIDGE_TOGGLE same-run flip of the trimmed path; fit with g1e_fast_ab.py (add --key bridge).
Outcomes: >=5% dense ms -> land; <3% -> write the G1e dd4 ceiling into CURRENT-TRUTH and take G3 render fidelity.
