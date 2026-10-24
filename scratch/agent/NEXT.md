# NEXT: G1c - fold s6068_px2_dd2_hold300_l10pu
HYPOTHESIS-ID: g1c-heap-exhaustion
Fold the SOAK-RESULTS line (tag g1c6068px2l10pu). Clean (hold>=300 alive, vi_stalls30s=0, crashlines=0) => G1c crash criterion met on L1/L5/L10; ask owner to judge look, then measure terrain fraction dd1 vs dd2 (tools/g1c_ddtog_fold.py). If it crashes, capture a backtrace - that is a real dd2/L10 datum. ALWAYS give L10 recipes ROGUESQ_FORCE_PLANET_UNLOCK=0xFF and SOAK_TIMEOUT>=1000.
