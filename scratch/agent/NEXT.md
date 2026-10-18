# Next work unit: why do flown-mission frames show only sky?
HYPOTHESIS-ID: m6-flown-render-fidelity

s5423: s5421_nor frames 10000/20000 = sky gradient + green craft icon + partial reticle, no terrain/objects. Hangar frame renders fine.
H1 geometry/terrain DLs dropped/clipped; H2 autopilot legitimately flies into empty sky; H3 fb dump partial.
Discriminator: one flown run with a per-frame triangle count (RDP tri cmds) in flight vs hangar, and frame dumps at the mission start (VI phase just after origin 0x00690400) before the autopilot pitches. Tri count ~hangar-level with empty frame => H2/H3; near zero => H1. Use tools/ppm2png.py to view frames. Keep autopilot free of 'r'.
