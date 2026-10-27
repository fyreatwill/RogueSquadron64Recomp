# NEXT: G3c(c) screen shake while turning - arm table + jerk measurement
HYPOTHESIS-ID: g3c-shake
G3c(b) closed s6454 (angrylion: wedges are retail-faithful). Now owner defect (c): slight whole-view shake while the ship turns.
Hypotheses: H-fps60 (camera follow updated on a different cadence than craft), H-pacing (uneven VI spacing between presented frames), H-aspect (wide-view scale applied alternately), H-retail.
Discriminator: per presented frame log camera yaw/pos + craft yaw from guest RAM + present timestamp during a scripted steady turn; second difference of camera yaw per real second. Arms: retail, FPS60, ASPECT, both. Shake = sign-alternating jerk absent in retail. Find camera/craft yaw addresses from CURRENT-TRUTH/PORTING-STATE grep first; one build, all arms as queued soaks.
