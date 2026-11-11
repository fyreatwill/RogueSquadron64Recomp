# NEXT: sky top-fade bins, colour-free check: are their polys ever in the RDP stream? (follow-up to s7137, item 29)
HYPOTHESIS-ID: g3-sky-topfade
State (s7137): 0 top-fade-colour tris at dd1 4:3 (D1) and dd4 21:9 (Y1, incl. all 31 burst swaps 7530-7560 where the corner
looks above the band top). H-topdd refuted: the bin objects have the same state at both dd. In the shared render list, sector k's
+0 links to top bin 8+k, which links to sector k+1 (tools/s7137_skyobj.py). Sector tris draw with shade 255 (white), so the HOB
vertex colour A89880 may never reach the RDP shade, and the colour detector may be blind.
Hypotheses:
- H-topretail: the top-bin polys are never emitted (empty/unused DL, per-object cull, or a draw flag). Predicts no stream tris at
  the projected top-bin screen positions on Y1 burst swaps.
- H-topcolour: they ARE emitted but shaded white/modulated. Predicts stream tris whose 3 vertices match the projected top-bin
  vertices (within ~2 px).
Discriminator, OFFLINE, no run: scratch/s7136/Y1.cap (kept, RAM every 20 swaps from 7500, stream every swap). At RAM swaps 7520/7540:
  1. Find the top-bin vertex data. Object 8+k fields +0x34..+0x58 hold pointers into 0x8087xxxx / 0x80C1xxxx (dd4 spill). Read the
     loadSkyHorizonHob store sequence (N64Recomp/RecompiledFuncs/funcs_13.c:5157-6766, objects built around 0x8005AF10-0x8005B114,
     stride 0x5C) to name which field is the vertex array, which is the DL.
  2. Project the vertices with the camera of the same snapshot (matrix at *(0x80138D1C)+0x28 and the projection, as
     tools/s7136_band_elev.py does) and match them against the stream tris of that swap (tools/s7134_band.py vertex list).
  Positive control in the same pass: project SECTOR objects 0-7 the same way. Their tris must match (they draw), or the
  projection is wrong.
Outcomes: sectors match + top bins match -> H-topcolour: the fade IS drawn, so look at what covers it (the SKYFILL corner is
beige because the fade is transparent toward beige: then the stair is the authored look, close). Sectors match + top bins absent
-> H-topretail: find the gate (read the render walker for the object field that differs, e.g. +0x30, or the DL contents) and decide
with the owner whether drawing them is worth it. Sectors don't match -> fix the projection first.
Budget: this is iteration 2 of g3-sky-topfade. If it does not discriminate, close the thread as owner look (beige corner) and move
on to the next CURRENT-TRUTH backlog item.
Owner save rule applies. CURRENT-TRUTH ~58.9 KB: keep edits net-zero.
