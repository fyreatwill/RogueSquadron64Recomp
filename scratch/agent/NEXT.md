# NEXT: G1c - fold fog arms, then far-plane
HYPOTHESIS-ID: g1c-draw-distance
Fold s6029_g1c_fogmag vs s6029_g1c_fogret from SOAK-RESULTS.md (tri/task bins as in s6028, plus framebuffer capture if the recipe produced one: count magenta pixels in fogmag; control = retail has none). Magenta present => L-fade is live, find where fog start/end are set (RDP setFogRange / game fog params) and scale them. No magenta => fog not the limiter; go H-farplane: grep for far-clip constant near buildVisibleTerrainGridAroundCamera and the projection setup, then H-budget.
