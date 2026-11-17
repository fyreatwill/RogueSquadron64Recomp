# NEXT (s7526)
HYPOTHESIS-ID: rsp-task-v2p

Check `wc -c < docs/CURRENT-TRUTH.md` first (>60000 = MAINTENANCE iteration instead).

1. Fold soak s7525_v2p_levels (SOAK-RESULTS.md; logs scratch/s7525_v2p_levels/, re-score with
   `python3 tools/s7525_v2p_score.py scratch/s7525_v2p_levels l1 l7 l10 l12`). score 0 = V2P H-same on 6 levels.
2. Close the last gap: fixed-frame render equality V2P off vs on (same build). Use a phase-gated fb dump (ROGUESQ_G5B_FRAME_TRIG or
   the s7122 angrylion/RT64 sheet tooling) on L4 dd1 at a VI-gated frame in both arms; expect identical RDP input (s7096 already
   byte-exact) -> identical image within the retail floor. H-diff (any pixel class difference) would mean a hidden consumer of the
   KSEG0 task fields (e.g. bridge address masking in dpc_bridge.cpp) - grep `0x1FFFFFFF\|0xFFFFFF` uses on DPC_START/END first.
3. If both pass: add V2P to docs/OWNER-OPT-INS.md as a proposed default-on (retail fidelity, no visible change) and ask the owner;
   do NOT flip the default without the owner's say. Then return to the 3c ladder / next class audit.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
