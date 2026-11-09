# NEXT: G1c — are the invisible dd6 cells off-map clamp cells? (on/off-map x depth census + off-map ring cull, L1 and an open level)
HYPOTHESIS-ID: g1c-offmap-cells
Context (s7030): ROGUESQ_DD_FOGCULL showed only 2% of the ~7040 streamed cells/f sit past the fog end (H-fogwaste refuted), but a depth cull at
0.5 x fog end removes 51% of cells, rsp -4.9 ms/frame (-> 60 fps), with no visible change on L1: those cells sit behind the dark textured horizon
"wall" (k=0.3 breaks it into steps with sky gaps; sheet docs/owner_sheet_s7030_fogcull.jpg). s7024: 97-98% of getGridCellValueAt time is the
off-map clampGridCellLookup branch (L_80048554, 4500-6300 calls/frame). G5i/owner items: nothing to run (CURRENT-TRUTH items 1-14); check first.
Hypotheses:
 H-offmap: most dd6 window cells on L1 are off-map (clamp branch); the wall is the clamped map-edge plateau; off-map cells beyond the first R rings
   outside the map edge are invisible (behind the wall face) -> cull them: same cost win as k=0.5, no image change, on every level.
 H-occlude: the culled band is on-map terrain hidden by nearer hills/wall; off-map share is small -> a map-edge cull saves little; the lever is
   an occlusion/horizon test, not map bounds.
 H-open: on an open level (L4) the 0.5-1.0 fe band is visible terrain -> any depth cull pops terrain there; keep FOGCULL off, opt-in only.
Discriminator, ONE build: in rs64_s7030_cell also record whether the cell is off-map (cell x/z = window origin 0x80132DB0/B8 + col/row vs map dims
0x80136DC0+0x38/0x3A, the same test the clamp branch uses) and its ring distance outside the map edge; histogram on/off-map x depth bin per phase.
Add ROGUESQ_DD_OFFMAPCULL=<R> (cull off-map cells more than R rings outside the edge) with tog3 R values e.g. off/2/8, image positive control =
FOGCULL k=0.3 in a separate phase or run. Arms: L1 and L4 (21:9 dd6 WIDEWIN cap 10240, MELT, OWNER_TIMING), copy scratch/s7030/run_H.zsh
(capture 640x274 110 s, then tools/s7030_fogcull_image.py + s7030_fogcull_sheet.py; cost tools/g5e_cost_by_parity.py --phases 3).
Outcome map: off-map share of the 0.5-1.0 fe band >= 70% and OFFMAPCULL saves >= 3 ms with image |d| near the k=1 floor on both levels ->
H-offmap, offer as opt-in (owner decides default). Small off-map share -> H-occlude. L4 image |d| at k=0.5 near the k=0.3 control -> H-open.
