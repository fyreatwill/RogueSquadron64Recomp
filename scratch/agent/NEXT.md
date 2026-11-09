# NEXT: far-terrain slab edge at 21:9 dd4 (G3c(a) / G5e residual)
HYPOTHESIS-ID: dd-far-edge-219
Context: s7006 crops (scratch/s7006/c1.png, c2.png) at 21:9 dd4 L4, owner recipe with DD_FOG on by default, show the far terrain as a flat haze-coloured
slab with a hard straight edge against the sky. G5e (s6904) measured seam alpha at 16:9 only. The owner asked for distant terrain to melt into the haze.
Hypotheses:
- H-retail: dd1 shows the same hard horizon slab (retail look). Then it is not ours, and an opt-in fade is the only lever.
- H-colour: the dd4 ramp runs to full fog, but the fog colour differs from the sky gradient behind it, so a fully fogged slab still has a silhouette.
  Fix: fade alpha to 0 (or blend toward the sky) over the outer ring, not toward the fog colour.
- H-ramp: the s6904 ramp ends before the window edge at 21:9 (wider frustum exposes side cells past the ramp end), so the edge cells draw un-faded.
  Fix: scale the ramp end with the aspect width as well as dd.
Discriminator (one build, same run): add ROGUESQ_DD_FOG=tog to src/main/upstream_compat.cpp (alternate on/off per 24 MHz second, like W_CLAMP=tog), and log
per frame the fog colour and the cutoff/ramp distances once. Run `env CULL=1 ASP=21:9 CW=1260 CH=540 zsh scratch/s7006/arm.zsh 4 4 f1 "ROGUESQ_DD_FOG=tog" 120 60`,
plus a dd1 arm (`... 4 1 r1 "" 120 60`) for H-retail. Score: for frames at VI phase 0.2-0.9, find the terrain/sky silhouette per column in the top half and
take the colour step across it (sky pixel 3 px above vs terrain 3 px below), median per arm; also sample the slab colour vs the fog colour from the log.
Outcomes: dd1 step similar to dd4 -> H-retail; slab colour == fog colour and step large -> H-colour; edge cells at screen sides un-fogged (step larger at
the left/right thirds than the centre) -> H-ramp. Then fix and give the owner a before/after sheet at 21:9 and 16:9. Delete raws (disk 22 GB free).
