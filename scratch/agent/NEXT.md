# NEXT (s7253): fold the slow-host / AC soaks (s7250_slowhost, s7251_dd6r_ac, s7248_fixed_fps_b)
HYPOTHESIS-ID: widewin-heavy-window-cost
State (s7252): only the 11-12 afternoon battery runs (s7230/s7231) are clock-capped (x1.36-1.44); 11-09 battery runs read 1.00-1.05 vs AC
(tools/s7252_power_tag.py + s7251_clock_ratio.py), so no wider rerun sweep is needed. Before trusting any future battery-tagged timing, run the ratio on a same-recipe AC pair.
1. s7251_dd6r_ac in SOAK-RESULTS: read scratch/s7251/arms.log (pwr=AC) and its soak log tail (headroom/flat30 per arm + clock ratio).
   - Control: dd6rd flat 30 in t=77-97 and n4 ratio s7230/AC ~1.4. Control passes + dd6r 60 -> farthest-view line holds 60 on AC: correct
     CURRENT-TRUTH line 39/220 + tell owner. dd6r 30 on AC -> dd6 radius cost is real; next lever OFFMAPCULL K=0.6 rescored in that window.
   - dd6rd holds 60 -> duty stand-in too weak (see s7250_slowhost outcome), rerun at DUTY=1.6.
2. s7250_slowhost: as in s7250 NEXT (wwd flat 30 control; stackd 60 vs 30).
3. s7248_fixed_fps_b: score scratch/s7248r/log_{offb,wwb,stackb}.txt.
4. If none ran (owner active): take the next G-ladder / Next-steps item that is offline (do not repeat the battery audit; it is closed in s7252).
