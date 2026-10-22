# NEXT (s5900): what is r17 ("proj") in the segment-vs-sphere loop, and what is pp?
Context (s5899): same-pr lives keep rotation basis (+0x28..0x48) 30/33; boundaries are pp (arg r6) jumps >6 u. So r17 persists while pp jumps.
Competing: (a) r17 is a ship/emitter, pp = per-weapon muzzle segment origin (several per frame); (b) r17 is the bolt and pp is a different quantity (e.g. previous-pos); (c) r17 is a pool node reused with same basis (unlikely).
Discriminator (one build, one run, extend rs5897_track in tools/apply_s5835_sphere_probe.py): for the first 300 samples log pr, pp, pr+0x4c..0x54, pr+0x00 and +0x60 words, and |pp-obj pos|. pp==obj pos -> (a/b by motion); pp far from obj pos and alternating among few values -> (a). Positive control: log must show >=300 rows with nonzero pr.
Recipe: scratch/agent/s5897_life.sh (sed -i needs '' on macOS).
HYPOTHESIS-ID: g1-mission-progression
