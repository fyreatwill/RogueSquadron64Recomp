# NEXT (s7303): G5e far band - fog END sweep at dd8 16:9 (owner request: extended terrain melts into haze)
HYPOTHESIS-ID: g5e-far-fog
State (s7302): the dark band is the off-map plateau; it takes fog (FOG_ALT 0.3,0.8 control hazes everything); ks 3->1 alone is small.
Fog alpha is linear in z~1/d so the ramp END (ke, default 0.8dd = 6.4 at dd8) decides how hazy the 20-100 cell band reads.
Unit: tools/s7302_fog_alt_arms.zsh with spec list changed to arms (all dd8 16:9, MELT WIDEWIN):
  l1k2: L1 FOG_ALT=1,2   l1k3: L1 FOG_ALT=1,3   l1k45: L1 FOG_ALT=1,4.5   l4k3: L4 FOG_ALT=1,3
  (sheet already passes xor8 now - verify labels on one pair before trusting.)
Hypotheses / outcomes (s7247 far+side TEX flip + eyeball):
  - H-k3-sweet: ke=3 melts the plateau band by eye but keeps near/mid land (near flip < ~10%) -> make ke=3 (or min) the dd>=6 default
    candidate, owner sheet dd1 | default | ke3 on L1/L4/L5.
  - H-monotone-loss: every ke that melts the band also hazes visible land close in (near flip ~ l1c) -> the band needs a distance-shaped
    fade (e.g. apply only to off-map cells, or MELT stronger at far z) instead of a shorter ramp.
  - H-perf: shorter ke also shrinks g_rs64_s7030_fe (OFFMAPCULL K*fe) -> check [s7233] total_emit / frame ms per phase, likely a gain.
Before run: check CGSSessionScreenIsLocked + HID idle (keys drive the window); ~25 min for 4 arms; raws ~14 GB each are deleted by the script.
