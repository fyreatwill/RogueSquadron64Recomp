# NEXT: G1c - fold s6066_px2_dd2_hold300_l10a/b, then terrain fraction dd1 vs dd2
HYPOTHESIS-ID: g1c-heap-exhaustion
Fold the two SOAK-RESULTS lines (tag g1_lvl10g1c6066px2l10a/b): need one with hold>=300 alive vi_stalls30s=0 crashlines=0. If both are nomission again, root-cause the L10 route flake (keys.log nomission-att*, fail_att*.log at origin 0x62BD00) - it also hits dd1, so it is a G1/G4 datum, not G1c.
If a hold is clean: G1c crash criterion met (L1,L5,L10); ask owner to judge look, then measure terrain fraction dd1 vs dd2 with metric() in tools/g1c_ddtog_fold.py on fixed-dd fb dumps.
