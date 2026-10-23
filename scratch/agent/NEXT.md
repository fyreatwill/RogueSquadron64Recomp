# NEXT: G3 - root-cause the white pillar stubs with a matched retail/port frame pair

HYPOTHESIS-ID: g3-render-fidelity

Retail pixel oracle now exists (docs/G3-RETAIL-PIXEL-ORACLE.md). Port shows white vertical stubs at hangar pillar edges; retail does not (s5963, single-source, different overlay page).
Competing causes: H-tex (texture format/CI-palette on pillar-edge tris), H-rdp (combiner/blender/coverage state in rt64 vs angrylion), H-dl (ucode decode gives different vertex colours).
Work unit: (1) capture retail hangar at the SAME page as a port capture (two fb dumps at differing --fb-dump delays; pick the "Available Craft" page, press count may differ), (2) crop the pillar region on both at same scale, (3) use rdplog (tools/oracle/rdplog) retail RDP stream vs port RDP dump for the triangles touching the stub pixels to pick H-tex/H-rdp/H-dl. Positive control: whole-frame diff must flag the known overlay page difference.
Do not do aim/steer work.
