# NEXT: G3 - identify the DL/texture behind port-only white stub tris (port-side only)

HYPOTHESIS-ID: g3-render-fidelity

s5968: RDP command streams cannot be paired retail<->port by texture (descriptor overlap 0.05; producers differ, no texel bytes in dumps). Stop pairing offline.
Work unit: in rt64 (rt64_gbi_rdp.cpp), under an env flag, tint triangles whose othermode-lo is 0x504240/0x550231/0xf0a4001 (port-only states) a flat colour and log per-draw: DL address (curData), texture addr/fmt/size, cc. Same Available Craft page as s5964. Hypotheses: H-dl (wrong texture/DL state upstream) vs H-geom (transform). Positive control: tint ALL tris must colour the whole frame. Outcome: the stub tris' source DL address, then trace in the ucode DL builder.
Do not do aim/steer work.
