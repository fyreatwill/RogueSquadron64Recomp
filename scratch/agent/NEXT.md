# NEXT: G3 - content-keyed pairing or in-run image_read_en toggle

HYPOTHESIS-ID: g3-render-fidelity

s5966: SETTIMG address pairing impossible (0.00 overlap; heap layout differs; port self-control 1.0).
Work unit (cheapest discriminator first): in rt64, force image_read_en off on tris with othermode-lo 0x552038 (phase-gated on VI, toggle within one run every N VIs, positive control = force ALL tris off must visibly change frame) and see whether the white pillar stubs vanish. Stubs vanish => H-rdp-imgread; unchanged => H-dl / content difference, then hash texels (TMEM loads) for content pairing.
Do not do aim/steer work.
