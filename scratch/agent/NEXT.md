# NEXT: owner max recipe (dd6 bundle) per-level sweep: does every level reach flight and hold at 16:9 and 21:9?
HYPOTHESIS-ID: dd6-bundle-level-sweep
Context: s7036-s7040 qualified the dd6 + WIDEWIN + MELT auto bundle (OWNER-OPT-INS "Farthest view" line) on L1, L4, L5 (holds) and the cutscene playlist,
at 21:9 and (s7040) 16:9 on L1/L4. The owner will fly every mission with that one line; levels 0, 2, 3, 6-9, 11-18 have never run at dd6 + WIDEWIN + bundle.
This is qualification of a new opt-in recipe, not a G4 repeat-hold crash hunt.
Unit, one game at a time: scratch/s7040/run_hold.zsh-style hold (16:9, tog3 R=-1,2,2 K=0,0.6,0.6 so the cost split comes free) on 4-5 unrun levels per iteration,
starting with L2, L3, L6, L7 (L10 cloud level has no terrain grid: health only). Per level: alive_at_end, vi_stalls30s, crashlines, fl fps per phase
(g5e_cost_by_parity --phases 3 --skip-s 130), [s7031] ocull/f per phase. Note arm.zsh tags m6 dirs by level+name (g1_lvl<L>s7031<name>): use unique names.
Outcomes: H-clean (all hold, bundle phase >= off phase fps) -> extend OWNER-OPT-INS level list; H-fail (crash/stall/fps drop on a level) -> root-cause that level
(backtrace, writer), it is a datum; H-nocull (ocull 0 on a level) -> note it, bundle harmless there.
