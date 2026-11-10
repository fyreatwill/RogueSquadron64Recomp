# NEXT: what does WIDEWIN cap 12288 (POOLX_MAX=6) cost on L4 at 21:9? (same-run tog3 hold)
HYPOTHESIS-ID: dd6-219-l4-cap12288-cost
Context: s7053 showed the default cap 10240 still binds slightly on L4 21:9: 12288 raises the far-left shoreline 2-5 rows
(score 0.08-0.17, sheet docs/owner_sheet_s7053_l4_219_cap12288.jpg). s7037 measured 12288 at +0.6 ms rsp on L1 dd8 21:9 (no edge gain there).
Whether it can be offered to the owner for 21:9 depends on the L4 frame rate.
Hypotheses:
 H-free: 12288 vs 10240 within ~0.5 fps and P(>=2VI) <= 0.03 in both runs -> offer as a 21:9 opt-in line in OWNER-OPT-INS (default unchanged).
 H-cliff: 12288 drops >1.5 fps or P(>=2VI) > 0.05 in both runs -> record, no opt-in, cap thread closed at 10240.
 H-unsafe: crash / heap or spill failure in the 12288 phases -> record.
Unit (no build):
1. cp scratch/s7049/run_hold.zsh scratch/s7054/run_hold.zsh; O -> scratch/s7054; add ROGUESQ_DD_POOLX_MAX=6 to COMMON.
   Run A: `zsh scratch/s7054/run_hold.zsh L4a 4 10240,12288,10240`; Run B (rotated): `... L4b 4 12288,10240,12288` (~11 min each,
   one game at a time). Anchor: `[s7012] widewin cap n=3 ... tog3=1` in each log.
2. Per-phase fps/rsp/P(>=2VI) with the same analysis as s7049 (grep its PORTING-STATE entry for the tl_*.bin command, xor8 split).
   The duplicated cap in each run gives an A/A for that run.
3. Update OWNER-OPT-INS 12288 line with the measured cost; ledger + commit.
Owner-gated items (G5a-G5i, L15 21:9, G1d) still need nothing run; check them first.
