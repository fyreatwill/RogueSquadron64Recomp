# NEXT (s7552)
HYPOTHESIS-ID: class-gl-writeback-undrawn-column-drift

GK CLOSED s7551 (H-clean, see CURRENT-TRUTH item 19). Side datum: RT64's colour writeback changes bytes OUTSIDE the pair's
drawColorRect columns with no prior RAM change (rtOut): mission L12 dd4 1,062,781 bytes / 9614 writebacks; L1 dd1 and L4 dd4 0.
Hardware leaves undrawn pixels untouched, so these are host-made changes to guest RAM.

Hypotheses:
- H-rect-edge: drawColorRect rounding (left(false)/right(true)) or a draw not merged into drawColorRect (fill/tex rect, a
  scissor-clipped tri) means the "outside" columns were really drawn -> no defect, instrument boundary only.
- H-dither: copyNativeToRAM re-quantises a high-precision native target with a per-writeback random dither seed -> low bits of
  undrawn pixels flicker each writeback (xor pattern confined to the low 1-3 bits of each 5-bit channel).
- H-stale-native: the native target holds content that never matched RAM in those columns (upload skipped / partial upload /
  a different fb aliased at that address), so the writeback paints old or foreign content -> real defect.
Discriminating measurement, ONE build (extend src/main/main.cpp s7551::post, still ROGUESQ_S7551_GK=1): for rtOut bytes record
(a) column histogram relative to rect (distance to rl/rr: 0-1 px = edge), (b) per-16-bit-pixel xor of pre/post (popcount and
whether it touches only channel low bits), (c) whether post equals the value at the same offset in ANY other registered span's
snapshot (foreign content), (d) span phys/width/rect for the top 8 (phys, rect) keys. Positive control: the existing plant.
Run L12 dd4 (the only level with rtOut) + L1 dd1 control arm, HOLD 120, tools/g1e_owner_quiet_arms.zsh
  (E="ROGUESQ_S7551_GK=1+ROGUESQ_S7551_GK_PLANT=1"; ARMS="4:l12:ROGUESQ_FORCE_SAVE_MISSION=12+$E 1:l1:ROGUESQ_FORCE_SAVE_MISSION=1+$E").
Outcomes: edge-only -> H-rect-edge, close GL. Low-bit xor spread across interior undrawn columns -> H-dither (decide whether
the guest ever reads those pixels: s7391 says no CPU reader of live colour images; then close as benign). Foreign/structured
content -> H-stale-native: name the aliasing fb and fix the upload/writeback extent.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
