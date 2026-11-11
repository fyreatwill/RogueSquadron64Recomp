# NEXT: residual non-pierce near-wall losses (the class NEARLIFT does not touch), offline on s7115 runs d-g
HYPOTHESIS-ID: fps60-wall-frame
Context: s7116 confirmed NEARLIFT (pooled 83/31). On-second losses pierce the near pyramid 0/27 (e-g); ~30% of off losses also do not pierce. Data on disk:
scratch/s7115/{tris,push,losscan,neargap}_{d,e,f,g}.bin/txt (g.raw kept for frames).
Hypotheses for the non-pierce losses: H-join (loss swap joined to the wrong camera tick: re-test pierce at tick -1/+1/+2; FPS60 render-only frames use an
interpolated camera that may be inside while both sim ticks are outside), H-proj (the render near plane/projection used for that swap differs from f20/half-tans
s7108 assume: read the swap's actual projection from the G5B stream), H-other (not a near-plane loss at all: losscan rule false positive; check presented frames in
g.raw with tools/s7107_sheet.py).
Discriminator, one offline pass: for every non-pierce loss in d-g, pierce at tick offsets -2..+2 and with the interpolated (render) eye; plus a sheet of g's
non-pierce on-second losses. H-join: pierce appears at an offset/interp eye; H-proj: none pierce but near-z of dropped tris < f20 frustum; H-other: frames show no cut.
If H-join: extend the lift to the render-only interpolated eye (apply_s7115_nearlift.py). Also queue/ask: owner judges ROGUESQ_S7115_NEARLIFT=1 for hops.
