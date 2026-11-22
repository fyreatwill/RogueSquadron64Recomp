# NEXT (s7797)
HYPOTHESIS-ID: g3-frame-diff-unsheeted
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines (any of these outranks the rest).

Unit (CURRENT-TRUTH item 13): post-G6c fidelity on L10 at 16:9 (owner recipe FPS60 dd4) + STANDINS=1. L10 has the most stand-ins
added (s7749: 192/280 lifetime), so it is the strongest remaining test of H-standin. Done so far == angrylion: L1/L12 16:9, L1/L4 21:9 (s7793-s7796).
Screen unlocked (`/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes'` must fail), one game:
  env RDIR=s7797 zsh tools/s7131_arm.zsh 10 L10 "ROGUESQ_STANDINS=1 ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
  (do NOT use tools/s7141_arm.zsh: it hard-codes scratch/s7141)
  zsh tools/s7141_post.zsh scratch/s7797 L10 0,10,370,217 46,322      (16:9 defaults; check how s7158 L10 / s7794 L12 called it first:
                                                                        grep -n 's7141_post\|s7160_fit_post' PORTING-STATE.md | tail)
  zsh tools/s7160_fit_post.zsh scratch/s7797 L10 <refit rect> docs/owner_sheet_s7797_L10_standins_fidelity.png
Liveness: run.log under scratch/agent/m6/g1_lvl10s7131L10/: `[standins] N objects`, 0 CRASH lines.
Baseline pre-G6c s7158 L10 16:9: 745 swaps, meand 4.66/5.12/5.48, frac 0.007/0.011/0.013, 0 >0.05, centre/side 0.003/0.017.
Hypotheses: H-equal (at the s7158 floor, 0 >0.05), H-standin (outlier regions at stand-in positions: check worst swaps by eye on the
sheet; stand-ins exist only in our build, angrylion replays the same RDP stream so stand-ins are IN both -> a gap would mean an RT64
render difference on stand-in geometry), H-regress (all bands up: bisect with ROGUESQ_STANDINS=0 in a second arm).
Same-run controls: CONTROL painted PASS line and shift-2 >0.05 count (must fire).
Delete .cap/.raw/replays after scoring unless outliers need the stream.
If H-equal: the post-G6c fidelity thread closes on four levels; take the next ladder item from CURRENT-TRUTH (item 3c) — e.g. a stand-in
coverage check on a level not yet run with STANDINS=1 holds (s7692 covered L1/L4/L5/L10/L12/L15).
