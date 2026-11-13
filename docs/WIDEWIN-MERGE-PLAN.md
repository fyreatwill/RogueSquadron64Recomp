# WIDEWIN far-terrain 2x2 merge mesh: design (s7239)

Status: BUILT s7240 (tools/apply_s7239_widewin_merge.py + rs64_s7239_* in src/main/upstream_compat.cpp), soak s7240_widewin_merge queued. Was: implement only if the R=48/64/72 bracket (soak s7237_widewin_r2) shows that no
radius meets the s7238 bar (window dsd <= -2.5 ms AND flight |dkpx| <= 1%). HYPOTHESIS-ID widewin-heavy-window-cost.

## Why a merge
s7231-s7238: at 21:9 dd4+WIDEWIN the L4 t=77-97 window costs +4.5 ms per gfx task. That cost tracks RDP triangles
(about 1.2-1.8 ms per 1000). The extra cells are far and tiny: 42% of their triangles have zero height and 58% add only 2% of the pixels.
Every WW-only far cell is already the coarsest retail mesh, one 4-corner quad (s7238). So the only thinning left past
radius R is to draw one quad over each 2x2 block of cells: 4 cells cost 2 triangles where they now cost 8. The radius
cut instead removes the cells and loses their pixels.

## Facts the design rests on (static, funcs_4.c / funcs_9.c, GLideN64 reference/gliden64/F5Rogue.cpp)
1. Emit loop: renderFlatMeshFaceGroup 0x8001108C. Its list is s0 = *(s1+0x20) at 0x800113D8 and s0 = *(s0+0) at 0x800119A4.
   Every element writes ONE 0x28-byte F5 TRI_GEN (op 0x05) command at the DL cursor *(0x8011DC58). The cursor is advanced
   by +0x28 at 0x800119A8/0x800119B0. A material change (elem+0x2C != last) runs 0x8000E104 first, and the segment-overflow
   link (B5) is emitted at 0x80011464 before the command. Both happen BEFORE the command, so dropping a command leaves the stream valid.
2. Flat path (lod 2, 0x80011550-0x80011710), taken when: byte +0x10 == 2, hw +0x16 == 0, (word +0x10 & 0xFFFFFF) == 0x020202,
   byte +0x14 == 2, hw +0x18|+0x1A|+0x1C|+0x1E == 0. Command words (a3 = cursor):
   - w0 = 0x05000000 | byte+0x21 << 16 | (hw+0x2E & 1 ? 0x300 : 0x200)
   - w1 = h0<<20 | (h4<<4 & 0xFFFF), w2 = h20<<20 | (h24<<4 & 0xFFFF); h = s8 bytes 0x0/0x4/0x14/0x18 of *(elem+0x24), the 5x5 height block
   - w3..w6 = RGBA of colour-grid entries 0, 4, 20, 24 (*(elem+0x28) +0x00, +0x10, +0x50, +0x60)
   - w7 = ((s3 & 0xFFFF) - 1) << 5, where s3 = the texture from 0x80022740
   - w8 = hw+0x08 << 16 | hw+0x0A, i.e. x and the y base; w9 = hw+0x0C << 16 | (hw+0x22 << 2), i.e. z and the cell spacing V0
3. Ucode (TriGen02, F5Rogue.cpp:730): the vertices are origin (x, ybase<<4, z) plus {0, V0} in x and z, with heights h<<4 added
   to y. Corner 4 = +x, 20 = +z, 24 = +x+z. So the cell size in emitted units is exactly V0, and the right neighbour sits at x+V0.
4. The list is the distance chain built by buildGridCellMeshForFace 0x8004317C: elem = *(node+0x14)+0x20, node+8 = dist^2 (float),
   and the LOD tier is node+8 against table 0x8009DE94 (0x800431D8-0x80043214). The chain is cut at the far cutoff 0x8009DEB4.
   A post pass (0x80043528-0x80043770) forces lod 1 on the neighbours of lod-2 cells. So a lod-2 flat element whose
   neighbours are lod 2 too lies inside a lod-2 region, with no transition morph across its edges.
