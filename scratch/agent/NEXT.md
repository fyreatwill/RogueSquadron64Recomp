# NEXT (s7749)
HYPOTHESIS-ID: g6c-l12-never-added
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner report, then new SOAK-RESULTS lines.
s7748 closed L12 visibility: the stand-ins are visible (4.1x ground flicker vs a quiet control, pylons by eye). H-drop, H-clip and H-size are refuted.
Unit: on L12, 85 of 92 stand-in items are never added (s7690_par_tally). [standins-s] skip reasons per second: unlinked ~1200, cond 210, spawned 390.
Hypotheses:
- H-zone: the game links an item (type-3 entry in the list scanned at rs64_standins.cpp s_linked) only for its current zone/trigger
  region, so unlinked items are far-zone by design. Adding them would need a different gate.
- H-cond: kConditionMet rejects items whose mission-script condition is not yet true (by design).
- H-ours: the s_linked scan misses entries (wrong list head or type on L12, or list rebuilt mid-frame).
Discriminator (offline first, using scratch/s7748_soak/log_u124.txt and the existing [s7672-ho]/[standins-spawn] lines): per item,
the final reason + distance to the player at end. If unlinked items are all far (beyond dd4 radius) -> H-zone. If they are near and
the real game spawns them later -> H-ours (check the list walk). Only build if the log cannot split them; then one per-item reason
histogram line plus the item's distance, same L12 a600 recipe (scratch/s7748_standins_px.sh).
