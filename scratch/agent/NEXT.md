# NEXT (s7249): fold s7248_fixed_fps_b, then decide the WIDEWIN stack's 60/s claim on a SLOW host
HYPOTHESIS-ID: widewin-heavy-window-cost
State (s7248): fixed-on L4 21:9 window off 10.06 / ww 13.16 / stack 9.59 ms, all 60/s, one run each (stack-ww -3.57 = tog -3.63/-3.88).
The positive control failed: ww did not go flat 30 because the host ran ~4 ms/task faster than in s7231 (sd_cpu 8.70 vs 12.25 ms, same code).
1. If SOAK-RESULTS has s7248_fixed_fps_b: score scratch/s7248r/log_{offb,wwb,stackb}.txt with tools/s7230_headroom.py + tools/s7229_flat30_cost.py.
2. The control needs the slow-host condition. Hypotheses: H-load (owner apps / host load raise sd_cpu: P->E core or lower clock), H-thermal.
   Discriminator, one run in scratch/s7249: run ww and stack with a fixed background load (e.g. 3 `yes > /dev/null` busy loops, killed by the
   recipe) and check ww goes flat 30 (control) while stack stays 60 (H-60). Or wait for an owner-active-but-away period. If ww stays 60 under load,
   s7231's 18.4 ms needs another explanation (compare its [g1b] qos/load columns).
Outcomes: ww flat 30 + stack 60 -> tell the owner the stack gives steady 60 with WIDEWIN at 21:9 and ask about the auto bundle; both 30 -> next lever
R=40 rescored with the hole scorer; ww 60 under load -> the s7231 cost was host-specific, re-measure s7231 a4 as-is.