5. Group flag *(s1+0x2C) & 0x40000000 (0x80011884) records the command pointer s2 in table 0x8011 63BC (up to 0x40 entries) for a later
   patch. A merge must NOT touch groups with that flag: a dropped command's pointer would be patched into a neighbour.

## Mechanism (opt-in ROGUESQ_DD_WIDEWIN_MERGE=<frac>, unset/0 = off; _TOG=1 same-run split like WIDEWIN_R_TOG)
Fixup tools/apply_s7239_widewin_merge.py (funcs_4.c + funcs_9.c), host code beside rs64_s7233_* in src/main/upstream_compat.cpp:
- H1, buildGridCellMeshForFace per node: rs64_s7239_node(elem, dist2) fills an open-addressed host hash (elem -> dist2). It is cleared
  at the start of every build pass (the s7009 binPolygon latch reset is the existing per-pass hook).
- H2, 0x800113D8 after s0 is loaded, gated by g_rs64_ww (WIDEWIN active this frame) and the group flag being clear:
  rs64_s7239_group(s1, s0) walks the list in RDRAM once. It keys every flat-eligible element (rule 2) by (x, z, V0). An element is an
  ANCHOR when ((x / V0) & 1) == 0, ((z / V0) & 1) == 0, its three partners (x+V0, z), (x, z+V0), (x+V0, z+V0) with the same V0 are
  in the list and flat, and all four have dist2 >= (frac * farcut)^2 (farcut read from 0x8009DEB4, so the knob follows dd). Partners
  are marked DROP. Unpaired cells stay as they are.
- H3, after the w9 store at 0x80011880: for an ANCHOR, rewrite the command in place:
  w1 = h0(A)<<20 | (h4'(B)<<4 & 0xFFFF), w2 = h20'(C)<<20 | (h24'(D)<<4 & 0xFFFF), where h' = h + ybase(partner) - ybase(A) is
  rebased to A's y origin (12-bit range; clamp and count overflows, then skip the merge for that block); w4 = c4(B), w5 = c20(C),
  w6 = c24(D); w9 low = 2*V0 (must fit 16 bits; otherwise skip the merge). Texture coordinates stretch 2x (acceptable at merge range).
- H4, at 0x800119A8: for a DROP element, take the +0x28 back, so the next element overwrites its command.
- Tally [s7239] per phase every 2 s: elements, flat-eligible, anchors, drops, overflow skips, and dist2 hash misses.

## Expected cracks
A merged edge meets single-cell neighbours only where a 2x2 block borders an unmerged cell: a T-junction at the edge
midpoint, with a gap of |h_mid - (h_end1 + h_end2)/2| << 4 units. Haze hides most of it at merge range (DD_MELT). Measure, don't assume:
owner sheet + the s7232 kpx classifier.

## Validation (one build, one soak, same-run tog)
- Arms, L4 owner path at 21:9 dd4+WW+MELT, ROGUESQ_G1CF=1, HOLD 130: MERGE=0.5, MERGE=0.7 (and the winning WIDEWIN_R arm as reference).
- Positive control (iron rule 1): ph1 anchors > 0 and drops == 3*anchors (minus edge cases), ph0 anchors == 0. Expected
  tri change: about -6 tri per anchor, before ucode rejection.
- Bar (s7238): window dsd <= -2.5 ms with flight |dkpx| <= 1% (scorer tools/s7233_widewin_r.py extended for [s7239]).
- Owner sheet: side edge vs docs/owner_sheet_s7009_widewin_219.png, L4 far-left shoreline (s7052), crack close-ups.

## Rejected alternatives
- Coarser per-cell mesh: impossible, the cell is already 2 triangles (s7238).
- Host-side DL rewrite in the DPC bridge: the commands are already in RDRAM when the RSP task starts, so a host pass would have to
  parse the task DL and could only zero-area the dropped commands. The ucode would still process them, so less of the RSP cost is saved.
- Stream-time grid marking (rs64_s7233_cell): the stream works in grid cells (wx, wz) and the emit loop in element (x, z). Their offset
  is unmeasured, while the node dist2 already comes with the element.
