# NEXT: G3 - get a truly page-aligned retail/port RDP frame pair

HYPOTHESIS-ID: g3-render-fidelity

Done s5965: last-stable-frame census differs structurally (retail 1115 tris / port 425, disjoint tri bands, port-only states 0x504240/0x550231/0xf0a4001). Frame pairing unproven.
Competing: H-page (different scene state), H-rdp-imgread, H-dl.
Work unit: pair by content, not position. For the retail rdp.log pick the fullsync whose framebuffer (angrylion r12.png) matches; then locate in BOTH streams the SETTIMG/SETTILE texture address+size sets (texture-image census per frame) and choose the frame pair with the largest overlap. Then diff only the tris that sample shared textures. Positive control: self-diff of two consecutive port frames must be ~0.
Alternative cheap test: in rt64 toggle image_read_en forcing on 0x552038 tris in-run (toggle every N VIs, phase-gated) and see whether white stubs change.
Do not do aim/steer work.
