# NEXT: G3 - which texture do the white pillar-cap tris sample?

HYPOTHESIS-ID: g3-render-fidelity

s5970: pillar stubs on Available Craft are textured tris (cap DLs 0x3007936f0/937a0/93678/93b70/93c20, L=0x552038). Not untextured shade-only (mode 3 negative; mode 4 rect control turned both pillars green).
Work unit: extend TINT_OM mode 4 to log per-tri the bound texture identity (tmem/SETTIMG addr, fmt/size, width, texel hash of the first 64 bytes from RDRAM) and the cc/combiner and vertex colour for cap tris vs body tris. Hypotheses: H-tex (cap texture mis-loaded/wrong fmt: e.g. 1x1 white or TMEM overwrite), H-cc (combiner yields white regardless of texel), H-design (retail also white, differs only by darkening). Discriminator: force texel sample to flat magenta in cap tris (mode 5, same rect): if still white => cc/shade path; if magenta => texture path, then dump texel bytes. Recipe: copy scratch/agent/s5970_tint4.sh. Compare retail r12.png pillar caps (dark).
Do not do aim/steer work.
