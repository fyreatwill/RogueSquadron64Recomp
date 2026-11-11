# NEXT: G3 hangar text-box residual + level select/briefing at 21:9 (CURRENT-TRUTH item 32)
HYPOTHESIS-ID: g3-fidelity-hangar-219
State (s7142): RT64 rect-aspect fixed (ROGUESQ_RECT_ASPECT default on). Hangar steady centre frac>40 0.05 (edges), text boxes 0.21 vs flight
HUD boxes ~0.09-0.12. Data kept: scratch/s7142/{H2,H3,G2,G3}.raw + *r replays + csvs (no re-run needed for step 1).
Step 1 (offline, no run): text-box registration sweep: crop the title box (21:9 compare coords 165:8:305:38) from H2 raw and angrylion rgb, sweep
dx/dy -2..2 and a 0.5 px subpixel shift + 3x3 blur of the angrylion side. Hypotheses:
- H-filter: a blur of angrylion (bilinear-like) drops the box score to the side floor -> filtering only, close.
- H-misalign: a nonzero dx (horizontalMisalignment still applied to non-full rects) drops it -> zero p.horizontalMisalignment under the fix too.
- H-tex: neither helps -> diff the glyph texels (TLUT/format) on one swap.
Step 2: level select + mission briefing at 21:9: tools/s7142_arm.zsh with AP extended past 64:a (70:start,76:start) and FROM at the briefing
(H1 swaps 3820+ scored 0.006 centre = briefing? check the g5g/time map first). Positive control: painted-square PASS + --shift 10 on slow menus.
Side lead: 4:3 hangar VI fbSize (is retail 512x336?) to test the 21:9 whole-picture 0.86 squash claim in s7142's entry.
CURRENT-TRUTH ~59.4 KB: keep edits net-zero.
