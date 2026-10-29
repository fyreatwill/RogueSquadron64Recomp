# NEXT: compare guest depth words to the copyFromChanges stripe
HYPOTHESIS-ID: g1d-levelselect-upload

s6625 selects H-prior-stripe. One Debug binary, both widths. On the 21:9
floor depth texture (1024x339, same pointer) clearDepthTarget reads back
1.0 on x=16 and x=1007, y=180..250 (142/142). The next event is one
full-rect RenderTarget::copyFromChanges (fbChangesDrawDepth, scissor
(0,0)-(1024,339)). Its post image is the stripe: rows 0..11 of that band
are exact 0 on both columns (25 exact zeros in the 26 head cells), then
x=16 is a smooth ramp 0.96408..0.96146 and x=1007 stays 1.0. floor-enter
frame 1357 phase 4 matches that image with max abs diff 0, and matches
shader attachment sample 0. 16:9's 796x339 floor depth has no
copyFromChanges; one copyFromTarget leaves 1.0, floor-enter is all 1.0,
and shader_2 sample 11 stores z 0.99524..0.99667 (95 pixels). Magenta and
pix-match pass. Widths agree, so this is not H-depth-pitch. The clear
read back, so the zeros are not unwritten tiles. Caller is not tagged.
Depth call sites: state.cpp:2604 (clear when readHeight==0, and that path
computes depth row bytes from colorImg.width), workload_queue.cpp:966,
framebuffer_manager.cpp:345. Do not repeat the in-submission witness or
the s6625 event log. Do not change a default or add a cull/skip/restore.

ONE work unit, one binary, both widths. At every depth copyFromChanges
and copyFromTarget whose target width is 796 or 1024, log before the
draw:
- site id (the three call sites above; do not guess from event order)
- fb width, height, readHeight or rowStart, row byte stride, address
- the guest depth bytes for x=16 and x=width-17, y=180..250, 71 rows
Keep the s6625 GPU post-depth sample on that same call so guest and GPU
are one run. Decode guest depth with the scale fbChangesDrawDepth already
uses. Do not invent a second conversion.

Hypotheses and discriminating outcomes:
- H-guest: the decoded guest columns already have the exact-0 head and the
  ~0.96 ramp on x=16 with 1.0 on x=w-17, and they match the GPU post image
  on those rows. copyFromChanges is faithful. 16:9's guest, if uploaded,
  matches its GPU 1.0.
- H-upload: the guest field is a clear or a smooth ramp, and the GPU post
  image is the stripe. Name the site id, the row range, and which shader
  input (pixel texture vs boolean mask vs viewport) differs from the guest
  words. Do not patch the shader in this unit.
- H-witness: the 21:9 clear-then-stripe sequence does not recur, the 16:9
  floor store of z~0.995 is absent, or guest bytes were not logged for the
  call whose GPU image is the stripe. Repair the log in this same
  iteration before interpreting a null.

Positive controls, required: magenta pixel (16,180) still changes; 16:9
floor sample-0 depth stays 1.0 and a later floor op stores z in
0.990..0.998; 21:9 GPU post image of the upload still has >=20 exact zeros
in rows 0..12 and the x=16 ramp against x=w-17 staying near 1. A silent
log is not a result. Phase-gate the route. No cross-run animation compare.
Screen must be unlocked. SIGKILL. One game run at a time. Do not overwrite
scratch/agent/s6624_attachment or scratch/agent/s6625_depth.

Build and run from build/ with the ROM beside it. Keep
tools/g1d_floor_depth.py --selftest and tools/g1d_floor_attachment.py
--selftest green. If lib/ changes, ./submodule-patches/export.sh is part
of the commit.
