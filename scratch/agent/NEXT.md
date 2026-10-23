# NEXT: G3 - texel-content pairing of port-only white-stub tris

HYPOTHESIS-ID: g3-render-fidelity

s5967: image_read_en is inert in rt64 (IM_RD unused) -> not the cause of port-only white pillar stubs.
Work unit: hash the texel payload (LOADBLOCK/LOADTILE source bytes + tile fmt/size/dims) bound to each triangle in the s5964 retail RDP dump and in a port capture of the same Available Craft page (ROGUESQ_LOG_TRITEX exists in rt64_gbi_rdp.cpp:1151). Pair by content hash; list port-only tris (the ~40 with states 0x504240/0x550231/0xf0a4001) and their texture hash/dims/colour-combiner. Outcomes: stubs use a texture/cc absent in retail => H-dl (wrong DL/texture state upstream); same textures present in retail but not drawn at those screen positions => geometry/transform difference. Positive control: self-pairing port-vs-port must give 1.0.
Do not do aim/steer work.
