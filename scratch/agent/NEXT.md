# G1d: wide-title residual, H-fillrect
HYPOTHESIS-ID: g1d-widescreen
s6250: bboxR ph4 texrects in garbage regions are 8-22 px glyph-like rects, no >512 span -> H-bg-wrap unsupported (capped sample of 600).
Hypotheses: H-fillrect (FILLRECT/fill-cycle rects paint the ~0.13 lower-band residual), H-tex-clamp (rects with s-span past lrs sample clamped/stale texels).
Discriminator: log fill-cycle rects (cyc=3) and fillrects in ph4 with rect + fill colour, and skip arm 'fill' together with texrect-all and RI_CLEAR in one run; residual (nb_frac.py) dropping to ~0 selects H-fillrect.
Recipe: SKIPPH=4 TAGX=_x env "EXTRA_E=ROGUESQ_WB_CLEAR=1 ROGUESQ_RI_CLEAR=1 " zsh scratch/agent/s6244_run.sh <arm>. Note: run the harness fix.out says allattempts-failed but run.log in scratch/agent/m6/g1_lvl1s6244_*/ is valid for title-phase data.
