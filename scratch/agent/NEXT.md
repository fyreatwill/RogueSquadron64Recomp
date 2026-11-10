# NEXT: does WIDEWIN cap 12288 (POOLX_MAX=6) stay under the VI cliff on L12 at 21:9? (same-run tog3 hold)
HYPOTHESIS-ID: dd6-219-cap12288-l12
Context: s7054 measured 12288 on L4 21:9 as ~free (rsp +0.25 ms, fps inside A/A). s7053 showed it buys a few far-shoreline rows on L4.
L12 is the load-bearing level at 21:9 (s7049: 10240 at 56.3-59.0 fps; s7048 ~56). The opt-in line must say whether 12288 hurts there.
Hypotheses:
 H-free-L12: 12288 vs 10240 within the same-run A/A spread in both runs, P(>=2VI) not >0.03 above 10240 -> OWNER-OPT-INS: 12288 fine at 21:9 everywhere tested.
 H-cliff-L12: 12288 drops >1 fps beyond A/A or P(>=2VI) +0.04 in both runs -> OWNER-OPT-INS: 12288 costs L12, keep 10240.
 H-noop-L12: ring_sum/f not higher at 12288 (window already bounded on 88x88 L12) -> cost/benefit moot there; record.
Unit (no build):
1. cp scratch/s7054/run_hold.zsh scratch/s7055/run_hold.zsh; sed O -> scratch/s7055. Avoid run names that case-collide with
   existing scratch/agent/m6/g1_lvl12s7031* dirs (ls -d first; macOS is case-insensitive). E.g. names L12p / L12q.
   Run A: `zsh scratch/s7055/run_hold.zsh L12p 12 10240,12288,10240`; Run B: `... L12q 12 12288,10240,12288` (~11 min each, one at a time).
2. python3 tools/g5e_cost_by_parity.py --phases 3 --skip-s 130 --split xor8 scratch/s7055/tl_<N>.bin.* scratch/agent/m6/g1_lvl12s7031<N>/run.log
   python3 scratch/s7054/cells.py scratch/agent/m6/g1_lvl12s7031<N>/run.log  (positive control: ring_sum/f higher at 12288)
3. Update OWNER-OPT-INS 12288 line; ledger + commit.
Owner-gated items (G5a-G5i, L15 21:9, G1d) still need nothing run; check them first.
