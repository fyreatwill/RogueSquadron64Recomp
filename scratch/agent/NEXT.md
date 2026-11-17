# NEXT (s7498)
HYPOTHESIS-ID: m3-partition-over-live-block

Fold first: SOAK-RESULTS line for s7497_ev_levels (tools/s7497_ev_recipe.zsh; `s7497_ev_levels ev arm=` rows in its out.txt): z0_sum=0
with ctl_tri/ctl_fill/ctl_wb > 0 on L1 dd8 21:9 / L7 / L10 / L12 dd4 -> EV CLOSED 6 levels (z0_windows may be 0 on a level that never
sets Z=0; that arm then scores the control only - say so).

Work unit: class EW, RT64 writeback EXTENT vs the game's container block. EU (s7496) checked the image extent the game declares
(addr + w*480*bpp, an estimate); ER (s7493) checked that each writeback's image is live. Neither checked that the bytes RT64 actually
writes back, [phys, phys+bytes), stay inside the used heap block (or fixed partition) that holds that image: a writeback with more rows
than the game's buffer (dd8 1024-wide, RESMULT, scissor > buffer) would spill into the neighbouring block.
Hypotheses: H-ew-inside (every writeback range lies inside one used container block or a non-heap fixed region) / H-ew-spill (some
writeback ranges run past their container's end: name image, rows, width, the neighbour block's s7475 ra) / H-ew-retail (the spill is
the game's own sizing: retail buffer heights equal ours; check with the oracle's buffer sizes).
Instrument, ONE build: in main.cpp s7497_wb (rs64_wbw_post), for each NEW (base, width, rows, kind) key call rs64_s7496_overlap(phys,
phys+bytes) and classify container / partial (live spill) / free / non-heap; rows `[s7498] wb ext=` + `[s7498] sum`. Positive control,
same run: ROGUESQ_S7498_CTL=<n> extends the n-th distinct writeback query's range by 0x40000 bytes past its end, which must classify as
partial or free (not container).
Run: `env XC=ROGUESQ_S7498_EW=1+ROGUESQ_S7498_CTL=20 zsh tools/s7497_ev_recipe.zsh` (L4 dd1, L15 dd8 21:9). Outcomes: 0 partial with
the control caught -> H-ew-inside, queue the levels soak; partial > 0 -> name the image and compare its height with retail.
