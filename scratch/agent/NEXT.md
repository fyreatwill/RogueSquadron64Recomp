# NEXT: G1d residual - hangar/menu at 21:9 and 16:9
HYPOTHESIS-ID: g1d-aspect-hangar
G1e is CLOSED (s6254-s6262: retail 30 game fps on 60 VI/s, FPS60 lever = 60, sim delta-time; s6290 frame spacing). The old NEXT.md was stale.
Soak queued: soak_queue/s6433_aspect_hangar219.sh (hangar route, ASPECT 21:9 then 16:9, 240 s holds).
Fold from SOAK-RESULTS: rc, alive_at_end, vi_stalls30s, crashlines per arm; then view the hangar fb dumps. H-ok (hangar fills/centred, 0 crash) vs H-hangar-broken (stretch/garble/crash) -> root-cause. Then build owner contact sheet (flight 4:3/16:9/21:9 + hangar). Next rung after: G3 tick-matched livery diff, then G5.
