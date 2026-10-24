# NEXT: G1c - fold s6050_dd{1,2}_l{5,10} (levels 5 and 10 at 2x)
HYPOTHESIS-ID: g1c-draw-distance
Hypotheses: H-holds (2x survives 300 s on lvl5 and lvl10 with the span-table bound) vs H-levelspecific (another unbounded writer / smaller terrain on those levels crashes).
Discriminator: SOAK-RESULTS s6050_dd2_l5 / dd2_l10 rc and summary (crashlines, vi_stalls30s); controls dd1_l5 / dd1_l10 must be rc=0. grep -a '[spanbound]' and '[gridlog]' in scratch/agent/m6/g1_lvl*g1cdd2l{5,10}/run.log for skips and window w.
If crash: lldb backtrace, name the writer (iron rule 11). If both pass: G1c half done; build the G1b per-VI wall-clock instrument for the frame-time clause, then ask the owner to judge the look.
