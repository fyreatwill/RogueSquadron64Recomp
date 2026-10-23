# NEXT: lvl1 ground darkness - per-tri colour-combiner dump
HYPOTHESIS-ID: g3-lvl1-mesh-ground
H1 legit dark field; H2' ground tris get dark shade/prim/env (vertex colour or lighting) while texture is fine; H3' wrong TLUT/palette. (Format-garble H2 weakened s5988: zoom shows structured tiling.)
Discriminator: one lvl1 run, dump for the ground-frame tris AND the hill-frame control (grass bright): tex addr/fmt/siz, TLUT hash, combiner, prim/env colour, mean vertex shade. Dark shade with bright-frame same tex => H2'; palette differs => H3'; same everything => H1 (then move on to G1 (c)/(d)).
Else continue G4/G1 coverage.
